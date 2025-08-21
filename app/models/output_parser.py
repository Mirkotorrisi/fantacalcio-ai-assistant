from typing import Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Response(BaseModel):
    player: str = Field(description="The player bought")
    team: str = Field(description="The team who bought the player")
    price: int = Field(None, description="The price of the player")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player": self.player,
            "team": self.team,
            "price": self.price,
        }

response_parser = PydanticOutputParser(pydantic_object=Response)
