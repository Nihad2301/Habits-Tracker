from fastapi import APIRouter, Depends
from db.models.core_models import User
from schemas.user_schema import UserRead, UserUpdate
from sqlalchemy.orm import Session
from db.session import get_db
from core.jwt_utils import get_current_user, require_verified_email
from services.user_service import (
    update, delete
    )    

user_router = APIRouter()

@user_router.get("/current-user", response_model=UserRead)
def get_current_user(user: User = Depends(get_current_user)):
    return user

@user_router.patch("/update-user", response_model=UserRead)
def update_user(new_one: UserUpdate, 
                user: User = Depends(require_verified_email), 
                db_session: Session = Depends(get_db)
                ):
    updated_data = new_one.model_dump(exclude_unset=True)

    updated_user = update(
        user=user, 
        db=db_session,
        **updated_data
        )
    
    return updated_user   
    
@user_router.delete("/delete-user", response_model=dict)
def delete_user(
    user: User = Depends(require_verified_email), 
    db_session: Session = Depends(get_db)
    ):
    return delete(user=user, db=db_session)