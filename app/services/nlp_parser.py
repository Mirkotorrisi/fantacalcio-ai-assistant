from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from app.models.output_parser import response_parser


class AuctionParse(BaseModel):
    player: str = Field(...)
    team: str = Field(...)
    price: int = Field(...)

def parse_auction_text(input_text: str, players_names: list, team_names: list) -> dict:

    parse_auction_template = '''
    Given a human prompt about a player to buy, and a team who bought it, 
    you must extract the player name, team name, and price from the prompt.

    If you can't recognize a team from the prompt, you must return it as 'error'.
    You should never guess the team.

    Human prompt: {prompt}

    List of players: {players_names}

    List of teams: {team_names}

    \n{format_instructions}
    '''

    get_sign_prompt_template = PromptTemplate(input_variables=['players_names', 'team_names'], 
                                             template=parse_auction_template,
                                            partial_variables={'format_instructions': response_parser.get_format_instructions()})

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")


    chain = get_sign_prompt_template | llm | response_parser

    res = chain.invoke(input={'prompt': input_text, 'players_names': players_names, 'team_names': team_names })
    print(res)

    # Validation
    if res.player not in players_names:
        raise ValueError(f"Player '{res.player}' not found in the list.")
    if res.team not in team_names:
        raise ValueError(f"Can't find a valid team from your input.")
    return res
