from datetime import datetime


precreated_scenarios = [
    {
        "setting": "Neon Noir Metropolis",
        "roles": ["Corporate Spy", "Rogue AI"],
        "prompt": "Exchange encrypted data through physical touch in crowded streets",
        "time": "8:00 PM"
    },
    {
        "setting": "Quantum Garden",
        "roles": ["Time Gardener", "Paradox Bloom"],
        "prompt": "Navigate temporal loops through sensory feedback",
        "time": "9:30 PM"
    },
    {
        "setting": "Holographic Masquerade",
        "roles": ["Identity Sculptor", "Digital Phantom"],
        "prompt": "Reveal truths through avatar distortions",
        "time": "7:45 PM"
    }
]

def seed_scenarios(app, db):
    with app.app_context():
        from models import Scenario
        
        if not Scenario.query.filter_by(is_precreated=True).first():
            scenarios_to_add = [
                Scenario(
                    setting=scenario["setting"],
                    roles=scenario["roles"],
                    prompt=scenario["prompt"],
                    time=scenario["time"],
                    is_precreated=True,
                    created_at=datetime.utcnow()
                ) for scenario in precreated_scenarios
            ]
            
            try:
                db.session.bulk_save_objects(scenarios_to_add)
                db.session.commit()
                print(f"✅ Successfully seeded {len(scenarios_to_add)} scenarios")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error seeding scenarios: {str(e)}")