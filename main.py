import os
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.session import get_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from jose import JWTError
import redis
from config import settings
from exceptions import (
    AppException,
    custom_exception_handler,
    validation_exception_handler,
    jwt_exception_handler
)
from api.v1.auth import auth_router
from api.v1.users import user_router
from api.v1.habits import habit_router
from api.v1.habits_completion import completion_router
from api.v1.habit_analytics import analytics_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

app = FastAPI(
    title="Habits Tracker API",
    description="A backend API for tracking daily habits, streaks, and completion analytics. Built with FastAPI, PostgreSQL, and JWT authentication.",
    version="1.0.0",
    contact={
        "name": "Nihad",
        "url": "https://github.com/Nihad2301/Habits-Tracker",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    redis_status = "connected"
    
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    
    try:
        redis_client.ping()
    except Exception:
        redis_status = "disconnected"
    
    if db_status == "disconnected" or redis_status == "disconnected":
        raise HTTPException(
            status_code=503, 
            detail={"status": "error", "database": db_status, "redis": redis_status}
        )
    
    return {"status": "ok", "database": db_status, "redis": redis_status}

app.add_exception_handler(AppException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)

app.include_router(auth_router, tags=["Auth"])
app.include_router(user_router, tags=["Users"])
app.include_router(habit_router, tags=["Habits"])
app.include_router(completion_router, tags=["Habit Completions"])
app.include_router(analytics_router, tags=["Analytics"])