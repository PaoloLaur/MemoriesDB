from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
from models import db, bcrypt
from routes import api as api_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from commands import register_commands  # Import our commands
import os 
import redis
from flask_migrate import Migrate


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


def build_redis_uri():
    host = os.getenv('REDIS_HOST')
    port = int(os.getenv('REDIS_PORT', 6379))
    db_num = int(os.getenv('REDIS_DB', 0))
    password = os.getenv('REDIS_PASSWORD')
    
    # In production, require explicit Redis host
    if os.getenv('FLASK_ENV') == 'PRODUCTION' and not host:
        raise ValueError("REDIS_HOST must be set in production")
    
    # Fallback to localhost only in development
    host = host or 'localhost'
    
    if password:
        return f"redis://:{password}@{host}:{port}/{db_num}"
    else:
        return f"redis://{host}:{port}/{db_num}"
  

# Initialize limiter
limiter = Limiter(
    key_func=get_user_id,
    storage_uri=build_redis_uri(),
    default_limits=["3000 per hour"]
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set logging level based on environment
    if os.getenv('FLASK_ENV') == 'PRODUCTION':
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Initialize extensions
    jwt = JWTManager(app)
    db.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    limiter.init_app(app)
    
    # Register CLI commands
    register_commands(app)

    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        return jsonify({"error": "Invalid token"}), 401

    cors_origins = os.getenv('CORS_ORIGINS')
    if not cors_origins:
        if os.getenv('FLASK_ENV') == 'PRODUCTION':
            raise ValueError("CORS_ORIGINS must be set in production")
        else:
            cors_origins = 'http://192.168.1.9:5001'  # Development default

    cors_origins_list = cors_origins.split(',')

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins_list,
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Test Redis connection
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )

        host=os.getenv('REDIS_HOST', 'localhost'),
            
        if os.getenv('FLASK_ENV') == 'PRODUCTION' and not host == 'localhost':
            raise ValueError("REDIS_HOST must be set in production")
        
        redis_client.ping()
        app.logger.info("✅ Redis connection successful")
    except redis.ConnectionError as e:
        app.logger.warning(f"❌ Redis connection failed: {e}")

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