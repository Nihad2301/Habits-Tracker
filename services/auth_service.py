from datetime import datetime, timedelta
import secrets
from db.models.core_models.email_verification_token_model import EmailVerificationToken
from db.models.core_models.password_reset_token_model import PasswordResetToken
from services.email_service import send_email
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

def generate_token(
    db: Session, 
    user_id: int, 
    token_type: str, 
    expires_in_minutes: int | None = None
):
    """
    Generate a token for the specified user 
    and token type (email_verification or password_reset).
    """
    token_string = secrets.token_urlsafe(32)
    """
    If expires_at is provided, the token will expire at that time.
    Otherwise, it will expire in 24 hours.
    """
    expires = None
    if expires_in_minutes:
        expires = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    else:
        expires = datetime.utcnow() + timedelta(hours=24)

    if token_type == "email_verification":
        token = EmailVerificationToken(
            user_id=user_id,
            token=token_string,
            expires_at=expires
        )
    elif token_type == "password_reset":
        token = PasswordResetToken(
            user_id=user_id,
            token=token_string,
            expires_at=expires
        )
    else:
        raise ValueError(f"Invalid token type: {token_type}")

    db.add(token)
    db.commit()
    db.refresh(token)
    return token
    
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
    
    return user

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
    
    token = generate_token(db, user.id, "email_verification")    
    resend_email = send_email(
        email=user.email, 
        token=token.token, 
        email_type="verification"
    )
    return resend_email

def password_reset(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise NotFoundError(
            message="User not found"
        )
    
    token = generate_token(db, user.id, "password_reset")
    resend_email = send_email(
        email=user.email,
        token=token.token,
        email_type="password_reset"
    )
    return resend_email

def password_reset_verify(db: Session, token: str):
    password_reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()
    if not password_reset_token:
        raise NotFoundError(
            message="Password reset token not found"
        )
    
    if password_reset_token.is_used:
        raise AlreadyExistsError(
            message="Password reset token already used"
        )
    
    if password_reset_token.expires_at < datetime.utcnow():
        raise ExpiredTokenError(
            message="Password reset token expired"
        )
    
    password_reset_token.is_used = 1

    db.commit()
    db.refresh(password_reset_token)
    
    return password_reset_token  

def reset_password(db: Session, token: str, new_password: str):
    password_reset_token = password_reset_verify(db=db, token=token)
    user = db.query(User).filter(User.id == password_reset_token.user_id).first()
    if not user:
        raise NotFoundError(
            message="User not found"
        )
    if not new_password:
        raise ValueError(
            message="New password is required"
        )
    if len(new_password) < 8:
        raise WeakPasswordError()
        
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user      