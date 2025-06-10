from datetime import datetime


precreated_scenarios = [
    {
        "setting": "Luxury Hotel Penthouse",
        "roles": ["Mysterious Billionaire", "Curious Housekeeper"],
        "prompt": (
            "While cleaning the room, the housekeeper finds a naughty invitation hidden under the pillow, daring them to explore. "
            "They must follow the billionaire’s seductive instructions one by one: open the wine, sit on the bed, take off one piece of clothing… "
            "Every action gets them deeper into a sensual game of control and submission, ending in wild passion on the silk sheets."
        ),
        "time": "10:00 PM"
    },
    {
        "setting": "Secret Speakeasy",
        "roles": ["Jazz Singer", "Undercover Detective"],
        "prompt": (
            "Start with teasing conversation at the bar — the detective subtly interrogates, the singer flirts and resists. "
            "For every question the detective asks, the singer must give an answer… but only if the detective earns it with a sensual touch. "
            "When the singer performs a private song, the detective must ‘thank’ them without words — using only their body. "
            "End the night behind the curtains, clothes barely hanging on."
        ),
        "time": "9:00 PM"
    },
    {
        "setting": "Private Island Resort",
        "roles": ["Flirty Bartender", "Wealthy Guest"],
        "prompt": (
            "The bartender dares the guest to answer bold questions or take sexy dares — removing clothing, whispering fantasies, or showing a hidden tattoo. "
            "If the guest completes 3 dares in a row, they get to order the bartender around for 5 minutes. "
            "If they fail or blush, the bartender can touch them wherever they want. "
            "Eventually, one ends up on the bar counter, moaning while the other takes full control."
        ),
        "time": "8:30 PM"
    },
    {
        "setting": "Art Gallery After Hours",
        "roles": ["Bold Artist", "Muse in Disguise"],
        "prompt": (
            "The muse agrees to pose nude for a forbidden sketch. The artist must draw while resisting the urge to touch. "
            "The muse slowly teases — changing poses, making soft noises, eye contact. "
            "If the artist breaks and touches before the drawing is done, they have to make it up to the muse with hands, lips, and body. "
            "If the drawing finishes without touching, the muse rewards them by taking full control of the next hour."
        ),
        "time": "11:00 PM"
    },
    {
        "setting": "Deserted School",
        "roles": ["Strict Professor", "Rebellious University Student"],
        "prompt": (
            "The professor catches the student breaking rules after hours. As punishment, the student must learn something word-for-word from the teacher. "
            "If the student doesn't follow, or makes mistakes, the professor decides how they’ll ‘learn their lesson’. "
            "Roleplay the full power exchange: strict voice, sharp commands, bent over the desk discipline."
        ),
        "time": "9:00 PM"
    },
    {
        "setting": "Luxury Train Cabin",
        "roles": ["Elegant Stranger", "Royalty Member"],
        "prompt": (
            "You’re both strangers in a private cabin — but each wants a secret the other holds. "
            "During dinner, you flirt while playing a truth-or-dare-style seduction game. If someone refuses to answer or perform a task, they loose a point. "
            "Whoever ends up loosing more than 3, must beg for the truth and let the other have full control for the rest of the ride."
        ),
        "time": "6:45 PM"
    },
    {
        "setting": "Gothic Manor",
        "roles": ["Vampire Lord", "Willing Visitor"],
        "prompt": (
            "The visitor enters the dark manor, offering themselves in exchange for forbidden pleasure. "
            "The vampire tempts them with promises of ecstasy and eternal lust. The game: the visitor must let the vampire tease every part of them without climaxing. "
            "If they break, they become the vampire’s toy for the night. If they hold on, they get to make the vampire kneel and beg. "
            "Darkness, moans, and dominance mix into a sinful night."
        ),
        "time": "12:00 AM"
    },
    {
        "setting": "High-Stakes Poker Night",
        "roles": ["Card Shark", "Dealer with Secrets"],
        "prompt": (
            "Every round of poker, someone loses a piece of clothing. But more than chips are on the line. "
            "Whoever ends up naked must crawl across the table and serve the winner however they demand, no speaking, just action. "
            "You can bluff, tease, cheat… but the winner calls all the shots. Once the game ends, the real play begins."
        ),
        "time": "10:30 PM"
    },
    {
        "setting": "Rainy Night Taxi Ride",
        "roles": ["Confident Driver", "Mysterious Passenger"],
        "prompt": (
            "The passenger gets in late at night. The driver offers a ride with a twist — for each stoplight, they must answer an intimate question. "
            "If they lie, hesitate, or blush too hard, the driver earns a reward — a kiss, a touch, or control for the next question. "
            "Eventually, when things get too hot to handle, the driver pulls over and climbs into the back seat. Now the questions are physical."
        ),
        "time": "11:15 PM"
    },
    {
        "setting": "Moonlit Rooftop",
        "roles": ["Runaway Bride", "Best Man"],
        "prompt": (
            "She ran from the wedding, found you on the rooftop. You have 30 minutes before someone finds her. "
            "You start by calming her down — kisses, soft touches, dirty jokes. "
            "Then you help her 'forget everything' by making her lose control. Dress torn, panties on the ground, your hands all over her. "
            "Bonus challenge: try not to moan loud enough to get caught."
        ),
        "time": "1:00 AM"
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