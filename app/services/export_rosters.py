from io import StringIO

from fastapi.responses import StreamingResponse
from app.configs.consts import ALL_ROLES
from app.models.schema import Roster


def export_roster(roster: Roster):
    '''
    This function takes as input the Roster object and converts it to a CSV format.
    The CSV format will follow this path:
    $,$,$ <- this is a separator that divides each team
    {Team Name},{player id},{player price}
    '''
    csv_data = ""
    for team in roster.teams:
        csv_data += f"$,$,$\n"
        for role in ALL_ROLES:
            players = team.players.__getattribute__(role)
            for player in players:
                csv_data += f"{team.name},{player.id},{player.price}\n"

    buffer = StringIO()
    buffer.write(csv_data)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rosters.csv"}
    )
