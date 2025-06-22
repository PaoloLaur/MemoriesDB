from flask import Blueprint, request, jsonify, current_app
from models import db, User, Couple, Mission, CoupleMission, CoupleChallenges, Scenario, Challenges, CoupleScenario, StoryProgress, bcrypt
import re  
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from functools import wraps
import logging
from flask_limiter import Limiter


api = Blueprint('api', __name__)

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

if not CLIENT_ID:
    raise ValueError("Google Client ID not found")

security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('security.log')
security_handler.setLevel(logging.WARNING)
security_logger.addHandler(security_handler)



def log_security_event(user_id, event_type, details):
    """Log security-related events"""
    security_logger.warning(f"User {user_id}: {event_type} - {details}")

def validate_request_size(max_size_mb=1):
    """Limit request size to prevent DoS"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_length and request.content_length > max_size_mb * 1024 * 1024:
                return jsonify({'error': 'Request too large'}), 413
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_structure():
    """Ensure JSON is properly structured"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:

                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({'error': 'Invalid JSON'}), 400
            except Exception:
                return jsonify({'error': 'Malformed JSON'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_text_input(text, field_name, max_length=500, min_length=1):
    """
    Validate and sanitize text input to prevent injection attacks
    """
    if text is None or not isinstance(text, str):
        return None, f"{field_name} is required and must be text"
    
    # Strip whitespace
    text = text.strip()
    
    # Check length
    if len(text) < min_length:
        return None, f"{field_name} is too short"
    if len(text) > max_length:
        return None, f"{field_name} is too long (max {max_length} characters)"
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript protocol
        r'on\w+\s*=',                # Event handlers
        r'<iframe[^>]*>',            # Iframes
        r'<object[^>]*>',            # Objects
        r'<embed[^>]*>',             # Embeds
        r'eval\s*\(',                # eval() calls
        r'Function\s*\(',            # Function constructor
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return None, f"{field_name} contains potentially unsafe content"
    
    # Additional check for excessive special characters
    special_char_count = len(re.findall(r'[<>{}[\]\\`]', text))
    if special_char_count > len(text) * 0.1:  # More than 10% special chars
        return None, f"{field_name} contains too many special characters"
    
    return text, None

def validate_name(name):
    """Specific validation for names"""
    name, error = validate_text_input(name, "Name", max_length=30, min_length=1)
    if error:
        return None, error
    
    # Names should be mostly letters, spaces, hyphens, apostrophes
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        return None, "Name contains invalid characters"
    
    return name, None

def validate_content(content, content_type="Content"):
    """Validate mission/challenge content"""
    return validate_text_input(content, content_type, max_length=300, min_length=5)

def validate_comments(comments):
    """Validate user comments"""
    if not comments:  # Comments are optional
        return "", None
    return validate_text_input(comments, "Comments", max_length=300, min_length=1)

def validate_id_int(id, field_name):
    """validate the id, when supposed to be a single integer"""
    if id is None or not isinstance(id, int):
        return None, f"{field_name} is required and must be integer"
    if len(str(id)) > 5:
        return None, f"{field_name} is too long"
    
    return id, None

def get_limiter():
    if 'limiter' not in current_app.extensions:
        return None
    limiter_ext = current_app.extensions['limiter']
    
    if isinstance(limiter_ext, dict) and limiter_ext:
        return next(iter(limiter_ext.values()))
    elif isinstance(limiter_ext, set) and limiter_ext:
        return next(iter(limiter_ext))
    return None

def rate_limit(limit_string):
    """Decorator to apply rate limits to routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = get_limiter()
            if limiter:
                # Create a new decorated function with the rate limit applied
                limited_function = limiter.limit(limit_string)(f)
                return limited_function(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ------------------------------------------------
# ------------------------------------------------
# ------------------------------------------------


@api.route('/auth/google/register', methods=['POST'])
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")  # 30 mission acceptances per minute per user
def google_register():
    data = request.get_json()
    id_token_str = data.get('token')
    
    # Verify token first
    try:
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)
        if idinfo['aud'] != CLIENT_ID:
            return jsonify({'error': 'Invalid token'}), 401
        email = idinfo['email']
    except ValueError as e:
        return jsonify({'error': str(e)}), 402

    # Check existing user
    if User.query.filter_by(username=email).first():
        return jsonify({'error': 'User already exists'}), 409

    # Extract fields
    invitation_code = data.get('invitation_code', '').strip()
    if invitation_code:
        if len(invitation_code) > 40 or len(invitation_code) < 10:
            return jsonify({'error': 'Invalid invitation code'}, 408)
        
    name = data.get('name', '')
    name, error = validate_name(name)
    if error:
        return jsonify({'error': error}), 400
    
    accepted_terms = data.get('accepted_terms', False)

    if len(name) > 30:
        return jsonify({'error': 'Name too long'}), 400


    
    # Validate common fields
    if not all([name, accepted_terms]):
        return jsonify({'error': 'Missing name or terms acceptance'}), 403
        
    # Handle invitation code case
    if invitation_code:
        couple = Couple.query.filter_by(invitation_code=invitation_code).first()
        if not couple:
            return jsonify({'error': 'Invalid invitation code'}), 404
            
        if len(couple.users) >= 2:
            return jsonify({'error': 'Couple is full'}), 405
        
        couple_id = couple.id
        couple_name = couple.couple_name  # Get from existing couple
        
    # Handle new couple case
    else:
        couple_name = data.get('couple_name', '')
        if not couple_name:
            return jsonify({'error': 'Couple name required for new couples'}), 406
            
        if len(couple_name) > 30:
            return jsonify({'error': 'Couple name too long'}), 407
        
        validated_couple_name, error = validate_name(couple_name)
        if error:
            return jsonify({'error': f"Couple {error.lower()}"}), 400
        
        couple_name = validated_couple_name
    
            
        new_couple = Couple(couple_name=couple_name)
        db.session.add(new_couple)
        db.session.flush()
        couple_id = new_couple.id

    # Create user
    new_user = User(
        username=email,
        name=name,
        couple_id=couple_id
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Generate tokens
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': new_user.id,
        'couple_id': couple_id,
        'couple_name': couple_name
    }), 201

@api.route('/auth/google/login', methods=['POST'])
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")
def google_login():
    id_token_str = request.get_json().get('token')
    try:
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)
        email = idinfo['email']
    except ValueError:
        return jsonify({'error': 'Invalid token'}), 401

    user = User.query.filter_by(username=email).first()
    if not user:
        return jsonify({'error': 'User not registered'}), 404

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user.id,
        'couple_id': user.couple_id
    }), 200

@api.route('/users/delete', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("5 per minute")
def delete_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        couple = Couple.query.get(user.couple_id)
    
        # Get all user-created content first
        user_missions = Mission.query.filter_by(created_by=user.id).all()
        
        user_challenges = Challenges.query.filter_by(created_by=user.id).all()
        
        user_scenarios = Scenario.query.filter_by(created_by=user.id).all()
        
        # Delete dependent records first
        # 1. Handle Missions
        for mission in user_missions:
            # Delete from couples_missions first
            CoupleMission.query.filter_by(mission_id=mission.id).delete()
            db.session.delete(mission)
        
        # 2. Handle Challenges  
        for challenge in user_challenges:
            # Delete from couple_challenges first
            CoupleChallenges.query.filter_by(challenges_id=challenge.id).delete()
            db.session.delete(challenge)
        
        # 3. Handle Scenarios
        for scenario in user_scenarios:
            # Delete from couples_scenarios first
            CoupleScenario.query.filter_by(scenario_id=scenario.id).delete()
            db.session.delete(scenario)
        
        # Check remaining users BEFORE deleting current user
        remaining_users_count = User.query.filter_by(couple_id=couple.id).filter(User.id != user.id).count()
        
        # Delete the user
        db.session.delete(user)
        
        # If this was the last user in the couple, delete the couple and related data
        if remaining_users_count == 0:
            
            # Delete all couple's accepted content (regardless of who created it)
            CoupleMission.query.filter_by(couple_id=couple.id).delete()
            CoupleChallenges.query.filter_by(couple_id=couple.id).delete() 
            CoupleScenario.query.filter_by(couple_id=couple.id).delete()
            
            # Delete story progress
            StoryProgress.query.filter_by(couple_id=couple.id).delete()
            
            # Finally delete the couple
            db.session.delete(couple)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@api.route('/couple', methods=['GET'])
@jwt_required()
@rate_limit("15 per minute")
def get_couple_details():
    try:
  
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        couple = Couple.query.get(user.couple_id)
        if not couple:
            return jsonify({'error': 'Couple not found'}), 404
        

        return jsonify({
            'couple_name': couple.couple_name,
            'level': couple.level,
            'points': couple.points,
            'invitation_code': couple.invitation_code,
            'users': [user.name for user in couple.users]
        }), 200

    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500



@api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # This validates the refresh token
@validate_request_size(max_size_mb=3)
#@validate_json_structure()
@rate_limit("30 per minute")
def refresh():
    try:
        current_user = get_jwt_identity()
        return jsonify({
            'access_token': create_access_token(identity=current_user)
        }), 200
    except Exception as e:
        # Specific error for expired refresh token
        return jsonify({"error": "Refresh token expired"}), 401


    
# missions section

@api.route('/missions', methods=['GET'])
@jwt_required()
@rate_limit("15 per minute")
def get_missions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    missions = Mission.query.filter((Mission.is_precreated == True) | (Mission.created_by == couple_id)).all()

    # Check acceptance
    accepted_mission_ids = {cm.mission_id for cm in CoupleMission.query.filter_by(couple_id=couple_id)}

    result = []
    for mission in missions:
        result.append({
            'id': mission.id,
            'content': mission.content,
            'category': mission.category,
            'is_precreated': mission.is_precreated,
            'created_by': mission.created_by,
            'accepted': mission.id in accepted_mission_ids
        })
    
    return jsonify(result), 200


@api.route('/missions', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("10 per hour")
def create_mission():
    data = request.get_json()

    content = data.get('content', '')
    validated_content, error = validate_content(content, "Mission content")
    if error:
        return jsonify({'error': error}), 400
    
    category = data.get('category', '')
    validated_category, error = validate_text_input(category, "Category", max_length=150, min_length=1)
    if error:
        return jsonify({'error': error}), 400
    

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    # Query the database to count missions created by this couple
    existing_mission_count = Mission.query.filter_by(created_by=couple_id).count()


    # Check if the count is more than 5
    if existing_mission_count > 5:
        return jsonify({'error': 'Forbidden - Maximum number of missions created (5) exceeded'}), 403

    # Proceed to create the new mission
    new_mission = Mission(
        content=validated_content,
        category=validated_category,
        created_by=couple_id,
        is_precreated=False
    )

    db.session.add(new_mission)
    db.session.commit()

    return jsonify({
        'id': new_mission.id,
        'content': new_mission.content,
        'category': new_mission.category,
        'is_precreated': False,
        'accepted': False,
        'created_by': new_mission.created_by  
    }), 201


@api.route('/couples/<int:couple_id>/missions', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")
def accept_mission(couple_id):
    data = request.get_json()

    mission_id = data['mission_id']

    mission_id, error = validate_id_int(mission_id, "mission id")
    if error:
        return jsonify({'error': error}), 400


    # Verify user belongs to the couple
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_entry = CoupleMission(couple_id=couple_id, mission_id=mission_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'Mission accepted'}), 201


@api.route('/missions/<int:mission_id>', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("20 per minute")
def delete_mission(mission_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    mission = Mission.query.get(mission_id)
    if not mission:
        return jsonify({'error': 'Challenge not found'}), 404
        
    # Only allow deletion of user-created challenges
    if mission.created_by != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(mission)
    db.session.commit()
    return jsonify({'message': 'Challenge deleted'}), 200


# Unlike a mission
@api.route('/couples/<int:couple_id>/missions/<int:mission_id>', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("30 per minute")
def unlike_mission(couple_id, mission_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    entry = CoupleMission.query.filter_by(
        couple_id=couple_id, 
        mission_id=mission_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Challenge unliked'}), 200

# challenges section

@api.route('/challenges', methods=['GET'])
@jwt_required()
@rate_limit("10 per minute")
def get_challenges():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    # Fetch all challenges
    challenges = Challenges.query.filter((Challenges.is_precreated == True) | (Challenges.created_by == couple_id)).all()

    # Check acceptance
    accepted_challenges_ids = {cm.challenges_id for cm in CoupleChallenges.query.filter_by(couple_id=couple_id)}

    result = []
    for challenges in challenges:
        result.append({
            'id': challenges.id,
            'content': challenges.content,
            'category': challenges.category,
            'is_precreated': challenges.is_precreated,
            'created_by': challenges.created_by,
            'accepted': challenges.id in accepted_challenges_ids
        })
    
    return jsonify(result), 200


@api.route('/challenges', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("10 per hour")
def create_challenges():
    data = request.get_json()

    content = data.get('content', '')
    validated_content, error = validate_content(content, "Mission content")
    if error:
        return jsonify({'error': error}), 400
    
    category = data.get('category', '')
    validated_category, error = validate_text_input(category, "Category", max_length=150, min_length=1)
    if error:
        return jsonify({'error': error}), 400
    

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    # Query the database to count missions created by this couple
    existing_challenges_count = Challenges.query.filter_by(created_by=couple_id).count()


    # Check if the count is more than 5
    if existing_challenges_count > 5:
        return jsonify({'error': 'Forbidden - Maximum number of challenges created (5) exceeded'}), 403

    new_challenges = Challenges(
        content=validated_content,
        category=validated_category,
        created_by=couple_id,
        is_precreated=False
    )
    db.session.add(new_challenges)
    db.session.commit()

    return jsonify({
        'id': new_challenges.id,
        'content': new_challenges.content,
        'category': new_challenges.category,
        'is_precreated': False,
        'accepted': False,
        'created_by': new_challenges.created_by  
    }), 201

@api.route('/couples/<int:couple_id>/challenges', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")
def accept_challenges(couple_id):
    data = request.get_json()
    challenges_id = data['challenges_id']

    challenges_id, error = validate_id_int(challenges_id, "mission id")
    if error:
        return jsonify({'error': error}), 400


    # Verify user belongs to the couple
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_entry = CoupleChallenges(couple_id=couple_id, challenges_id=challenges_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'challenges accepted'}), 201


@api.route('/scenarios', methods=['GET'])
@jwt_required()
@rate_limit("30 per minute")
def get_scenarios():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        couple_id = user.couple_id

        # Get all scenarios
        scenarios = Scenario.query.all()
        
        # Get accepted scenario IDs for this couple
        accepted_ids = {cs.scenario_id for cs in CoupleScenario.query.filter_by(couple_id=couple_id)}

        return jsonify([{
            'id': s.id,
            'setting': s.setting,
            'roles': s.roles,
            'prompt': s.prompt,
            'time': s.time,
            'is_precreated': s.is_precreated,
            'accepted': s.id in accepted_ids  
        } for s in scenarios]), 200
        
    except Exception as e:
        print(f"Error fetching scenarios: {str(e)}")
        return jsonify({"error": "Failed to fetch scenarios"}), 500
    

@api.route('/couples/<int:couple_id>/scenarios', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")
def accept_scenario(couple_id):
    data = request.get_json()
    scenario_id = data['scenario_id']


    scenario_id, error = validate_id_int(scenario_id, "mission id")
    if error:
        return jsonify({'error': error}), 400

    # Verify user belongs to the couple
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_entry = CoupleScenario(couple_id=couple_id, scenario_id=scenario_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'scenario accepted'}), 201


@api.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("20 per minute")
def delete_challenge(challenge_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    challenge = Challenges.query.get(challenge_id)
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
        
    # Only allow deletion of user-created challenges
    if challenge.created_by != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(challenge)
    db.session.commit()
    return jsonify({'message': 'Challenge deleted'}), 200


@api.route('/couples/<int:couple_id>/challenges/<int:challenge_id>', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("30 per minute")
def unlike_challenge(couple_id, challenge_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    entry = CoupleChallenges.query.filter_by(
        couple_id=couple_id, 
        challenges_id=challenge_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Challenge unliked'}), 200


@api.route('/couples/<int:couple_id>/scenarios/<int:scenario_id>', methods=['DELETE'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("30 per minute")
def unlike_scenario(couple_id, scenario_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    entry = CoupleScenario.query.filter_by(
        couple_id=couple_id, 
        scenario_id=scenario_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Scenario unliked'}), 200


# notebook routes

@api.route('/story/start', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@rate_limit("30 per minute")
def start_story():
    user = User.query.get(get_jwt_identity())
    couple = user.couple
    
    if couple.story_started_at:
        return jsonify({'error': 'Story already started'}), 400
        
    couple.story_started_at = datetime.now()
    couple.story_current_page = 0
    db.session.commit()
    
    return jsonify({
        'started_at': couple.story_started_at.isoformat(),
        'current_page': couple.story_current_page,
        'completed_pages': []  # Add empty array

    }), 200


@api.route('/story/status', methods=['GET'])
@jwt_required()
@rate_limit("30 per minute")
def get_story_status():
    user = User.query.get(get_jwt_identity())
    couple = user.couple
    
    completed_pages = [{
        'page_number': p.page_number,
        'completed_at': p.completed_at.isoformat(),
        'fun_level': p.fun_level,
        'comments': p.comments
    } for p in couple.completed_pages]
    
    return jsonify({
        'current_page': couple.story_current_page,
        'started_at': couple.story_started_at.isoformat() if couple.story_started_at else None,
        'completed_pages': completed_pages
    }), 200


@api.route('/story/progress', methods=['POST'])
@jwt_required()
@validate_request_size(max_size_mb=3)
@validate_json_structure()
@rate_limit("30 per minute")
def update_progress():
    user = User.query.get(get_jwt_identity())
    couple = user.couple
    data = request.get_json()

    # Validate required fields

    page_number = data.get('page_number')
    page_number, error = validate_id_int(page_number, "page number")
    if error:
        return jsonify({'error' : error}), 400

    # Find existing progress or create new
    existing_progress = StoryProgress.query.filter_by(
        couple_id=couple.id,
        page_number=page_number
    ).first()

    if existing_progress:
        # Update existing entry
        fun_level = data.get('fun_level', existing_progress.fun_level)
        fun_level, error = validate_id_int(fun_level, "fun level")
        if error:
            return jsonify({'error' : error}), 400
        
        comments =  data.get('comments', existing_progress.comments)
        comments, error = validate_comments(comments)
        if error:
            return jsonify({'error' : error}), 400        
        
        existing_progress.fun_level = fun_level
        existing_progress.comments = comments
        existing_progress.completed_at = datetime.now()
    else:
        # Create new entry
        fun_level = data.get('fun_level')
        fun_level, error = validate_id_int(fun_level, "fun level")
        if error:
            return jsonify({'error' : error}), 400
        
        comments =  data.get('comments')
        comments, error = validate_comments(comments)
        if error:
            return jsonify({'error' : error}), 400      
        
        new_progress = StoryProgress(
            couple_id=couple.id,
            page_number=page_number,
            completed_at=datetime.now(),
            fun_level=data.get('fun_level'),
            comments=data.get('comments')
        )
        db.session.add(new_progress)

    db.session.commit()

    return jsonify({
        'completed_at': existing_progress.completed_at.isoformat() if existing_progress 
                        else new_progress.completed_at.isoformat()
    }), 200





  

