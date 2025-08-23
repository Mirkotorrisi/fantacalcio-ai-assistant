from typing import List
from fastapi import UploadFile, File
from google.cloud import speech
import os, json
from google.cloud import speech
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

creds_info = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
creds = service_account.Credentials.from_service_account_info(creds_info)
client = speech.SpeechClient(credentials=creds)

async def transcribe_audio(team_names: List[str], players_list: List[str], file: UploadFile = File(...)) -> str:
    phrase_hints = players_list + team_names
    audio_content = await file.read()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="it-IT",
        speech_contexts=[speech.SpeechContext(phrases=phrase_hints)]
    )
    response = client.recognize(config=config, audio=audio)
    results = [result.alternatives[0].transcript for result in response.results]
    return " ".join(results)


