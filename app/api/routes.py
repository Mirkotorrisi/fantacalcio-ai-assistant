
from fastapi import APIRouter, File, Form, Query, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from app.models.schema import DeletePlayerRequest, InitSessionRequest, UpdateAuctionRequest, Roster
from app.services.delete_player import delete_player_from_roster
from app.services.export_rosters import export_roster
from app.services.get_session_and_players import get_session_and_players
from app.services.transcribe_audio import transcribe_audio
from app.services.create_new_session import create_new_session
from app.services.get_players_list import load_available_players_list
from app.services.updater import process_auction_update
from app.core.redis_manager import get_rosters
from app.core.connection_manager import manager
import logging

router = APIRouter()

@router.post("/init-session")
async def init_session(request: InitSessionRequest):
    """Initializes a new session with 8 teams and budget."""
    try:
        logging.info(f"Initializing session with teams: {request.team_names} and budget: {request.budget}")
        valid_team_counts = {6, 8, 10, 12}
        if len(request.team_names) not in valid_team_counts:
            raise HTTPException(status_code=400, detail=f"team_names must contain exactly {', '.join(map(str, valid_team_counts))} names.")
        session_id, roster = create_new_session(request.team_names, request.budget)
        logging.info(f"Session initialized with ID: {session_id}")
        # broadcast initial roster (ignore errors)
        try:
            await manager.broadcast_roster(session_id, roster.model_dump())
        except Exception as e:
            logging.warning(f"Broadcast failed on init-session: {e}")
        return {"session_id": session_id, "roster": roster}
    except Exception as e:
        logging.error(f"Error initializing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-auction", response_model=Roster)
async def update_auction(request: UpdateAuctionRequest):
    logging.info(f"Updating auction for session: {request.session_id}")
    """Updates the current_role rosters based on the user's prompt."""
    try:
        session, players_list, team_names = get_session_and_players(request.session_id, request.current_role)
        roster = process_auction_update(team_names, players_list, session, request.input_text, request.session_id, request.current_role)
        try:
            await manager.broadcast_roster(request.session_id, roster.model_dump())
        except Exception as e:
            logging.warning(f"Broadcast failed on update-auction: {e}")
        return roster
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
        roster = process_auction_update(team_names, players_list, session, transcribed_text, session_id, current_role)
        try:
            await manager.broadcast_roster(session_id, roster.model_dump())
        except Exception as e:
            logging.warning(f"Broadcast failed on update-auction-transcription: {e}")
        return roster

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
    
@router.post("/delete-player")
async def delete_player(request: DeletePlayerRequest):
    """Delete a player from a roster and refunds the paid price to the team"""
    try:
        logging.info(f"Deleting the player {request.player_name} from team {request.team_name}")
        rosters = get_rosters(request.session_id)
        updated_rosters = delete_player_from_roster(rosters, request)
        try:
            await manager.broadcast_roster(request.session_id, updated_rosters)
        except Exception as e:
            logging.warning(f"Broadcast failed on delete-player: {e}")
        return Roster(**updated_rosters)
    except Exception as e:
        logging.error(f"Error deleting player: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    print(session_id)
    """WebSocket endpoint: client connects providing a session_id query param and receives roster updates."""
    await manager.connect(session_id, websocket)
    # On connect, immediately send current roster (if any)
    roster = get_rosters(session_id)
    print("thisistheroster", roster)
    if roster:
        await manager.send_personal_roster(websocket, roster)
    try:
        # Keep the connection open. We don't expect meaningful messages from client yet.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception:
        # Any other exception -> ensure disconnection cleanup
        manager.disconnect(session_id, websocket)
