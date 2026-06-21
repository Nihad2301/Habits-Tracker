from datetime import datetime, timedelta
import secrets
from db.models.core_models.email_verification_token_model import EmailVerificationToken
from email_service import send_verification_email
from sqlalchemy.orm import Session
from db.models.core_models import User
from core.security import hash_password, verify_password
from exceptions import (
    NotFoundError, 
    IncorrectPasswordError, 
    AlreadyExistsError, 
    WeakPasswordError,
    ExpiredTokenError
)

def register_user(db: Session, Username: str, Password: str, Email: str):
    exists = db.query(User).filter(User.username == Username).first()
    if exists:
        raise AlreadyExistsError(
            message="User already exists")
    
    if len(Password) < 8:
        raise WeakPasswordError()
    
    hashed = hash_password(Password)
    new_user = User(
        username=Username, 
        hashed_password=hashed, 
        email=Email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, Username, Password):
    user = db.query(User).filter(User.username == Username).first()
    if not user:
        raise NotFoundError(
            message="User is not found"
        )
    
    verified = verify_password(Password, user.hashed_password)
    if not verified:
        raise IncorrectPasswordError()

    return user

def generate_verification_token(db: Session, user_id: int):
    token = secrets.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    verification_token = EmailVerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(verification_token)
    db.commit()
    db.refresh(verification_token)
    
    return verification_token

def verify_email(db: Session, token: str):
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()
    if not verification_token:
        raise NotFoundError(
            message="Verification token not found"
        )
    
    if verification_token.is_used:
        raise AlreadyExistsError(
            message="Verification token already used"
        )
    
    if verification_token.expires_at < datetime.utcnow():
        raise ExpiredTokenError(
            message="Verification token expired"
        )
    
    verification_token.is_used = 1

    user = db.query(User).filter(User.id == verification_token.user_id).first()
    user.is_verified = True

    db.commit()
    db.refresh(verification_token)
    db.refresh(user)
    
    return verification_token

def resend_verification(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise NotFoundError(
            message="User not found"
        )
    if user.is_verified:
        raise AlreadyExistsError(
            message="User already verified"
        )
    
    token = generate_verification_token(db, user.id)    
    resend_email = send_verification_email(email=user.email, token=token.token)
    return resend_email

