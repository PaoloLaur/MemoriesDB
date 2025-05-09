from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
from models import db, bcrypt
from routes import api as api_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from seed_missions import seed_missions
from seed_challenges import seed_challenges
from seed_scenarios import seed_scenarios
import os 


limiter = Limiter(key_func=get_remote_address)

def create_app():


    app = Flask(__name__) # __name__ variable that takes the name of the file (in this case app.py)
    app.config.from_object(Config) # from_object is safe, allows for configuring the flask application from the Config class

    jwt = JWTManager(app) 


    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        print(f"❌ Invalid token: {error}")
        return jsonify({"error": "Invalid token"}), 401

    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # Never use origins="*" in production - specify exact domains

            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
     # a flask extension, allows for cross origin resource sharing. In produciton origins should be either restricted or recondidered
    limiter.init_app(app)
    limiter.default_limits = ["10800 per hour"] 


    db.init_app(app)
    bcrypt.init_app(app)

    # here register blueprints 
    app.register_blueprint(api_blueprint, url_prefix='/api')


    # After all routes are registered and before app.run()
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} ({', '.join(rule.methods)})")
    print("========================\n")


    return app

app = create_app()



# here start the app 

if __name__ == '__main__': # Ensuring code only runs when executing the file directly (python app.py), not when imported as a module, never used in production deployments (WSGI servers like Gunicorn don't execute this block).

    logging.basicConfig(level=logging.DEBUG) # dangerous in prod,change to logging.INFO

    with app.app_context():
        #db.drop_all()  # REMOVE BEFORE PROD

        db.create_all() # with app.app_context is needed otherwise sqlalchemy doesnt know which config to use for db connections, creates all database tables based on your SQLAlchemy models. Don't use in prod, use either alembic or flask migration

        seed_missions(app, db)

        seed_challenges(app, db)
        
        seed_scenarios(app, db)
    
        app.run(host='0.0.0.0', port=5001, ssl_context='adhoc')  

