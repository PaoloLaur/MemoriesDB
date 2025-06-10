from models import db, Challenges

def delete_precreated_challenges():
    """Delete all challenges where is_precreated is True"""
    try:
        # Count how many will be deleted (optional, for confirmation)
        count = Challenges.query.filter(Challenges.is_precreated == True).count()
        print(f"Found {count} pre-created challenges to delete")
        
        # Delete all pre-created challenges
        deleted_count = Challenges.query.filter(Challenges.is_precreated == True).delete()
        
        # Commit the transaction
        db.session.commit()
        
        print(f"Successfully deleted {deleted_count} pre-created challenges")
        return deleted_count
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Error deleting challenges: {e}")
        raise

if __name__ == '__main__':
    # If running this as a script, you'll need app context
    from app import app
    
    with app.app_context():
        # Use method 1 (recommended for most cases)
        delete_precreated_challenges()
        