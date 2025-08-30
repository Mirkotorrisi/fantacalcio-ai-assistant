from pydantic import BaseModel


class DeletePlayerRequest(BaseModel):
    session_id: str
    current_role: str
    player_name: str
    team_name: str


class UpdateAuctionRequest(BaseModel):
    input_text: str
    session_id: str
    current_role: str

class InitSessionRequest(BaseModel):
    team_names: list[str]
    budget: int = 500


class Player(BaseModel):
    name: str
    price: int
    id: str
    team: str

class PlayersByRole(BaseModel):
    goalkeepers: list[Player]
    defenders: list[Player]
    midfielders: list[Player]
    forwards: list[Player]

class Team(BaseModel):
    id: int
    name: str
    budget: int
    players: PlayersByRole

class Roster(BaseModel):
    id: int
    lastUpdate: str
    current_role: str
    teams: list[Team]
    initialBudget: int | None = None