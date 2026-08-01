from sqlalchemy.orm import Session
from db.models.core_models import User
from db.models.core_models import Habit
from db.models.core_models import HabitCompletion
from sqlalchemy.exc import IntegrityError
from exceptions import NotFoundError, AlreadyMarkedTodayError, NotMarkedYetError
from db.session import _commit_with_add, _simple_commit
from datetime import date, datetime
import pytz
from config import settings

local_tz = pytz.timezone(settings.TIMEZONE)

def _is_already_marked_error(e: IntegrityError) -> bool:
    msg = str(getattr(e, "orig", e)).lower()

    # Check for SQLite error message
    if "unique constraint failed" in msg:
        required_columns = [
            "habits_completion.habit_id",
            "habits_completion.user_id",
            "habits_completion.completion_date"
        ] 
        return all(column in msg for column in required_columns)
    
    # Check for PostgreSQL error message (any duplicate key violation on habits_completion)
    if "duplicate key" in msg and "unique constraint" in msg and "habits_completion" in msg:
        return True
    
    return False


def _get_owned_habit(db: Session, habit_id: int, user: User):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
        ).first()

    if habit is None:
        raise NotFoundError()   
    
    return habit


def mark_completed_habit(habit_id: int, db: Session, user: User) -> HabitCompletion:
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)

    # Get local timezone (you can change this to your specific timezone)
    local_time = datetime.now(local_tz)
    local_date = local_time.date()
    
    completed_habit = HabitCompletion(
        habit_id=habit.id,
        user_id=habit.user_id,
        completion_date=local_date,
        completion_time=local_time
    )

    try:
        _commit_with_add(db=db, obj=completed_habit)
    except IntegrityError as e:
        if _is_already_marked_error(e):
            raise AlreadyMarkedTodayError()   
        
    return completed_habit
   

def unmark_completed_habit(db: Session, habit_id: int, user: User) -> str:
    local_date = datetime.now(local_tz).date()

    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)
    if habit is None:
        raise NotFoundError()

    marked_habit = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id, 
        HabitCompletion.completion_date == local_date
        ).first()
    if marked_habit is None:
        raise NotMarkedYetError()
    
    db.delete(marked_habit)
    _simple_commit(db=db)


def show_marked_habits(db: Session, user: User, skip: int, limit: int) -> list[Habit]:
    local_time = datetime.now(local_tz)
    local_date = local_time.date()
    
    habits = db.query(HabitCompletion).filter(
        HabitCompletion.user_id == user.id,
        HabitCompletion.completion_date == local_date
    ).offset(skip).limit(limit).all()

    return habits



