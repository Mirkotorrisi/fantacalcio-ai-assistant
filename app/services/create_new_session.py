import uuid

from app.core.redis_manager import save_rosters
from app.models.schema import PlayersByRole, Roster, Team

def create_new_session(team_names: list[str], budget: int = 500):
    session_id = str(uuid.uuid4())
    teams = []
    for name in team_names:
        team = Team(
            id=uuid.uuid4().int >> 96,
            name=name,
            budget=budget,
            players=PlayersByRole(goalkeepers=[], defenders=[], midfielders=[], forwards=[])
        )
        teams.append(team)
    roster = Roster(
        id=uuid.uuid4().int >> 96,
        lastUpdate="",
        current="goalkeepers",
        teams=teams
    )
    save_rosters(session_id, roster.model_dump())
    return session_id, roster