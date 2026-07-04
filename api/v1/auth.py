from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.core_models import User
from schemas.user_schema import UserBuild, UserRead, Login, PasswordResetConfirm
from schemas.response_schemas import SuccessResponse, MessageResponse
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
    user_profile_update
    )
from services.email_service import send_email

auth_router = APIRouter()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/register", response_model=SuccessResponse[UserRead], status_code=201)
def register(
    user: UserBuild, 
    db_session : Session = Depends(get_db), 
    expires_at: int | None = None
    ):
    registered_user = register_user(
        db=db_session, 
        Username=user.username,
        Password=user.password,
        Email=user.email
        ) 

    verification_token = generate_token(
        db=db_session, 
        user_id=registered_user.id,
        token_type="email_verification",
        expires_in_minutes=expires_at
        )
    send_email(
        email=registered_user.email, 
        token=verification_token.token,
        email_type="email_verification"
        )

    return SuccessResponse(
        message="User registered successfully",
        data=UserRead.model_validate(registered_user)
    )

@auth_router.post("/login", response_model=SuccessResponse[AuthResponse])
def login(logging_user: Login, session_db: Session = Depends(get_db)):
    user = login_user(
        db=session_db,
        Username=logging_user.username,
        Password=logging_user.password
        )
    
    access_token = make_access_token(data={"sub": str(user.id)})
    
    return SuccessResponse(
        message="User logged in successfully",
        data=AuthResponse(
            access_token=access_token,
            expires_in=1800
        )
    )

@auth_router.get("/verify-email", response_model=MessageResponse)
def email_verification(token: str, db_session: Session = Depends(get_db)):
    verify_email(token=token, db=db_session)
    return MessageResponse(message="Email verified successfully")

@auth_router.post("/resend-verification-email", response_model=MessageResponse)
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
    return MessageResponse(message="Verification email sent successfully")

@auth_router.post("/reset-password/request", response_model=MessageResponse)
def reset_password_request(
    password_reset_request_data: PasswordResetRequest,
    db_session: Session = Depends(get_db),
    expires_at: int | None = None
    ):
    password_reset_request(db=db_session, email=password_reset_request_data.email, expires_at=expires_at)
    return MessageResponse(message="Password reset email sent successfully")

@auth_router.post("/reset-password/confirm", response_model=MessageResponse)
def reset_password_confirm(
    password_reset_confirm_data: PasswordResetConfirm,
    db_session: Session = Depends(get_db)
    ):
    password_reset_confirm(
        db=db_session, 
        token=password_reset_confirm_data.token, 
        new_password=password_reset_confirm_data.new_password
    )
    
    return MessageResponse(
        message="Password reset successfully"
    )

@auth_router.post("/logout", response_model=SuccessResponse)
def logout(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
    ):
    user = logout_user(db=db_session, user_id=current_user.id)
    return SuccessResponse(
        message="User logged out successfully", 
        data={"last_logout": user.last_logout.isoformat()}
    )

@auth_router.put("/profile", response_model=SuccessResponse)
def update_profile(
    full_name: str | None = None,
    bio: str | None = None,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
    ):
    user = user_profile_update(
        db=db_session,
        user_id=current_user.id,
        full_name=full_name,
        bio=bio
    )
    return SuccessResponse(
        message="Profile updated successfully",
        data={"Full name": user.full_name, "Bio": user.bio}
    )



