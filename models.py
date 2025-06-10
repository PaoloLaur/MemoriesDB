from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import uuid
from sqlalchemy import Index

db = SQLAlchemy()
bcrypt = Bcrypt()



class User(db.Model):
    __tablename__ = 'users' # what is this?? what properties does __tablename__ have?


    __table_args__ = (
        db.CheckConstraint('couple_id IS NOT NULL', name='user_must_belong_to_couple'),
        Index('idx_user_couple_id', 'couple_id')
    )
   



    #not nullable keys

    id = db.Column(db.Integer, primary_key=True) # why primary key? this is built in such a way that every id is unique, but how?
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)    
    name = db.Column(db.String(30), nullable=False)    
    password_hash = db.Column(db.String(120), nullable=True)

    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False) # what is ForeignKey?
    created_at = db.Column(db.DateTime, default=datetime.now) # is this necessary? does it have a problem??

    points = db.Column(db.Integer, default=0, nullable=False)
    couple_name = db.Column(db.String(30))  # For couple creator

    #nullable keys

    couple = db.relationship('Couple', back_populates='users') # IMP. : what is this db.relationship('Couple', back_populates='users')???

    @property
    def password(self):
        raise AttributeError('password is write-only')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    

class Couple(db.Model):
    __tablename__ = 'couples'


    id = db.Column(db.Integer, primary_key=True)
    invitation_code = db.Column(db.String(36), unique=True, nullable=False, index = True)  # invitation code of the first user
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)

    couple_name = db.Column(db.String(30), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)

    users = db.relationship('User', back_populates='couple')

    story_started_at = db.Column(db.DateTime)
    story_current_page = db.Column(db.Integer, default=0)
    completed_pages = db.relationship('StoryProgress', backref='couple', lazy=True)

    def __init__(self, couple_name):
        self.invitation_code = str(uuid.uuid4())  # Generate unique code
        self.couple_name = couple_name
    
    
class StoryProgress(db.Model):

    __table_args__ = (
    # Composite index for couple_id + page_number queries
    Index('idx_story_progress_couple_page', 'couple_id', 'page_number'),
    # Index for couple_id queries (to get all progress for a couple)
    Index('idx_story_progress_couple_id', 'couple_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False)
    fun_level = db.Column(db.Integer)
    comments = db.Column(db.Text)

class Mission(db.Model):
    __tablename__ = 'missions'

    __table_args__ = (
    # Composite index for filtering by precreated OR created_by
    Index('idx_mission_precreated_created_by', 'is_precreated', 'created_by'),
    # Index for created_by queries (counting user missions)
    Index('idx_mission_created_by', 'created_by'),
    # Index for category filtering
    Index('idx_mission_category', 'category'),
    )


    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=True)  # Null for pre-created
    is_precreated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # For pre-created missions: is_precreated=True, created_by=None
    # For user-created: is_precreated=False, created_by=user.id


# to handle the accepted missions
class CoupleMission(db.Model):
    __tablename__ = 'couples_missions'

    __table_args__ = (
    # Composite index for couple_id + mission_id queries (checking acceptance)
    Index('idx_couple_mission_couple_mission', 'couple_id', 'mission_id'),
    # Index for couple_id queries (getting all accepted missions)
    Index('idx_couple_mission_couple_id', 'couple_id'),
    # Index for mission_id queries (when deleting missions)
    Index('idx_couple_mission_mission_id', 'mission_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id', ondelete='CASCADE'), nullable=False) 
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id', ondelete='CASCADE'), nullable=False)  
    accepted_at = db.Column(db.DateTime, default=datetime.now)


class Challenges(db.Model):
    __tablename__ = 'challenges'

    __table_args__ = (
    # Similar indexes as Mission
    Index('idx_challenges_precreated_created_by', 'is_precreated', 'created_by'),
    Index('idx_challenges_created_by', 'created_by'),
    Index('idx_challenges_category', 'category'),
    )


    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=True)  # Null for pre-created
    is_precreated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)



# to handle the accepted missions
class CoupleChallenges(db.Model):
    __tablename__ = 'couple_challenges'

    __table_args__ = (
    # Similar indexes as CoupleMission
    Index('idx_couple_challenges_couple_challenge', 'couple_id', 'challenges_id'),
    Index('idx_couple_challenges_couple_id', 'couple_id'),
    Index('idx_couple_challenges_challenge_id', 'challenges_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id', ondelete='CASCADE') , nullable=False)
    challenges_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'),  nullable=False)
    accepted_at = db.Column(db.DateTime, default=datetime.now)


class Scenario(db.Model):
    __tablename__ = 'scenarios'

    __table_args__ = (
    # Index for created_by queries
    Index('idx_scenario_created_by', 'created_by'),
    # Index for precreated filtering
    Index('idx_scenario_precreated', 'is_precreated'),
    )

    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String(150), nullable=False)
    roles = db.Column(db.JSON, nullable=False)  # Stores list of strings
    prompt = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(50))  # Flexible time format (e.g., "8:00 PM")
    is_precreated = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class CoupleScenario(db.Model):
    __tablename__ = 'couples_scenarios'

    __table_args__ = (
    # Similar indexes as other couple association tables
    Index('idx_couple_scenario_couple_scenario', 'couple_id', 'scenario_id'),
    Index('idx_couple_scenario_couple_id', 'couple_id'),
    Index('idx_couple_scenario_scenario_id', 'scenario_id'),
    )

    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    accepted_at = db.Column(db.DateTime, default=datetime.now)




