from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.core_models import User
from schemas.user_schema import UserBuild, UserRead, Login
from core.jwt_utils import make_access_token, get_current_user
from services.auth_service import (
    register_user, 
    login_user, 
    generate_token, 
    verify_email,
    resend_verification,
    password_reset_request,
    password_reset_confirm,
    logout_user,
    user_profile_update,
    update_user_preferences
    )
from services.email_service import send_email

auth_router = APIRouter()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/register", response_model=UserRead, status_code=201)
def register(
    user: UserBuild, 
    db_session : Session = Depends(get_db), 
    expires_at: int | None = None
    ):
    registering_user = register_user(
        db=db_session, 
        Username=user.username,
        Password=user.password,
        Email=user.email
        ) 

    verification_token = generate_token(
        db=db_session, 
        user_id=registering_user.id,
        token_type="email_verification",
        expires_in_minutes=expires_at
        )
    send_email(
        email=registering_user.email, 
        token=verification_token.token,
        email_type="email_verification"
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

@auth_router.get("/verify-email")
def email_verification(token: str, db_session: Session = Depends(get_db)):
    return verify_email(token=token, db=db_session)

@auth_router.post("/resend-verification-email")
def resend_verification_email(
    email: str = None, 
    db_session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    if current_user:
        email = current_user.email
     
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    resend_verification(db=db_session, email=email)
    return {"message": "Verification email sent successfully"}

@auth_router.post("/reset-password/request")
def reset_password_request(
    email: str = None, 
    db_session: Session = Depends(get_db),
    expires_at: int | None = None
    ):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    password_reset_request(db=db_session, email=email, expires_at=expires_at)
    return {"message": "Password reset email sent successfully"}

@auth_router.post("/reset-password/confirm")
def reset_password_confirm(
    token: str,
    new_password: str,
    db_session: Session = Depends(get_db)
    ):
    password_reset_confirm(
        db=db_session, 
        token=token, 
        new_password=new_password
    )
    return {"message": "Password reset successfully"}

@auth_router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
    ):
    return logout_user(db=db_session, user_id=current_user.id)

@auth_router.put("/profile")
def update_profile(
    full_name: str | None = None,
    bio: str | None = None,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
    ):
    return user_profile_update(
        db=db_session,
        user_id=current_user.id,
        full_name=full_name,
        bio=bio
        )

@auth_router.put("/preferences")
def update_preferences(
    language: str | None = None,
    theme: str | None = None,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
    ):
    return update_user_preferences(
        db=db_session,
        user_id=current_user.id,
        language=language,
        theme=theme
        )

