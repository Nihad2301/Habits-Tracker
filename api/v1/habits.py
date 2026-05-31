from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.jwt_utils import get_current_user
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

@habit_router.post("/habits", response_model=HabitRead, status_code=201)
def add_new_habit(
    habit: HabitBuild,
    current_one: User = Depends(get_current_user),
    db_session: Session = Depends(get_db)
):
    habit_data = habit.model_dump(exclude_unset=True)

    new_one = add_habit(
        user=current_one,
        db=db_session,
        **habit_data
    )

    return new_one

@habit_router.get("/habits", response_model=dict[str, list[HabitRead]])
def get_all_habits(
    db_session: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    all_habits = get_all(db=db_session, user=user)
    return {"habits": all_habits}

@habit_router.get("/habits/{habit_id}", response_model=HabitRead)
def get_habit(
    habit_id: int, 
    db_session: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    habit = retrieve_habit(habit_id=habit_id, db=db_session, user=user)
    return habit

@habit_router.patch("/habits/{habit_id}", response_model=HabitRead)
def update_habit(
    habit_id: int,
    new_habit: HabitUpdate,
    db_session: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    update_data = new_habit.model_dump(exclude_unset=True)

    updated_habit = update(
        user=user,
        habit_id=habit_id,
        db=db_session,
        **update_data
    )

    return updated_habit

@habit_router.delete("/habits/{habit_id}")
def delete_habit(habit_id: int,
    db_session: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return delete(
        habit_id=habit_id,
        db=db_session,
        user=user
    )
