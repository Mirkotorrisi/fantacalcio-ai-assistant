
from fastapi import APIRouter, File, Form, Query, HTTPException, UploadFile
from app.models.schema import InitSessionRequest, UpdateAuctionRequest, Roster
from app.services.export_rosters import export_roster
from app.services.get_session_and_players import get_session_and_players
from app.services.transcribe_audio import transcribe_audio
from app.services.create_new_session import create_new_session
from app.services.get_players_list import load_available_players_list
from app.services.updater import process_auction_update
from app.core.redis_manager import get_rosters
import logging

router = APIRouter()

@router.post("/init-session")
def init_session(request: InitSessionRequest):
    """Initializes a new session with 8 teams and budget."""
    try:
        logging.info(f"Initializing session with teams: {request.team_names} and budget: {request.budget}")
        valid_team_counts = {6, 8, 10, 12}
        if len(request.team_names) not in valid_team_counts:
            raise HTTPException(status_code=400, detail=f"team_names must contain exactly {', '.join(map(str, valid_team_counts))} names.")
        session_id, roster = create_new_session(request.team_names, request.budget)
        logging.info(f"Session initialized with ID: {session_id}")
        return {"session_id": session_id, "roster": roster}
    except Exception as e:
        logging.error(f"Error initializing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-auction", response_model=Roster)
def update_auction(request: UpdateAuctionRequest):
    logging.info(f"Updating auction for session: {request.session_id}")
    """Updates the current_role rosters based on the user's prompt."""
    try:
        session, players_list, team_names = get_session_and_players(request.session_id, request.current_role)
        return process_auction_update(team_names, players_list, session, request.input_text, request.session_id, request.current_role)
    except Exception as e:
        logging.error(f"Error updating auction: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-auction-transcription", response_model=Roster)
async def update_auction_transcription(file: UploadFile = File(...), session_id: str = Form(...), current_role: str = Form(...)):
    """
    Receives an audio file from the frontend, sends it to the Whisper API,
    and returns the transcription.
    """
    logging.info(f"Transcribing audio for session: {session_id}")
    try:
        session, players_list, team_names = get_session_and_players(session_id, current_role)
        transcribed_text = await transcribe_audio(team_names, players_list,file)
        logging.info(f"Transcribed text for session {session_id}: {transcribed_text}")
        return process_auction_update(team_names, players_list, session, transcribed_text, session_id, current_role)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rosters")
def get_user_rosters(session_id: str = Query(...)):
    """Returns the current_role rosters."""
    try: 
        rosters = get_rosters(session_id)
        return rosters
    except Exception as e:
        logging.error(f"Error fetching rosters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/players-list")
def get_user_players_list(session_id: str = Query(...)):
    """Returns the current_role players list."""
    try:
        logging.info(f"Fetching players list for session: {session_id}")
        rosters = get_rosters(session_id)
        players_list = load_available_players_list(Roster(**rosters))
        return players_list
    except Exception as e:
        logging.error(f"Error fetching players list: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/export-rosters")
def export_user_rosters(session_id: str = Query(...)):
    """Exports the current_role rosters."""
    try:
        logging.info(f"Exporting rosters for session: {session_id}")
        rosters = get_rosters(session_id)
        return export_roster(Roster(**rosters))
    except Exception as e:
        logging.error(f"Error exporting rosters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
