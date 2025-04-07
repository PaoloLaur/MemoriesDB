from datetime import datetime

precreated_challenges = [
    {
        "content": "Spicy Dance-Off: Have a 3-minute dance battle where you try to out-seduce each other using only body movements",
        "category": "Physical"
    },
    {
        "content": "Sensory Blackout: Feed each other mystery foods blindfolded and guess what they are",
        "category": "Sensory"
    },
    {
        "content": "Role Reversal Quiz: Answer intimate questions while pretending to be each other",
        "category": "Emotional"
    },
    {
        "content": "Tension Tower: Build a tower of objects using only your mouths (start with light snacks like crackers)",
        "category": "Playful"
    },
    {
        "content": "Memory Lane: Recreate your first date... with exaggerated romantic clichés",
        "category": "Nostalgic"
    },
    {
        "content": "Whisper Challenge: Describe your fantasies using only single-word hints while loud music plays",
        "category": "Communication"
    },
    {
        "content": "Sync or Swim: Attempt to mirror each other's movements perfectly for 5 minutes straight",
        "category": "Coordination"
    },
    {
        "content": "Sensual Sketch: Draw portraits of each other using only non-dominant hands",
        "category": "Creative"
    },
    {
        "content": "Temperature Play: Exchange massages using alternating hot/cold items (safety first!)",
        "category": "Sensory"
    },
    {
        "content": "Eye Contact Marathon: Maintain unbroken eye contact while asking increasingly personal questions",
        "category": "Intimacy"
    },
    {
        "content": "Fantasy Charades: Act out secret desires without using words",
        "category": "Playful"
    },
    {
        "content": "Breathing Sync: Match your breathing patterns while sitting back-to-back",
        "category": "Connection"
    },
    {
        "content": "Scent Memory: Create custom perfumes/oils for each other using household items",
        "category": "Sensory"
    },
    {
        "content": "Kiss Catalogue: Invent 5 new types of kisses and name them together",
        "category": "Physical"
    },
    {
        "content": "Future Fantasy: Describe your ideal day together 10 years from now in vivid detail",
        "category": "Emotional"
    }
]

def seed_challenges(app, db):
    with app.app_context():
        from models import Challenges  # Local import to avoid circular dependency
        
        # Only seed if no precreated challenges exist
        if not Challenges.query.filter_by(is_precreated=True).first():
            challenges_to_add = [
                Challenges(
                    content=challenge["content"],
                    category=challenge["category"],
                    is_precreated=True,
                    created_at=datetime.utcnow()
                ) for challenge in precreated_challenges
            ]
            
            try:
                db.session.bulk_save_objects(challenges_to_add)
                db.session.commit()
                print(f"✅ Successfully seeded {len(challenges_to_add)} precreated challenges")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error seeding challenges: {str(e)}")