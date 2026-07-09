from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.core_models import User
from schemas.user_schema import (
    UserBuild, 
    UserRead, 
    Login, 
    PasswordResetRequest, 
    PasswordResetConfirm, 
    ResendVerificationEmail
)
from schemas.response_schemas import SuccessResponse, MessageResponse
from core.jwt_utils import make_access_token, get_current_user
from services.auth_service import (
    register_user, 
    login_user, 
    verify_email,
    resend_verification,
    password_reset_request,
    password_reset_confirm,
    logout_user,
    user_profile_update
    )

auth_router = APIRouter()

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/register", response_model=SuccessResponse[UserRead], status_code=201)
def register(
    user: UserBuild, 
    db_session : Session = Depends(get_db)
    ):
    registered_user = register_user(
        db=db_session, 
        username=user.username,
        password=user.password,
        email=user.email
        )

    return SuccessResponse(
        message="User registered successfully",
        data=UserRead.model_validate(registered_user)
    )

@auth_router.post("/login", response_model=SuccessResponse[AuthResponse])
def login(logging_user: Login, session_db: Session = Depends(get_db)):
    user = login_user(
        db=session_db,
        username=logging_user.username,
        password=logging_user.password
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
    email_data: ResendVerificationEmail,
    db_session: Session = Depends(get_db)
    ):
    resend_verification(db=db_session, email=email_data.email)
    return MessageResponse(message="if an account exists, we sent a link")

@auth_router.post("/reset-password/request", response_model=MessageResponse)
def reset_password_request(
    password_reset_request_data: PasswordResetRequest,
    db_session: Session = Depends(get_db),
    expires_at: int | None = Query(
        default=None, 
        description="Expiration time in minutes"
        )
    ):
    password_reset_request(db=db_session, email=password_reset_request_data.email, expires_at=expires_at)
    return MessageResponse(message="if an account exists, we sent a link")

@auth_router.post("/reset-password/confirm", response_model=SuccessResponse[UserRead])
def reset_password_confirm(
    password_reset_confirm_data: PasswordResetConfirm,
    db_session: Session = Depends(get_db)
    ):
    user = password_reset_confirm(
        db=db_session, 
        token=password_reset_confirm_data.token, 
        new_password=password_reset_confirm_data.new_password
    )
    
    return SuccessResponse(
        message="Password reset successfully",
        data=UserRead.model_validate(user)
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



