from sqlalchemy.orm import Session
from db.models.core_models import User
from core.security import hash_password
from exceptions import NotFoundError
from core.jwt_utils import get_current_user


def show_all_users(db: Session):
    all_users = db.query(User).all()

    if not all_users:
        raise NotFoundError()
    
    return all_users


def update(user: User, db: Session, username=None, password=None):     
    current_user = db.query(User).filter(User.id == user.id).first()
     
    if isinstance(username, str):        
        current_user.username = username
    if isinstance(password, str):
        hashed = hash_password(password)
        current_user.hashed_password = hashed

    db.commit()
    db.refresh(current_user)    

    return current_user 
 
                                                
def delete(user: User, db: Session):
    user = db.query(User).filter(User.id == user.id).first()

    if not user:
        raise NotFoundError()

    db.delete(user)
    db.commit()

    return {"message": f"{user.username} is deleted"}      


