from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.jwt_utils import get_current_user
from services.habit_completion_service import (
    mark_completed_habit, 
    unmark_completed_habit,
    show_marked_habits
    )
from db.models.core_models import User

completion_router = APIRouter()


@completion_router.post("/habits/{habit_id}/complete", status_code=201)
def mark_habit_as_completed(
    habit_id: int, 
    db_session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    completed_habit = mark_completed_habit(
        habit_id=habit_id,
        db=db_session,
        user=current_user
    )

    return completed_habit


@completion_router.delete("/habits/{habit_id}/complete", status_code=201)
def unmark_habit(
    habit_id: int,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    return unmark_completed_habit(
        db=db_session, 
        habit_id=habit_id, 
        user=current_user
        )


@completion_router.get("/all-habits-complete")
def marked_habits(
        db_session: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
        ):
    return show_marked_habits(db=db_session, user=current_user)


