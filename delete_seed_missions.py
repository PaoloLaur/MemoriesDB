from models import db, Mission

def delete_precreated_missions():
    """Delete all missions where is_precreated is True"""
    try:
        # Count how many will be deleted (optional, for confirmation)
        count = Mission.query.filter(Mission.is_precreated == True).count()
        print(f"Found {count} pre-created missions to delete")
        
        # Delete all pre-created missions
        deleted_count = Mission.query.filter(Mission.is_precreated == True).delete()
        
        # Commit the transaction
        db.session.commit()
        
        print(f"Successfully deleted {deleted_count} pre-created missions")
        return deleted_count
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Error deleting Mission: {e}")
        raise

if __name__ == '__main__':
    # If running this as a script, you'll need app context
    from app import app
    
    with app.app_context():
        # Use method 1 (recommended for most cases)
        delete_precreated_missions()
        