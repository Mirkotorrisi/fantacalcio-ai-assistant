import csv

from app.configs.consts import ALL_ROLES
from app.models.schema import Roster

def load_csv_names_list(current):
    csv_file_path = f'data/{current}.csv'
    # Read players from CSV using built-in csv module
    players_list = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players_list.append(row['Nome'])
    return players_list

def load_csv_names_and_price_list(current):
    csv_file_path = f'data/{current}.csv'
    # Read players from CSV using built-in csv module
    players_list = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players_list.append({"name":row['Nome'], "price": row['Qt.A']})
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
        all_players[role] = load_csv_names_and_price_list(role)
        # Filter out players that are already in the rosters
        all_players[role] = [player for player in all_players[role] if player['name'] not in taken_players]
    return all_players