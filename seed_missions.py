# seed_missions.py
from datetime import datetime

precreated_missions = [
    {
        "content": "Cook a meal together using only 5 ingredients",
        "category": "Food"
    },
    {
        "content": "Share your favorite memory from when you first met",
        "category": "Reflection"
    },
    {
        "content": "Dance together to your song for 3 minutes straight",
        "category": "Fun"
    },
    {
        "content": "Write each other a handwritten note and exchange",
        "category": "Romance"
    },
    {
        "content": "Recreate your first date",
        "category": "Romance"
    },
    {
        "content": "Try a new workout routine together",
        "category": "Fitness"
    },
    {
        "content": "Watch each other's favorite childhood movie",
        "category": "Fun"
    }
]

def seed_missions(app, db):
    with app.app_context():
        from models import Mission  # Local import to avoid circular dependency
        
        # Only seed if no precreated missions exist
        if not Mission.query.filter_by(is_precreated=True).first():
            missions_to_add = [
                Mission(
                    content=mission["content"],
                    category=mission["category"],
                    is_precreated=True,
                    created_at=datetime.utcnow()
                ) for mission in precreated_missions
            ]
            
            try:
                db.session.bulk_save_objects(missions_to_add)
                db.session.commit()
                print(f"✅ Successfully seeded {len(missions_to_add)} precreated missions")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error seeding missions: {str(e)}")