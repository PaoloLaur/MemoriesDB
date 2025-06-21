from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
from models import db, bcrypt
from routes import api as api_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from seed_missions import seed_missions
from seed_challenges import seed_challenges
from seed_scenarios import seed_scenarios
import os 
import redis
from flask_migrate import Migrate


def get_user_id():
    """Custom key function for rate limiting based on user_id"""
    try:
        # Try to get user_id from JWT token
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
        else:
            # Fallback to IP address for unauthenticated requests
            return f"ip:{get_remote_address()}"
    except:
        # If JWT is not available, use IP address
        return f"ip:{get_remote_address()}"



def build_redis_uri():
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    db = int(os.getenv('REDIS_DB', 0))
    password = os.getenv('REDIS_PASSWORD', None)
    
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    else:
        return f"redis://{host}:{port}/{db}"

# Initialize limiter with proper Redis storage and custom key function
limiter = Limiter(
    key_func=get_user_id,
    storage_uri=build_redis_uri(),
    default_limits=["3000 per hour"]
)

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
    
    # Test Redis connection
    try:
        # Create Redis client for testing
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )
        redis_client.ping()
        print("✅ Redis connection successful")
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("Rate limiting will fall back to in-memory storage")


    db.init_app(app)
    bcrypt.init_app(app)

    migrate = Migrate(app, db) 


    # here register blueprints 
    app.register_blueprint(api_blueprint, url_prefix='/api')


    # After all routes are registered and before app.run()
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} ({', '.join(rule.methods)})")
    print("========================\n")

    print(f"Limiter instances: {app.extensions['limiter']}")
    print(f"Number of limiters: {len(app.extensions['limiter'])}")
    return app

app = create_app()



# here start the app 

if __name__ == '__main__': # Ensuring code only runs when executing the file directly (python app.py), not when imported as a module, never used in production deployments (WSGI servers like Gunicorn don't execute this block).

    logging.basicConfig(level=logging.DEBUG) # dangerous in prod,change to logging.INFO

    with app.app_context():
        
        seed_missions(app, db)

        seed_challenges(app, db)
        
        seed_scenarios(app, db)
    
        app.run(host='0.0.0.0', port=5001, ssl_context='adhoc')  

