from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from db.models.core_models import User
from db.models.core_models import Habit
from db.session import _commit_safely
from exceptions import NotFoundError, AllFieldsEmptyError, AlreadyExistsError, ForbiddenError
import pytz
from datetime import datetime
from config import settings

def _already_exists(e: IntegrityError) -> bool:
    msg = str(getattr(e, "orig", e)).lower()

    if "unique constraint failed" in msg:
        required_columns = ["habits.name", "habits.user_id"]
        return all(column in msg for column in required_columns)

    return False
                                          

def _get_owned_habit(db: Session, habit_id: int, user: User) -> Habit:
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if habit is None:
        raise NotFoundError()
    
    if habit.user_id != user.id:
        raise ForbiddenError()
    
    return habit


def add_habit(
        *,
        user: User, db: Session, name=None, 
        frequency=None, description=None
        ) -> Habit:
    local_tz = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(local_tz)
    
    new_habit = Habit(
        name=name,
        frequency=frequency,
        description=description,
        user_id=user.id,
        built_at=now
        )

    db.add(new_habit)

    try:
        _commit_safely(db=db, obj=new_habit)
        return new_habit
    except IntegrityError as e:
        if _already_exists(e):
            raise AlreadyExistsError("Habit already exists")


def get_all(db: Session, user: User) -> list[Habit]:
    all_habits = db.query(Habit).filter(Habit.user_id == user.id).all()

    return all_habits


def retrieve_habit(habit_id: int, db: Session, user: User) -> Habit:
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)

    return habit


def update(
        *,
        user: User,
        habit_id: int,
        db: Session,
        name: Optional[str] = None, 
        frequency: Optional[str] = None, 
        description: Optional[str] = None
        ) -> Habit:
    
    updates = {
        "name": name,
        "frequency": frequency,
        "description": description
    }
    
    if all(data is None for data in updates.values()):
        raise AllFieldsEmptyError()

    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)
    
    for field, value in updates.items():
        if value is not None:
            setattr(habit, field, value)           

    try:
        _commit_safely(db=db, obj=habit)
    except IntegrityError as e:
        if _already_exists(e):
            raise AlreadyExistsError("Habit already exists")
        raise

    return habit


def delete(habit_id: int, db: Session, user: User) -> dict:
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)

    db.delete(habit)
    _commit_safely(db=db)
    
    return {"message": f"Habit with id {habit_id} is deleted"}
