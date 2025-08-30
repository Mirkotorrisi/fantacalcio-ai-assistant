
from typing import List
from app.services.nlp_parser import parse_auction_text
from app.core.redis_manager import save_rosters
from app.models.schema import Player, Roster
import logging

players_slots = {
    "goalkeepers": 3,
    "defenders": 8,
    "midfielders": 8,
    "forwards": 6
}

def process_auction_update(team_names: List[str], players_list: List[Player], session: Roster, input_text: str, session_id: str, current_role: str) -> Roster:
    logging.info(f"start parsing: {input_text}, {team_names}, {current_role} players: {len(players_list)}")
    players_names = [player['name'] for player in players_list]
    parsed = parse_auction_text(input_text, players_names, team_names)
    logging.info(f"Parsed auction: {parsed}")
    # Here we check if the player was already present in any team, if so, raise an error
    if any(parsed.player == p['name'] for team in session['teams'] for p in team['players'][current_role]):
        raise ValueError(f"Player {parsed.player} is already assigned to a team")
    # Find team in the roster json
    team = next((item for item in session['teams'] if item["name"] == parsed.team), None)
    if not team:
        raise ValueError("Team not found in roster")
    # Check if the team can afford the new player
    if team['budget'] < parsed.price:
        raise ValueError(f"Team {team['name']} cannot afford {parsed.player}")
    # Check if the team has reached the maximum number of players
    if len(team['players'][current_role]) >= players_slots[current_role]:
        raise ValueError(f"Team {team['name']} has reached the maximum number of {current_role} players")
    
    # Find the player by name in the list
    player = next((p for p in players_list if p['name'] == parsed.player), None)

    if not player:
        raise ValueError(f"Player {parsed.player} not found in players list")
    team['players'][current_role].append({
        "id": player['id'],
        "name": player['name'],
        "price": parsed.price, # here we store the parsed price instead of the list price
        "team": player['team']
    })
    team['budget'] -= parsed.price
    # Update the last modified time
    import datetime
    session['lastUpdate'] = datetime.datetime.now().isoformat()
    # Update the current_role role
    session['current_role'] = current_role
    save_rosters(session_id, session)

    return Roster(
        id=session['id'],
        lastUpdate=session['lastUpdate'],
        current_role=session['current_role'],
        teams=session['teams'],
        initialBudget=session['initialBudget']
    )
