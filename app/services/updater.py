
from app.services.nlp_parser import parse_auction_text
from app.core.redis_manager import get_rosters, save_rosters
from app.models.schema import Roster
import pandas as pd
import logging

players_slots = {
    "goalkeepers": 3,
    "defenders": 8,
    "midfielders": 8,
    "forwards": 6
}

def process_auction_update(input_text: str, session_id: str, current: str) -> Roster:
    session = get_rosters(session_id)
    if not session:
        raise ValueError("Session not found")
    if not current:
        current = session.get('current', 'goalkeepers')
    if current not in ['goalkeepers', 'defenders', 'midfielders', 'forwards']:
        raise ValueError("Invalid current role specified")
    # Load the correct players csv file based on the current (goalkeepers, defenders, midfielders, forwards)
    csv_file_path = f'data/{current}.csv'
    players_df = pd.read_csv(csv_file_path)
    team_names = [team.get('name') for team in session.get('teams', [])]
    logging.info(f"start parsing: {input_text}, {team_names}, {current} players: {players_df['Nome'].count()}")
    parsed = parse_auction_text(input_text, players_df, team_names)
    roster = get_rosters(session_id)
    logging.info(f"Parsed auction: {parsed}")
    # Here we check if the player was already present in any team, if so, raise an error
    if any(parsed.player == p['name'] for team in roster['teams'] for p in team['players'][current]):
        raise ValueError(f"Player {parsed.player} is already assigned to a team")
    # Find team in the roster json
    team = next((item for item in roster['teams'] if item["name"] == parsed.team), None)
    if not team:
        raise ValueError("Team not found in roster")
    # Check if the team can afford the new player
    if team['budget'] < parsed.price:
        raise ValueError(f"Team {team['name']} cannot afford {parsed.player}")
    # Check if the team has reached the maximum number of players
    if len(team['players'][current]) >= players_slots[current]:
        raise ValueError(f"Team {team['name']} has reached the maximum number of {current} players")
    team['players'][current].append({"name": parsed.player, "price": parsed.price})
    team['budget'] -= parsed.price
    # Update the last modified time
    roster['lastUpdate'] = pd.Timestamp.now().isoformat()
    # Update the current role
    roster['current'] = current
    save_rosters(session_id, roster)

    return Roster(
        id=roster['id'],
        lastUpdate=roster['lastUpdate'],
        current=roster['current'],
        teams=roster['teams']
    )
