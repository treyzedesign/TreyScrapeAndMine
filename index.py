import os
from fastapi import FastAPI, Request
from config.database import Base, engine  # Import Base and engine
from config.db_setup import init_db
from route.lotto import router as winning_numbers_router  # Import your router

import logging
from fastapi.templating import Jinja2Templates
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Database connection successfully established.")

@app.get("/")
async def home(request: Request):
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000") 
    return templates.TemplateResponse("index.html", {"request": request, "name": "LottoWinningNumbers"})

app.include_router(winning_numbers_router, prefix="/api")