from app.core.redis_manager import save_rosters
from app.models.schema import DeletePlayerRequest, Roster

def delete_player_from_roster(rosters: Roster, request: DeletePlayerRequest):
    '''Here we find the player using its team name, player name and role and we remove if from the list'''
    # Find the team to remove the player from
    team = next((t for t in rosters['teams'] if t['name'].lower() == request.team_name.lower()), None)
    if team:
        # Find the player to remove
        player = next((p for p in team['players'][request.current_role] if p['name'].lower() == request.player_name.lower()), None)
        if player:
            team['players'][request.current_role].remove(player)
            # Refund the price to the team budget
            team['budget'] += player['price']
    # Save the updated rosters
        # Update the last modified time
    import datetime
    rosters['lastUpdate'] = datetime.datetime.now().isoformat()
    save_rosters(request.session_id, rosters)
    return rosters