from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from db.models.core_models import User
from db.models.core_models import Habit
from db.session import _commit_with_add, _simple_commit
from exceptions import NotFoundError, AllFieldsEmptyError, AlreadyExistsError, ForbiddenError
import pytz
from datetime import datetime
from config import settings
import json
import redis
import logging
import time

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

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
    user: User, 
    db: Session, 
    name=None, 
    frequency=None, 
    description=None
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

    try:
        _commit_with_add(db=db, obj=new_habit)
        return new_habit
    except IntegrityError as e:
        if _already_exists(e):
            raise AlreadyExistsError("Habit already exists")


def get_all(db: Session, user: User, skip: int, limit: int) -> tuple[list[Habit], int]:
    all_habits = db.query(Habit).filter(Habit.user_id == user.id).offset(skip).limit(limit).all()
    total = db.query(Habit).filter(Habit.user_id == user.id).count()
    return all_habits, total


def retrieve_habit(habit_id: int, db: Session, user: User) -> dict:
    cache_key = f"habit:{user.id}:{habit_id}"
    
    start_time = time.time()
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"CACHE HIT: habit_id={habit_id}, user_id={user.id} - {elapsed:.2f}ms")
        return json.loads(cached_data)
    
    logger.info(f"CACHE MISS: habit_id={habit_id}, user_id={user.id} - querying database")
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)
    
    habit_dict = {
        "id": habit.id,
        "name": habit.name,
        "description": habit.description,
        "frequency": habit.frequency,
        "built_at": habit.built_at.isoformat() if habit.built_at else None
    }
    
    redis_client.setex(cache_key, 60, json.dumps(habit_dict))
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"CACHED: habit_id={habit_id}, user_id={user.id} with 60s TTL - {elapsed:.2f}ms")
    
    return habit_dict


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
        _commit_with_add(db=db, obj=habit)
    except IntegrityError as e:
        if _already_exists(e):
            raise AlreadyExistsError("Habit already exists")
        raise

    return habit


def delete(habit_id: int, db: Session, user: User) -> None:
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)

    db.delete(habit)
    _simple_commit(db=db)

