from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import json 
from datetime import datetime, timezone
import uuid


db = SQLAlchemy()
bcrypt = Bcrypt()

"""
what is needed?

user 

    id not nullable
    username not nullable
    password #be hashed not nullable
    couple_id # sent fromm the frontend after a user registrates not nullable
    couple # this is a relationship with the class Couple, backref is users not nullable 

    date of relationship ?

    selected_missions_list (with some reference to couple id to fetch them for both users)
    selected_spicy_activities (with some reference to couple id to fetch them for both users) 

    discarded_missions ?
    discarded_spicy_activities ?




couple

    id
    level
    what else?


notebook 
    id primary key which should be the same as the couple one
    date = date model, which has the values for each 'page in it'

    for each data there are 
        comments = [] up to two values inside the list, each comment has an id (which is the one of the user which posted it)
        media = [] up to two urls values inside the list, each media has an id (which is the one of the user which posted it)

missions 
    id
    missions = not nullable, a list of strings (missions)
    user_id if one of the two users created it 
    

spicy
    id
    spicy_activities = not nullable, a list of strings (activities)
    scenarios = not nullable, a list of strings (scenarios)
    user_id if one of the two users created it 



    

"""

class User(db.Model):
    __tablename__ = 'users' # what is this?? what properties does __tablename__ have?


    __table_args__ = (
        db.CheckConstraint('couple_id IS NOT NULL', name='user_must_belong_to_couple'),
    )
   



    #not nullable keys

    id = db.Column(db.Integer, primary_key=True) # why primary key? this is built in such a way that every id is unique, but how?
    username = db.Column(db.String(20), unique=True, nullable=False) # what is the (80)?
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(14), nullable=False)  # Add this line

    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False) # what is ForeignKey?
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # is this necessary? does it have a problem??

    points = db.Column(db.Integer, default=0, nullable=False)
    couple_name = db.Column(db.String(30))  # For couple creator

    #nullable keys

    couple = db.relationship('Couple', back_populates='users') # IMP. : what is this db.relationship('Couple', back_populates='users')???

    # understanding the following structure. explain what @property, @password.setter and check_password are, why are defined inside the model and not in routes, etc.


    @property
    def password(self):
        raise AttributeError('password is write-only')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    

# OTHER CLASSES, NOT CURRENT FOCUS

class Couple(db.Model):
    __tablename__ = 'couples'


    id = db.Column(db.Integer, primary_key=True)
    invitation_code = db.Column(db.String(36), unique=True, nullable=False)  # invitation code of the first user
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    couple_name = db.Column(db.String(30), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)

    users = db.relationship('User', back_populates='couple')

    def __init__(self, couple_name):
        self.invitation_code = str(uuid.uuid4())  # Generate unique code
        self.couple_name = couple_name


class Notebook(db.Model):
    __tablename__ = 'notebooks'
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    comments = db.Column(db.JSON)  # Store as {'user1_id': 'comment', 'user2_id': 'comment'}
    media = db.Column(db.JSON)     # Store as {'user1_id': 'url', 'user2_id': 'url'}

class Mission(db.Model):
    __tablename__ = 'missions'
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'))
    missions = db.Column(db.JSON, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(150), nullable = False)
    

class SpicyActivity(db.Model):
    __tablename__ = 'spicy_activities'
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'))
    activities = db.Column(db.JSON, nullable=False)
    scenarios = db.Column(db.JSON, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

