from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user_schema import UserBuild, UserRead, Login
from core.jwt_utils import make_access_token
from services.auth_service import register_user, login_user

auth_router = APIRouter()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/register", response_model=UserRead)
def register(user: UserBuild, db_session : Session = Depends(get_db)):
    registering_user = register_user(
        db=db_session, 
        Username=user.username,
        Password=user.password
        ) 

    return registering_user

@auth_router.post("/login", response_model=AuthResponse)
def login(logging_user: Login, session_db: Session = Depends(get_db)):
    user = login_user(
        db=session_db,
        Username=logging_user.username,
        Password=logging_user.password
        )
    
    access_token = make_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        expires_in=1800
        )