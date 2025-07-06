from datetime import datetime

precreated_challenges = [
    # EASY
    {
        "content": "Slow Dance in Your Underwear: put on a song and dance together just the two of you.",
        "category": "Light"
    },
    {
        "content": "Kiss for 30 seconds in every room of your home (yes, even the hallway).",
        "category": "Light"
    },
    {
        "content": "Take turns showing your partner where you love being touched (hands and mouth only).",
        "category": "Light"
    },
    {
        "content": "Set a 5-minute timer and do nothing but turning on each other — no distractions, no multitasking.",
        "category": "Light"
    },
    {
        "content": "Go out on a date and whisper naughty things in your partner’s ear and watch their reaction.",
        "category": "Light"
    },
    {
        "content": "Lock eyes for one full minute and then act on the first feeling that comes up.",
        "category": "Light"
    },
    {
        "content": "Send a playful dare to your partner over text, then complete it before the night ends.",
        "category": "Light"
    },
    {
        "content": "Recreate a makeout scene from your favorite movie — costumes optional!",
        "category": "Light"
    },
    {
        "content": "Take a warm bath or shower together. Soap each other up slowly.",
        "category": "Light"
    },
    {
        "content": "Pick only one item from each other’s wardrobe and wear it, even if just for laughs.",
        "category": "Light"
    },

    # MEDIUM
    {
        "content": "One partner wears a blindfold while the other uses gentle touch to...",
        "category": "Medium"
    },
    {
        "content": "Each of you choose 3 songs to a shared playlist, then let the music guide your next hour... be creative!",
        "category": "Medium"
    },
    {
        "content": "Lie very close together but resist touching. Whoever gives in first has to do something for the other...",
        "category": "Medium"
    },
    {
        "content": "Talk for at least 15 minutes about what you would like your partner to do during intimate time... then recreate it.",
        "category": "Medium"
    },
    {
        "content": "Private Photoshoot: take pictures of each other, only if you feel comfortable, to be shared only between you two.",
        "category": "Medium"
    },
    {
        "content": "Use ice cubes to explore each others... passions",
        "category": "Medium"
    },
    {
        "content": "One of you takes control. Arouse your partner as much as possible, but don’t let them finish... at least not right away.",
        "category": "Medium"
    },
    {
        "content": "Find a spicy story online. One reads aloud slowly while the other listens, and acts, accordingly...",
        "category": "Medium"
    },
    {
        "content": "Write body parts and spicy actions on paper, roll dices and obey to who wins each round.",
        "category": "Medium"
    },
    {
        "content": "One partner sits. The other asks questions. If the person skips one, they have to open their mouths for 1 minute and...",
        "category": "Medium"
    },

    # HARD
    {
        "content": "Text your partner instructions before you meet them later. They must follow it without explanation.",
        "category": "Hard"
    },
    {
        "content": "Use a soft scarf or tie to limit your partner's movement, and...",
        "category": "Hard"
    },
    {
        "content": "Bring whipped cream, chocolate syrup, or honey to the bedroom. Choose a “canvas” and decorate — then slowly clean up...",
        "category": "Hard"
    },
    {
        "content": "Give each other a secret task to perform discreetly in public... don't get caught!",
        "category": "Hard"
    },
    {
        "content": "Get in front of a large mirror and... watch yourselves.",
        "category": "Hard"
    },
    {
        "content": "Create a DIY strip game. Each round lost, remove a piece of clothing or do a sexy challenge.",
        "category": "Hard"
    },
    {
        "content": "One of you becomes the \"boss\" for the evening: giving orders, and deciding when (or if) the other is allowed to take control.",
        "category": "Hard"
    },
    {
        "content": "Choose a fantasy or kink you’ve both talked about but haven’t tried... and bring it to life (with trust and consent).",
        "category": "Hard"
    },
    {
        "content": "Each gets 3 sexy wishes for the night. No questions asked (within boundaries).",
        "category": "Hard"
    },
    {
        "content": "Pretend you're strangers meeting at a bar and take it from there; you'll respect each other less and be riskier...",
        "category": "Hard"
    }
]

def seed_challenges(app, db):
    with app.app_context():
        from models import Challenges  # Local import to avoid circular dependency
        
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
