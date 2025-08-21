
from fastapi import APIRouter, Query, HTTPException
from app.models.schema import InitSessionRequest, UpdateAuctionRequest, Roster
from app.services.create_new_session import create_new_session
from app.services.updater import process_auction_update
from app.core.redis_manager import get_rosters
import logging

router = APIRouter()

@router.post("/init_session")
def init_session(request: InitSessionRequest):
    """Initializes a new session with 8 teams and budget."""
    logging.info(f"Initializing session with teams: {request.team_names} and budget: {request.budget}")
    valid_team_counts = {6, 8, 10, 12}
    if len(request.team_names) not in valid_team_counts:
        raise HTTPException(status_code=400, detail=f"team_names must contain exactly {', '.join(map(str, valid_team_counts))} names.")
    session_id, roster = create_new_session(request.team_names, request.budget)
    logging.info(f"Session initialized with ID: {session_id}")
    return {"session_id": session_id, "roster": roster}

@router.post("/update_auction", response_model=Roster)
def update_auction(request: UpdateAuctionRequest):
    logging.info(f"Updating auction for session: {request.session_id}")
    """Updates the current rosters based on the user's prompt."""
    try:
        return process_auction_update(request.input_text, request.session_id, request.current)
    except Exception as e:
        logging.error(f"Error updating auction: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roster")
def get_user_roster(session_id: str = Query(...)):
    """Returns the current rosters."""
    return {"roster": get_rosters(session_id)}
