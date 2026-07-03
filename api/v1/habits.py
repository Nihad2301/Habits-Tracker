from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.jwt_utils import get_current_user, require_verified_email
from schemas.response_schemas import MessageResponse, SuccessResponse
from services.habit_service import (
    retrieve_habit, 
    update,
    delete, 
    get_all, 
    add_habit
    )
from db.models.core_models import User
from schemas.habit_schema import HabitBuild, HabitRead, HabitUpdate

habit_router = APIRouter()

@habit_router.post("/habits", response_model=SuccessResponse[HabitRead], status_code=201)
def add_new_habit(
    habit: HabitBuild,
    current_one: User = Depends(require_verified_email),
    db_session: Session = Depends(get_db)
):
    habit_data = habit.model_dump(exclude_unset=True)

    new_one = add_habit(
        user=current_one,
        db=db_session,
        **habit_data
    )

    return SuccessResponse(
        message="Habit built successfully", 
        data=new_one
    )

@habit_router.get(
    "/habits", 
    response_model=SuccessResponse[dict[str, list[HabitRead]]])
def get_all_habits(
    db_session: Session = Depends(get_db), 
    user: User = Depends(require_verified_email)
):
    all_habits = get_all(db=db_session, user=user)
    return SuccessResponse(
        message="Habits retrieved successfully", 
        data={"habits": all_habits}
    )

@habit_router.get(
    "/habits/{habit_id}", 
    response_model=SuccessResponse[HabitRead])
def get_habit(
    habit_id: int, 
    db_session: Session = Depends(get_db), 
    user: User = Depends(require_verified_email)
):
    habit = retrieve_habit(habit_id=habit_id, db=db_session, user=user)
    return SuccessResponse(
        message="Habit retrieved successfully", 
        data=habit
    )

@habit_router.patch(
    "/habits/{habit_id}", 
    response_model=SuccessResponse[HabitRead])
def update_habit(
    habit_id: int,
    new_habit: HabitUpdate,
    db_session: Session = Depends(get_db),
    user: User = Depends(require_verified_email)
):
    update_data = new_habit.model_dump(exclude_unset=True)

    updated_habit = update(
        user=user,
        habit_id=habit_id,
        db=db_session,
        **update_data
    )

    return SuccessResponse(
        message="Habit updated successfully", 
        data=updated_habit
    )

@habit_router.delete("/habits/{habit_id}", response_model=MessageResponse)
def delete_habit(habit_id: int,
    db_session: Session = Depends(get_db),
    user: User = Depends(require_verified_email)
):
    delete(
        habit_id=habit_id,
        db=db_session,
        user=user
    )
    
    return MessageResponse(message=f"Habit with id {habit_id} is deleted")
