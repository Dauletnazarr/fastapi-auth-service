from fastapi import FastAPI
from app.logging_config import setup_uvicorn_logger
from .config import settings
from .database import engine, Base
from .routers import auth as auth_router

setup_uvicorn_logger(host="127.0.0.1", port=8000)

if settings.app_debug:
    Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(auth_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
