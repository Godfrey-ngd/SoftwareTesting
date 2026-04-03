from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.api import router as api_router
from app.routes.web import router as web_router

load_dotenv()

app = FastAPI(title="LLM Black-Box Testing Tool", version="0.1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(web_router)
app.include_router(api_router, prefix="/api")
