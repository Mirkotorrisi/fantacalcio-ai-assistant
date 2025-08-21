from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.routes import router
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()
app.include_router(router)
