from app.configs.consts import ALL_ROLES
from app.core.redis_manager import get_rosters
from app.services.get_players_list import load_csv_names_list


def get_session_and_players(session_id: str, current: str):
    # Load the correct players csv file based on the current (goalkeepers, defenders, midfielders, forwards)
    session = get_rosters(session_id)
    if not session:
        raise ValueError("Session not found")
    if not current:
        current = session.get('current', 'goalkeepers')
    if current not in ALL_ROLES:
        raise ValueError("Invalid current role specified")
    players_list = load_csv_names_list(current)
    team_names = [team.get('name') for team in session.get('teams', [])]
    return session, players_list, team_names
