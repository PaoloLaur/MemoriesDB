import click
from flask.cli import with_appcontext
from models import db, Mission, Challenges, Scenario
from seed_missions import precreated_missions
from seed_challenges import precreated_challenges  
from seed_scenarios import precreated_scenarios
from datetime import datetime

# PRODUCTION NOTE:

"""
# In Railway dashboard -> your service -> Connect tab
export FLASK_APP=app_test.py

flask init-db
flask seed-all

# If you want to add new content later, just add new items to your seed files, then run:
flask seed-missions  # Only adds new ones!

"""

# DEVELOPMENT NOTE:

"""

# Initialize database
export FLASK_APP=app_test.py

flask init-db

# Seed everything first time
flask seed-all

# Add new content without deleting old
flask seed-missions
flask seed-challenges  
flask seed-scenarios

# Force recreate everything
flask seed-all --force

"""

@click.command()
@with_appcontext
def init_db():
    """
    Initialize database tables.

    RUN ONE IN LOCAL WHEN YOU START THE APP FOR THE FIRST TIME
    RUN ONLY ONE TIME IN PRODUCTION, WHEN YOU START THE APP FOR THE FIRST TIME

    
    """
    db.create_all()
    click.echo('Initialized database tables.')

# flask seed-all --force
@click.command()
@click.option('--force', is_flag=True, help='Force recreate all seeds (deletes existing)')
@with_appcontext
def seed_all(force): 
    """Seed all data (missions, challenges, scenarios)."""
    if force:
        click.echo('🗑️  Deleting existing seeds...')
        Mission.query.filter_by(is_precreated=True).delete()
        Challenges.query.filter_by(is_precreated=True).delete()
        Scenario.query.filter_by(is_precreated=True).delete()
        db.session.commit()
    
    seed_missions_data()
    seed_challenges_data()
    seed_scenarios_data()
    
    click.echo('✅ All seeding completed!')


@click.command()
@click.option('--force', is_flag=True, help='Force recreate missions')
@with_appcontext
def seed_missions_cmd(force):
    """Seed missions only."""
    if force:
        Mission.query.filter_by(is_precreated=True).delete()
        db.session.commit()
    
    seed_missions_data()


@click.command()
@click.option('--force', is_flag=True, help='Force recreate challenges')
@with_appcontext
def seed_challenges_cmd(force):
    """Seed challenges only."""
    if force:
        Challenges.query.filter_by(is_precreated=True).delete()
        db.session.commit()
    
    seed_challenges_data()


@click.command()
@click.option('--force', is_flag=True, help='Force recreate scenarios')
@with_appcontext
def seed_scenarios_cmd(force):
    """Seed scenarios only."""
    if force:
        Scenario.query.filter_by(is_precreated=True).delete()
        db.session.commit()
    
    seed_scenarios_data()


def seed_missions_data():
    """Smart seeding for missions - only adds new ones."""
    existing_contents = {m.content for m in Mission.query.filter_by(is_precreated=True).all()}
    new_missions = []
    
    for mission_data in precreated_missions:
        if mission_data["content"] not in existing_contents:
            new_missions.append(Mission(
                content=mission_data["content"],
                category=mission_data["category"],
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_missions:
        db.session.bulk_save_objects(new_missions)
        db.session.commit()
        click.echo(f'✅ Added {len(new_missions)} new missions')
    else:
        click.echo('ℹ️  No new missions to add')


def seed_challenges_data():
    """Smart seeding for challenges - only adds new ones."""
    existing_contents = {c.content for c in Challenges.query.filter_by(is_precreated=True).all()}
    new_challenges = []
    
    for challenge_data in precreated_challenges:
        if challenge_data["content"] not in existing_contents:
            new_challenges.append(Challenges(
                content=challenge_data["content"],
                category=challenge_data["category"],
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_challenges:
        db.session.bulk_save_objects(new_challenges)
        db.session.commit()
        click.echo(f'✅ Added {len(new_challenges)} new challenges')
    else:
        click.echo('ℹ️  No new challenges to add')


def seed_scenarios_data():
    """Smart seeding for scenarios - only adds new ones."""
    existing_prompts = {s.prompt for s in Scenario.query.filter_by(is_precreated=True).all()}
    new_scenarios = []
    
    for scenario_data in precreated_scenarios:
        if scenario_data["prompt"] not in existing_prompts:
            new_scenarios.append(Scenario(
                setting=scenario_data["setting"],
                roles=scenario_data["roles"],
                prompt=scenario_data["prompt"],
                time=scenario_data.get("time"),
                is_precreated=True,
                created_at=datetime.utcnow()
            ))
    
    if new_scenarios:
        db.session.bulk_save_objects(new_scenarios)
        db.session.commit()
        click.echo(f'✅ Added {len(new_scenarios)} new scenarios')
    else:
        click.echo('ℹ️  No new scenarios to add')


def register_commands(app):
    """Register all commands with the app."""
    app.cli.add_command(init_db, name='init-db')
    app.cli.add_command(seed_all, name='seed-all')
    app.cli.add_command(seed_missions_cmd, name='seed-missions')
    app.cli.add_command(seed_challenges_cmd, name='seed-challenges') 
    app.cli.add_command(seed_scenarios_cmd, name='seed-scenarios')