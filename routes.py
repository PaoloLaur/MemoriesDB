from flask import Blueprint, request, jsonify, session
from models import db, User, Couple, Mission, CoupleMission
import re  
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity



"""


we'll need a user, a couple ,a notebook, a missions, a spicy, blueprint

after that, we can create routes such as


login

register

....



"""


# ADDED THIS TO THE IMPORT FROM MODELS: User, Couple, bcrypt

api = Blueprint('api', __name__)

# what does this decorator do??
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json() # how does the get_json function work at low level?
    print(data)

    if len(data.get('username')) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if len(data.get('password')) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if not re.match("^[a-zA-Z0-9_]*$", data.get('username')):
        return jsonify({'error': 'Username can only contain letters, numbers and underscores'}), 400
    if not data.get('name') or len(data.get('name', '').strip()) == 0:
        return jsonify({'error': 'Name is required'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    invitation_code = data.get('invitation_code', '').strip()

    
    if User.query.filter_by(username=username).first(): #why the 'first'?
        return jsonify({'error': 'Username already exists'}), 409
    
    if not invitation_code and not data.get('couple_name'):
        return jsonify({'error': 'Couple name is required'}), 400
    

    
 # CASE 1: Joining existing couple
    if invitation_code:
        couple = Couple.query.filter_by(invitation_code=invitation_code).first()
        
        if not couple:
            return jsonify({'error': 'Invalid code'}), 404
        
        # which one is best??
        
        user_count = User.query.filter_by(couple_id=couple.id).count()
        if user_count >= 2:
            return jsonify({'error': 'Couple is full'}), 400
            
        if len(couple.users) >= 2:
            return jsonify({'error': 'Couple full'}), 400

        new_user = User(
            username=username,
            password=password,
            name=name,  
            couple_id=couple.id
        )
        
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=str(new_user.id))  # Convert to string
        refresh_token = create_refresh_token(identity=str(new_user.id))
            
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Joined couple',
            'user_id': new_user.id,
            'couple_id': couple.id
        }), 201

    # CASE 2: Creating new couple
    else:
        # FIX HERE: Create and commit couple first
        new_couple = Couple(couple_name=data.get('couple_name'))
        db.session.add(new_couple)
        db.session.flush()  # Generate ID without full commit
        
        new_user = User(
            username=username,
            password=password,
            name=name, 
            couple_id=new_couple.id  # Now has valid ID
        )
        
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id 

        access_token = create_access_token(identity=str(new_user.id))  # Convert to string
        refresh_token = create_refresh_token(identity=str(new_user.id))
            
    

    
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Couple created',
            'user_id': new_user.id,
            'couple_id': new_couple.id,
            'invitation_code': new_couple.invitation_code  # Send this to user
        }), 201

# Ensure consistent error responses
@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not user.check_password(data.get('password')):
            return jsonify({'error': 'Incorrect password'}), 401
        
        session['user_id'] = user.id 
        session.permanent = True

        access_token = create_access_token(identity=str(user.id))  # Convert to string
        refresh_token = create_refresh_token(identity=str(user.id))
            
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.id,
            'couple_id': user.couple_id
        }), 200
   

        
    except Exception as e:
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

@api.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.get_json()
    user_id = get_jwt_identity()  # Get user ID from JWT

    print(user_id)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.check_password(data.get('current_password')):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    if len(data.get('new_password')) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    user.password = data.get('new_password')
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'}), 200

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