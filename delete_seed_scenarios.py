from models import db, Scenario

def delete_precreated_scenarios():
    """Delete all scenarios where is_precreated is True"""
    try:
        # Count how many will be deleted (optional, for confirmation)
        count = Scenario.query.filter(Scenario.is_precreated == True).count()
        print(f"Found {count} pre-created scenarios to delete")
        
        # Delete all pre-created scenarios
        deleted_count = Scenario.query.filter(Scenario.is_precreated == True).delete()
        
        # Commit the transaction
        db.session.commit()
        
        print(f"Successfully deleted {deleted_count} pre-created scenarios")
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
        delete_precreated_scenarios()
        