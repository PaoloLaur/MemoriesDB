# seed_missions.py
from datetime import datetime

precreated_missions = [

    # ROMANCE
    {
        "content": "Choose a song you might want to dance to and choreograph a simple first dance together. Practice it, light some candles, dress up, and perform it in your living room.",
        "category": "Romance"
    },
    {
        "content": "Sit face to face. Each of you asks the other 3 deep questions you’ve never asked before (can be romantic, personal, or about your future). You must answer honestly.",
        "category": "Romance"
    },
    {
        "content": "Recreate the first time you met — dress how you did, meet at the same place (or recreate it), and act it out as if it’s the first time you’re seeing each other again.",
        "category": "Romance"
    },
    {
        "content": "Over dinner or a walk, take turns giving each other compliments — but you can’t repeat the same compliment twice. Keep going until you hit 100.",
        "category": "Romance"
    },
    {
        "content": "Record a mock podcast episode together where you retell your love story — how you met, your funniest moment, a hard time you overcame. Use your phone and share it just between the two of you.",
        "category": "Romance"
    },
    {
        "content": "Spend a full date night in complete silence — no talking, no phones. Try to make your partner laugh. The first one who does, looses.",
        "category": "Romance"
    },
    {
        "content": "Sit apart and write a heartfelt letter to your partner 5 years from now. Include your hopes, dreams, and what you love about them today. Seal the letters and agree on a special date to open them — maybe your anniversary or a future trip.",
        "category": "Romance"
    },
    {
        "content": "Spend an evening designing your future dream home. Draw the layout, pick imaginary furniture, choose room themes, and even assign quirky features (e.g., “secret library slide”). Bonus: create a Pinterest board together!",
        "category": "Romance"
    },
    {
        "content": "Without any limits, each of you describes your fantasy day together, from the moment you wake up to bedtime. Then, combine elements from both and plan a miniature version with what’s realistically possible over the weekend.",
        "category": "Romance"
    },
    {
        "content": "Take the official 5 Love Languages test and share your results. Then, for one day, intentionally express love using your partner’s top love language — not your own.",
        "category": "Romance"
    },

    #FUN

    {
        "content": "Each partner secretly hides a small item (under €5/$5) in a public place (park, bookstore, etc.) with a clue attached. Then, they give each other only 3 creative clues to find the other's item.",
        "category": "Fun"
    },
    {
        "content": "For 24 hours, each person has 3 “Yes” tokens. When used, the other person must say yes (within reason). Plan an adventure using all tokens strategically.",
        "category": "Fun"
    },
    {
        "content": "Open Google Maps, blindfold one partner, and let them tap randomly within a 2-hour drive radius. Wherever the finger lands, you go.",
        "category": "Fun"
    },
    {
        "content": "Create 10 daring but fun challenges for each other (e.g., “ask a stranger to sing with you,” “buy something without using words”). Put them in envelopes and complete them in a public place like a market or festival.",
        "category": "Fun"
    },
    {
        "content": "Each person picks a costume (goofy, romantic, fantasy) for the other to wear. You must go on a full date in those costumes.",
        "category": "Fun"
    },
    {
        "content": "You have 2 hours to create a mock business idea together (logo, name, slogan, and pitch). Then pitch it to a stranger or film a fake commercial.",
        "category": "Fun"
    },
    {
        "content": "Each of you writes 5 wild “bucket list” items on slips of paper and puts them in a jar. Mix and randomly draw one. You must do a version of it (adapted for safety and budget) within 3 days.",
        "category": "Fun"
    },
    {
        "content": "Spend 1 hour together outdoors (park, downtown, or mall) without speaking a single word. Communicate only with gestures, drawings, and facial expressions.",
        "category": "Fun"
    },
    {
        "content": "Write 3 ultra-kind anonymous notes and hand them out to strangers together.",
        "category": "Fun"
    },
    {
        "content": "Visit a nearby city or neighborhood you've never explored. Only rule: No GPS allowed. You must find a landmark, a dessert place, and a place to dance—using only maps, locals, and intuition.",
        "category": "Fun"
    },

    #CREATIVITY

    {
        "content": "Write a short fictional story (300–500 words) together, but with a twist: you must alternate every sentence. Then, hide the story in a bottle and leave it in a public place with a note saying: “To the stranger who finds this, continue the story.”",
        "category": "Creativity"
    },
    {
        "content": "Create your own “art museum” at home. Each of you must make 3 original artworks using different mediums (e.g., a pencil sketch, clay sculpture, digital collage, etc.). Set them up and give each piece a title and a 2-line description.",
        "category": "Creativity"
    },
    {
        "content": "Write a short photo-story (like a silent comic) together with 5 scenes. The twist: you must act as each other in the scenes — switching outfits and mimicking gestures, habits, quirks.",
        "category": "Creativity"
    },
    {
        "content": "Use temporary mediums (chalk, window markers, large paper, or digital tablet) to create a massive collaborative mural or graffiti-style piece about your love story. Must cover at least 1 square meter.",
        "category": "Creativity"
    },
    {
        "content": "Choose a famous scene from a movie, book, or song — and rewrite it as if the characters were you two. Keep the original structure but insert your names, habits, slang, and real situations. Record it then!",
        "category": "Creativity"
    },
    {
        "content": "Using only your hands and materials like dough, sand, clay, or mashed potatoes (yes, really), sculpt each other’s faces — no tools allowed. Reveal at the same time.",
        "category": "Creativity"
    },
    {
        "content": "Make a short 2/3 minute film together and with friends, in 48 hours. Only 1 location, Each person must appear in at least 2 roles (with costume change), Include 1 dramatic monologue and 1 ridiculous dance scene",
        "category": "Creativity"
    },
    {
        "content": "Invite another couple or two friends and give everyone 1 hour to create a themed art piece (e.g., \"What love looks like\"). Use paints, pastels, or digital tools. At the end, hold a fun mini “gallery opening” with drinks and explain the works.",
        "category": "Creativity"
    },
    {
        "content": "Grab some friends, pick a cheesy or romantic song, and plan + shoot a low-budget music video with ridiculous scenes, choreo, and plot. Assign roles like director, star, dancer, editor. Watch it together on a projector or TV!",
        "category": "Creativity"
    },

    # FITNESS

    {
        "content": "For 1 day out of 7, for four consecutive weeks, wake upand complete a 20-minute outdoor movement session together (yoga, run, calisthenics, dance, you choose). End each session by sharing 1 thing you're grateful for.",
        "category": "Fitness"
    },
    {
        "content": "After a light 10-minute stretch together (no talking), sit cross-legged and hold deep eye contact for 3 straight minutes. No phones, no distractions, no words.",
        "category": "Fitness"
    },
    {
        "content": "Go to the gym (or home setup) and do a full 45-minute partner workout without using any machines or weights. You must use each other’s bodyweight (wheelbarrow pushups, partner squats, resisted planks, etc.).",
        "category": "Fitness"
    },
    {
        "content": "Walk 10,000 steps together in one day, but every 1,000 steps, stop and ask a deep question (e.g., “What fear do you hide most?”). Prepare the 10 questions in advance.",
        "category": "Fitness"
    },
    {
        "content": "Go run together at least three times per month, for three months at least!",
        "category": "Fitness"
    },
    {
        "content": "Take a cold shower (or ice bath, if you're bold!) together or one after another. Right after, sit together in towels and write down 10 things you are grateful for having (a house, a job, health …)",
        "category": "Fitness"
    },
    {
        "content": "Choose a healthy dish you’ve never made before. You can only start cooking after you’ve done a 30-minute workout together. The goal: earn your meal.",
        "category": "Fitness"
    },
    {
        "content": "Try a 60-minute partner weight session, but with a twist: one person leads and the other must mirror the workout. Switch roles halfway if you want to, do it as many times as you can",
        "category": "Fitness"
    },
    {
        "content": "For one full day (from wake-up to 8 PM), both of you must avoid added sugar, sitting for more than 120 minutes at a time, and all entertainment screens.",
        "category": "Fitness"
    },
    {
        "content": "Design a fun, unique 20-minute workout that combines both your favorite types of movement (e.g., boxing & dance, yoga & HIIT). Record it, name it, and save it as “our routine.” Do it once a week for a month.",
        "category": "Fitness"
    },
    {
        "content": "Set up a mini challenge course in a park or gym: wheelbarrow races, couple planks, partner squats, 3-legged sprints. Compete against other couples or friends. Prize? The losers cook dinner.",
        "category": "Fitness"
    },
    {
        "content": "Pick a medium-difficulty trail with another couple or group.",
        "category": "Fitness"
    },

    # FOOD

    {
        "content": "Cook a full three-course meal where every dish is based around a single color (e.g. green = pesto pasta, zucchini, matcha dessert). The twist? Spin a virtual color wheel in the app to decide your color.",
        "category": "Food"
    },
    {
        "content": "Choose a country neither of you have visited. Research and cook a traditional appetizer, main course, and dessert from that culture. Set the table and dress in the local theme.",
        "category": "Food"
    },
    {
        "content": "One of you wears a blindfold while the other gives verbal instructions to cook a dish, from chopping to plating. Then switch roles for another dish.",
        "category": "Food"
    },
    {
        "content": "Create a full dinner using only what you currently have at home, no shopping allowed. Bonus: set a timer for 60 minutes from start to plate.",
        "category": "Food"
    },
    {
        "content": "Go out for lunch or dinner at least 4 times, and try each time a different cuisines, in 6 months.",
        "category": "Food"
    },
    {
        "content": "Each of you secretly picks a recipe you think the other will love — then you cook their recipe and they cook yours. Reveal the dishes only at dinnertime.",
        "category": "Food"
    },
    {
        "content": "Take your favorite fast food meal and try to recreate it at a gourmet level at home. Ex: Big Mac becomes Wagyu burger etc.",
        "category": "Food"
    },
    {
        "content": "Create a dish that represents your relationship — in ingredients, plating, or name. Then explain the story behind it to each other over dinner.",
        "category": "Food"
    },
    {
        "content": "Each friend/couple brings 1 unusual ingredient (like wasabi peas or dragon fruit). You must each cook or plate something using all the ingredients together in 1 hour. No prep allowed beforehand. Judge by creativity, taste, and presentation.",
        "category": "Food"
    },
    {
        "content": "Pick a theme (like tacos, sushi, or personal pizzas). Each friend brings 1 or 2 toppings. Make your versions and then a “Frankenstein” mix using at least 1 item from each person. Vote on the best and worst combos.",
        "category": "Food"
    },
    {
        "content": "Each friend or couple brings a dish that reminds them of a moment in their love or life story. During dinner, everyone must explain what the dish represents — a first date, a trip, a family moment, etc.",
        "category": "Food"
    },

    # HOME

    {
        "content": "Build a real blanket fort big enough for two. Inside, create a “couple’s secret journal” — the first entry must be: “The story of how we met, told like a fairytale.” Take turns writing one sentence at a time.",
        "category": "Home"
    },
    {
        "content": "Turn off all electric lights. Light only candles or fairy lights. Create a cozy atmosphere with cushions or blankets, and watch a movie together.",
        "category": "Home"
    },
    {
        "content": "Design and execute a full DIY spa night, with hot towels or foot soap, a homemade face mask, soothing playlist, a 10-minute massage for each partner; you must set a “spa menu” with names for each experience.",
        "category": "Home"
    },
    {
        "content": "Each person chooses 3 objects, photos, or notes from their past and places them in a shoebox. Then, over warm drinks, reveal them one by one, telling the story behind each.",
        "category": "Home"
    },
    {
        "content": "Set a timer for 2 hours. During that time, complete these 5 mini cozy tasks together: cuddle with no phones, take one Polaroid or styled photo together, choose and frame a favorite quote to hang at home",
        "category": "Home"
    },
    {
        "content": "Each partner hides 5 tiny sexy notes around the house in creative or funny places. Clues are optional — but the notes must include one compliment, one memory, and one inside joke.",
        "category": "Home"
    },
    {
        "content": "Prepare a cocktail for the both of us; try one new cocktail each week!",
        "category": "Home"
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