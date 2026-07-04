import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from jose import JWTError
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(habit_router)
app.include_router(completion_router)
app.include_router(analytics_router)