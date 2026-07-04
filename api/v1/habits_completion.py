from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.jwt_utils import require_verified_email
from services.habit_completion_service import (
    mark_completed_habit, 
    unmark_completed_habit,
    show_marked_habits
    )
from db.models.core_models import User
from schemas.habit_schema import HabitRead
from schemas.response_schemas import SuccessResponse, MessageResponse

completion_router = APIRouter()


@completion_router.post("/habits/{habit_id}/complete",response_model=MessageResponse, status_code=201)
def mark_habit_as_completed(
    habit_id: int, 
    db_session: Session = Depends(get_db), 
    current_user: User = Depends(require_verified_email)
    ):
    mark_completed_habit(
        habit_id=habit_id,
        db=db_session,
        user=current_user
    )

    return MessageResponse(message="Habit marked as completed")


@completion_router.delete("/habits/{habit_id}/complete",response_model=MessageResponse)
def unmark_habit(
    habit_id: int,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(require_verified_email)
    ):
    unmark_completed_habit(
        db=db_session, 
        habit_id=habit_id, 
        user=current_user
        )
    return MessageResponse(message="Habit unmarked as completed")


@completion_router.get("/all-habits-complete", response_model=SuccessResponse[list[HabitRead]])
def marked_habits(
    db_session: Session = Depends(get_db), 
    current_user: User = Depends(require_verified_email)
    ):
    marked_habits = show_marked_habits(db=db_session, user=current_user)
    return SuccessResponse(
        message="Successfully retrieved marked habits", 
        data=marked_habits
    )


