from flask import Blueprint, request, jsonify, session
from models import db, User, Couple, Mission, CoupleMission, CoupleChallenges, Scenario, Challenges, CoupleScenario, StoryProgress, bcrypt
import re  
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests
import os

"""


we'll need a user, a couple ,a notebook, a missions, a spicy, blueprint

after that, we can create routes such as
s

login

register

....



"""


# ADDED THIS TO THE IMPORT FROM MODELS: User, Couple, bcrypt

api = Blueprint('api', __name__)
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')


@api.route('/auth/google/register', methods=['POST'])
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
        return jsonify({'error': str(e)}), 401

    # Check existing user
    if User.query.filter_by(username=email).first():
        return jsonify({'error': 'User already exists'}), 409

    # Extract fields
    invitation_code = data.get('invitation_code', '').strip()
    name = data.get('name', '')
    accepted_terms = data.get('accepted_terms', False)

    if len(name) > 30:
        return jsonify({'error': 'Name too long'}), 400


    
    # Validate common fields
    if not all([name, accepted_terms]):
        return jsonify({'error': 'Missing name or terms acceptance'}), 400
        
    # Handle invitation code case
    if invitation_code:
        couple = Couple.query.filter_by(invitation_code=invitation_code).first()
        if not couple:
            return jsonify({'error': 'Invalid invitation code'}), 404
            
        if len(couple.users) >= 2:
            return jsonify({'error': 'Couple is full'}), 400
        
        couple_id = couple.id
        couple_name = couple.couple_name  # Get from existing couple
        
    # Handle new couple case
    else:
        couple_name = data.get('couple_name', '')
        if not couple_name:
            return jsonify({'error': 'Couple name required for new couples'}), 400
            
        if len(couple_name) > 30:
            return jsonify({'error': 'Couple name too long'}), 400
            
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
def delete_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        couple = Couple.query.get(user.couple_id)
        
        # Delete user
        db.session.delete(user)
        
        # Check if couple has no remaining users
        remaining_users = User.query.filter_by(couple_id=couple.id).count()
        if remaining_users == 0:
            # Delete couple and related data
            db.session.delete(couple)
            
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@api.route('/couple', methods=['GET'])
@jwt_required()
def get_couple_details():
    try:
  
        user_id = get_jwt_identity()
        print(f"🔑 User ID from JWT: {user_id} ({type(user_id)})")
        
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        print(f"👫 User couple ID: {user.couple_id}")
        couple = Couple.query.get(user.couple_id)
        if not couple:
            print(f"❌ Couple not found for user {user_id}")
            return jsonify({'error': 'Couple not found'}), 404
        
        print(f"✅ Successfully retrieved couple: {couple.id}")

        print(couple.couple_name, couple.level, couple.points, couple.invitation_code)
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
def get_missions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    # Fetch all missions
    missions = Mission.query.all()

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
def create_mission():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_mission = Mission(
        content=data['content'],
        category=data['category'],
        created_by=user_id,
        is_precreated=False
    )
    db.session.add(new_mission)
    db.session.commit()

    return jsonify({'message': 'Mission created', 'id': new_mission.id}), 201


@api.route('/couples/<int:couple_id>/missions', methods=['POST'])
@jwt_required()
def accept_mission(couple_id):
    data = request.get_json()
    mission_id = data['mission_id']

    # Verify user belongs to the couple
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_entry = CoupleMission(couple_id=couple_id, mission_id=mission_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'Mission accepted'}), 201




# challenges section

@api.route('/challenges', methods=['GET'])
@jwt_required()
def get_challenges():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    couple_id = user.couple_id

    # Fetch all challenges
    challenges = Challenges.query.all()

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
def create_challenges():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_challenges = Challenges(
        content=data['content'],
        category=data['category'],
        created_by=user_id,
        is_precreated=False
    )
    db.session.add(new_challenges)
    db.session.commit()

    return jsonify({'message': 'challenges created', 'id': new_challenges.id}), 201


@api.route('/couples/<int:couple_id>/challenges', methods=['POST'])
@jwt_required()
def accept_challenges(couple_id):
    data = request.get_json()
    challenges_id = data['challenges_id']

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
            'accepted': s.id in accepted_ids  # Add acceptance status
        } for s in scenarios]), 200
        
    except Exception as e:
        print(f"Error fetching scenarios: {str(e)}")
        return jsonify({"error": "Failed to fetch scenarios"}), 500
    

@api.route('/couples/<int:couple_id>/scenarios', methods=['POST'])
@jwt_required()
def accept_scenario(couple_id):
    data = request.get_json()
    scenario_id = data['scenario_id']

    # Verify user belongs to the couple
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.couple_id != couple_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_entry = CoupleScenario(couple_id=couple_id, scenario_id=scenario_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'scenario accepted'}), 201


def create_page_notebook():
    # This function is a placeholder for creating a page in the notebook
    # a notebook model should be a list of pages (page should be another model then i guess)
    # the function should create a page in the notebook, and the page in the notebook should have the following fields:

    
    pass

def get_page_notebook():
    # This function is a placeholder for getting a page in the notebook
    # it should return the page  or maybe a bunch of pages like in a paginated way(?) in the notebook, and the page in the notebook should have the following fields:

    
    pass

def delete_page_notebook():
    # This function is a placeholder for deleting a page in the notebook
    # it should delete the page in the notebook, and the page in the notebook 

    
    pass


"""
def check_upload_limit(user_id):
    from your_app.models import Image
    current_count = Image.query.filter_by(user_id=user_id).count()
    return current_count >= 50

"""


#use when user clicks on start now?
@api.route('/story/start', methods=['POST'])
@jwt_required()
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


#use when the user opens the sheet of the story book view, gets automatically called this function?
@api.route('/story/status', methods=['GET'])
@jwt_required()
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

# this is used when a page (one page then in the frontedn should contain two challenges)?

@api.route('/story/progress', methods=['POST'])
@jwt_required()
def update_progress():
    user = User.query.get(get_jwt_identity())
    couple = user.couple
    data = request.get_json()

    # Validate required fields
    page_number = data.get('page_number')
    if page_number is None:
        return jsonify({'error': 'page_number is required'}), 400

    # Find existing progress or create new
    existing_progress = StoryProgress.query.filter_by(
        couple_id=couple.id,
        page_number=page_number
    ).first()

    if existing_progress:
        # Update existing entry
        existing_progress.fun_level = data.get('fun_level', existing_progress.fun_level)
        existing_progress.comments = data.get('comments', existing_progress.comments)
        existing_progress.completed_at = datetime.now()
    else:
        # Create new entry
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


