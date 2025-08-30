from app.configs.consts import ALL_ROLES
from app.core.redis_manager import get_rosters
from app.services.get_players_list import load_csv_players_list


def get_session_and_players(session_id: str, current_role: str):
    # Load the correct players csv file based on the current_role (goalkeepers, defenders, midfielders, forwards)
    session = get_rosters(session_id)
    if not session:
        raise ValueError("Session not found")
    if not current_role:
        current_role = session.get('current_role', 'goalkeepers')
    if current_role not in ALL_ROLES:
        raise ValueError("Invalid current_role role specified")
    players_list = load_csv_players_list(current_role)
    team_names = [team.get('name') for team in session.get('teams', [])]
    return session, players_list, team_names
