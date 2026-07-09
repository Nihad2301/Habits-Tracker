from fastapi import Depends
from jose import jwt
import logging
from config import settings
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.models.core_models import User
from exceptions import (
    ExpiredTokenError, 
    InvalidTokenError, 
    NotAuthorizedError, 
    EmailNotVerifiedError
    )
from db.session import get_db

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

def make_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta        
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])   
        user_id: str = payload.get("sub")
        # protects against future token structure changes
        if user_id is None:
            raise InvalidTokenError()   
        return int(user_id)
    except ExpiredSignatureError:
        raise ExpiredTokenError()
    except JWTError:
        raise InvalidTokenError()

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise NotAuthorizedError()
    try:
        user_id = verify_token(credentials.credentials)
    except (ExpiredTokenError, InvalidTokenError) as e:
        logger.warning(f"Token verification failed: {type(e).__name__}")
        raise NotAuthorizedError()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise NotAuthorizedError()

    return user

def require_verified_email(user: User = Depends(get_current_user)):
    if not user.is_verified:
        raise EmailNotVerifiedError()
    return user
