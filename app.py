from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
from models import db, bcrypt, Mission, Challenges, Scenario
from routes import api as api_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from commands import register_commands  # Import our commands
import os 
import redis
from flask_migrate import Migrate
from urllib.parse import urlparse
from seed_missions import precreated_missions
from seed_challenges import precreated_challenges  
from seed_scenarios import precreated_scenarios
from datetime import datetime
from sqlalchemy import text

def get_user_id():
    """Custom key function for rate limiting based on user_id"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
        else:
            return f"ip:{get_remote_address()}"
    except:
        return f"ip:{get_remote_address()}"



REDIS_URL = os.getenv('REDIS_URL')



# Initialize limiter
limiter = Limiter(
    key_func=get_user_id,
    storage_uri=REDIS_URL,
    default_limits=["3000 per hour"]
)


# FUNCTIONS TO INITIALIZE PRECREATED DATA OR AUTOMATICALLY SEED/UPDATE DATA


def auto_initialize_database(app):
    """Automatically initialize and seed database on startup."""
    with app.app_context():
        try:
            # Check if database is accessible
            db.session.execute(text('SELECT 1'))
            app.logger.info("✅ Database connection successful")
            
            # Create all tables if they don't exist
            db.create_all()
            app.logger.info("✅ Database tables created/verified")
            
            # Auto-seed data
            auto_seed_all_data(app)
            
        except Exception as e:
            app.logger.error(f"❌ Database initialization failed: {e}")
            # Don't crash the app, just log the error


def auto_seed_all_data(app):
    """Automatically seed all data if needed."""
    try:
        # Check if we have any precreated data
        mission_count = Mission.query.filter_by(is_precreated=True).count()
        challenge_count = Challenges.query.filter_by(is_precreated=True).count()
        scenario_count = Scenario.query.filter_by(is_precreated=True).count()
        
        if mission_count == 0:
            app.logger.info("🌱 Auto-seeding missions...")
            auto_seed_missions()
        else:
            app.logger.info(f"ℹ️  Found {mission_count} existing missions, checking for updates...")
            auto_update_missions()
            
        if challenge_count == 0:
            app.logger.info("🌱 Auto-seeding challenges...")
            auto_seed_challenges()
        else:
            app.logger.info(f"ℹ️  Found {challenge_count} existing challenges, checking for updates...")
            auto_update_challenges()
            
        if scenario_count == 0:
            app.logger.info("🌱 Auto-seeding scenarios...")
            auto_seed_scenarios()
        else:
            app.logger.info(f"ℹ️  Found {scenario_count} existing scenarios, checking for updates...")
            auto_update_scenarios()
            
    except Exception as e:
        app.logger.error(f"❌ Auto-seeding failed: {e}")


def auto_seed_missions():
    """Auto-seed missions."""
    missions = [
        Mission(
            content=mission_data["content"],
            category=mission_data["category"],
            is_precreated=True,
            created_at=datetime.utcnow()
        ) for mission_data in precreated_missions
    ]
    
    db.session.bulk_save_objects(missions)
    db.session.commit()
    print(f"✅ Auto-seeded {len(missions)} missions")


def auto_update_missions():
    """Smart update - only add new missions."""
    existing_contents = {m.content for m in Mission.query.filter_by(is_precreated=True).all()}
    new_missions = []
    
    for mission_data in precreated_missions:
        if mission_data["content"] not in existing_contents:
            new_missions.append(Mission(
                content=mission_data["content"],
                category=mission_data["category"],
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_missions:
        db.session.bulk_save_objects(new_missions)
        db.session.commit()
        print(f"✅ Auto-added {len(new_missions)} new missions")


def auto_seed_challenges():
    """Auto-seed challenges."""
    challenges = [
        Challenges(
            content=challenge_data["content"],
            category=challenge_data["category"],
            is_precreated=True,
            created_at=datetime.utcnow()
        ) for challenge_data in precreated_challenges
    ]
    
    db.session.bulk_save_objects(challenges)
    db.session.commit()
    print(f"✅ Auto-seeded {len(challenges)} challenges")


def auto_update_challenges():
    """Smart update - only add new challenges."""
    existing_contents = {c.content for c in Challenges.query.filter_by(is_precreated=True).all()}
    new_challenges = []
    
    for challenge_data in precreated_challenges:
        if challenge_data["content"] not in existing_contents:
            new_challenges.append(Challenges(
                content=challenge_data["content"],
                category=challenge_data["category"],
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_challenges:
        db.session.bulk_save_objects(new_challenges)
        db.session.commit()
        print(f"✅ Auto-added {len(new_challenges)} new challenges")


def auto_seed_scenarios():
    """Auto-seed scenarios."""
    scenarios = [
        Scenario(
            setting=scenario_data["setting"],
            roles=scenario_data["roles"],
            prompt=scenario_data["prompt"],
            time=scenario_data.get("time"),
            is_precreated=True,
            created_at=datetime.utcnow()
        ) for scenario_data in precreated_scenarios
    ]
    
    db.session.bulk_save_objects(scenarios)
    db.session.commit()
    print(f"✅ Auto-seeded {len(scenarios)} scenarios")


def auto_update_scenarios():
    """Smart update - only add new scenarios."""
    existing_prompts = {s.prompt for s in Scenario.query.filter_by(is_precreated=True).all()}
    new_scenarios = []
    
    for scenario_data in precreated_scenarios:
        if scenario_data["prompt"] not in existing_prompts:
            new_scenarios.append(Scenario(
                setting=scenario_data["setting"],
                roles=scenario_data["roles"],
                prompt=scenario_data["prompt"],
                time=scenario_data.get("time"),
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_scenarios:
        db.session.bulk_save_objects(new_scenarios)
        db.session.commit()
        print(f"✅ Auto-added {len(new_scenarios)} new scenarios")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set logging level based on environment
    if os.getenv('FLASK_ENV') == 'PRODUCTION':
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Initialize extensions
    jwt = JWTManager(app) # uses JWT_SECRET_KEY from config
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    limiter.init_app(app)
    
    # Register CLI commands
    register_commands(app)

    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        return jsonify({"error": "Invalid token"}), 401

    CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # Test Redis connection using REDIS_URL
    try:
        redis_url = os.getenv('REDIS_URL')
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        app.logger.info("✅ Redis connection successful")
    except redis.ConnectionError as e:
        app.logger.warning(f"❌ Redis connection failed: {e}")
   
    # 🚀 AUTO-INITIALIZE DATABASE AND SEED DATA
    auto_initialize_database(app)
   
    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Test database
            db.session.execute('SELECT 1')
            
            return jsonify({'status': 'healthy'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    return app


app = create_app()


# Only run in development
if __name__ == '__main__':
    # This only runs during development
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context='adhoc')