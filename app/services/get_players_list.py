import csv
from typing import List

from app.configs.consts import ALL_ROLES
from app.models.schema import Player, Roster

def load_csv_players_list(current_role) -> List[Player]:
    csv_file_path = f'data/{current_role}.csv'
    # Read players from CSV using built-in csv module
    players_list = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players_list.append({
                "id": row['Id'],
                "name": row['Nome'],
                "price": row['Qt.A'],
                "team": row['Squadra']
            })
    return players_list


def load_available_players_list(rosters: Roster):
    # Collect all player names from all teams and roles
    taken_players = set()
    for team in rosters.teams:
        for role in ALL_ROLES:
            players = team.players.__getattribute__(role)
            for player in players:
                taken_players.add(player.name)
    
    all_players = {}
    for role in ALL_ROLES:
        all_players[role] = load_csv_players_list(role)
        # Filter out players that are already in the rosters
        all_players[role] = [player for player in all_players[role] if player['name'] not in taken_players]
    return all_players