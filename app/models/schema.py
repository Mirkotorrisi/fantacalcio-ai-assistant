from pydantic import BaseModel


class UpdateAuctionRequest(BaseModel):
    input_text: str
    session_id: str
    current: str


class InitSessionRequest(BaseModel):
    team_names: list[str]
    budget: int = 500


class Player(BaseModel):
    name: str
    price: int

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
    current: str
    teams: list[Team]