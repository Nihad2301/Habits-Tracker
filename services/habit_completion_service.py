from sqlalchemy.orm import Session
from db.models.core_models import User
from db.models.core_models import Habit
from db.models.core_models import HabitCompletion
from sqlalchemy.exc import IntegrityError
from exceptions import NotFoundError, AlreadyMarkedTodayError, NotMarkedYetError
from db.session import _commit_safely
from datetime import date, datetime
import pytz


def _is_already_marked_error(e: IntegrityError) -> bool:
    msg = str(getattr(e, "orig", e)).lower()

    if "unique constraint failed" not in msg:
        return False

    required_columns = [
        "habits_completion.habit_id",
        "habits_completion.user_id",
        "habits_completion.completion_date"
    ] 

    return all(column in msg for column in required_columns)


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
    local_tz = pytz.timezone('Asia/Baku')  # UTC+4 for your timezone
    local_time = datetime.now(local_tz)
    local_date = local_time.date()
    
    completed_habit = HabitCompletion(
        habit_id=habit.id,
        user_id=habit.user_id,
        completion_date=local_date,
        completion_time=local_time
    )

    try:
        _commit_safely(db=db, obj=completed_habit)
    except IntegrityError as e:
        if _is_already_marked_error(e):
            raise AlreadyMarkedTodayError()   
        
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
    habits = db.query(HabitCompletion).filter(
        HabitCompletion.user_id == user.id,
        HabitCompletion.completion_date == date.today()
    ).all()

    return habits



