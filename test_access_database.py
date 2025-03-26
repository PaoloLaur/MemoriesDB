import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Construct DB URI from environment
DB_URI = os.environ.get('DATABASE_URL') or \
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@" \
    f"{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"

def test_connection():
    try:
        engine = create_engine(DB_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL {version}")
            
            # Verify user privileges
            result = conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"🔑 Connected as user: {user}")
            
            # Verify database
            result = conn.execute(text("SELECT current_database()"))
            db = result.scalar()
            print(f"📦 Current database: {db}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()