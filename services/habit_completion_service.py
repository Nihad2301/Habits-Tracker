from sqlalchemy.orm import Session
from db.models.core_models import User
from db.models.core_models import Habit
from db.models.core_models import HabitCompletion
from sqlalchemy.exc import IntegrityError
from exceptions import NotFoundError, AlreadyMarkedTodayError, NotMarkedYetError
from db.session import _commit_safely
from datetime import date, datetime
import pytz
from config import settings


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
    
    # Check for PostgreSQL error message
    if "duplicate key" in msg and "unique constraint" in msg:
        required_columns = [
            "habits_completion.habit_id",
            "habits_completion.user_id",
            "habits_completion.completion_date"
        ]
        return all(column in msg for column in required_columns)
    
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
    local_tz = pytz.timezone(settings.TIMEZONE)
    local_time = datetime.now(local_tz)
    local_date = local_time.date()
    
    print(f"DEBUG: Saving - habit_id={habit_id}, user_id={user.id}, completion_date={local_date}")
    
    completed_habit = HabitCompletion(
        habit_id=habit.id,
        user_id=habit.user_id,
        completion_date=local_date,
        completion_time=local_time
    )

    try:
        _commit_safely(db=db, obj=completed_habit)
        print(f"DEBUG: Saved successfully, id={completed_habit.id}")
    except IntegrityError as e:
        print(f"DEBUG: IntegrityError caught: {e}")
        print(f"DEBUG: Error message: {str(getattr(e, 'orig', e))}")
        if _is_already_marked_error(e):
            print(f"DEBUG: Raising AlreadyMarkedTodayError")
            raise AlreadyMarkedTodayError()
        else:
            print(f"DEBUG: Not a duplicate error, re-raising")
            raise
        
    return completed_habit
   

def unmark_completed_habit(db: Session, habit_id: int, user: User) -> str:
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)
    if habit is None:
        raise NotFoundError()

    marked_habit = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id, 
        HabitCompletion.completion_date == date.today()
        ).first()
    if marked_habit is None:
        raise NotMarkedYetError()
    
    db.delete(marked_habit)
    db.commit()
    
    return f"Habit at id {habit_id} is unmarked"


def show_marked_habits(db: Session, user: User) -> list[Habit]:
    local_tz = pytz.timezone(settings.TIMEZONE)
    local_time = datetime.now(local_tz)
    local_date = local_time.date()
    
    habits = db.query(HabitCompletion).filter(
        HabitCompletion.user_id == user.id,
        HabitCompletion.completion_date == local_date
    ).all()

    return habits



