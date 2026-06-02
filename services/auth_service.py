from datetime import datetime, timedelta
import secrets
from db.models.core_models import EmailVerificationToken
from sqlalchemy.orm import Session
from db.models.core_models import User
from core.security import hash_password, verify_password
from exceptions import (
    NotFoundError, 
    IncorrectPasswordError, 
    AlreadyExistsError, 
    WeakPasswordError
)

def register_user(db: Session, Username: str, Password: str):
    exists = db.query(User).filter(User.username == Username).first()
    if exists:
        raise AlreadyExistsError(
            message="User already exists")
    
    if len(Password) < 8:
        raise WeakPasswordError()
    
    hashed = hash_password(Password)
    new_user = User(username=Username, hashed_password=hashed)

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

