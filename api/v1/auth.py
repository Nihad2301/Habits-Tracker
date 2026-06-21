from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user_schema import UserBuild, UserRead, Login
from core.jwt_utils import make_access_token
from services.auth_service import (
    register_user, 
    login_user, 
    generate_verification_token, 
    verify_email,
    resend_verification
    )
from services.email_service import send_verification_email

auth_router = APIRouter()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/register", response_model=UserRead, status_code=201)
def register(user: UserBuild, db_session : Session = Depends(get_db)):
    registering_user = register_user(
        db=db_session, 
        Username=user.username,
        Password=user.password,
        Email=user.email
        ) 

    verification_token = generate_verification_token(db=db_session, user_id=registering_user.id)
    send_email = send_verification_email(email=registering_user.email, token=verification_token.token)

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

@auth_router.get("/verify-email")
def email_verification(token: str, db_session: Session = Depends(get_db)):
    verify_email(token=token, db=db_session)
    return {"message": "Email verified successfully"}

@auth_router.post("/resend-verification-email")
def resend_verification_email(email: str, db_session: Session = Depends(get_db)):
    resend_verification(db=db_session, email=email)
    return {"message": "Verification email sent successfully"}
