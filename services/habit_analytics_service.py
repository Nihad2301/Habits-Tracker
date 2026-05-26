from db.models.core_models import User
from db.models.habit_analytics_models import HabitAnalytics
from db.models.core_models import HabitCompletion
from sqlalchemy.orm import Session
from services.habit_service import _get_owned_habit
from schemas.habit_analytics_schemas import HabitAnalyticsSchema
import datetime


def calculate_habit_streak(db: Session, user: User, habit_id: int):
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
    ).order_by(HabitCompletion.completion_date.desc()).all()
        
    current_streak = 0
    current_date = datetime.date.today()
    for completion in completions:
        # Convert completion_date to date for comparison
        completion_date = completion.completion_date
        if completion_date == current_date:
            current_streak += 1
            current_date -= datetime.timedelta(days=1)
        else:
            break
    
    return current_streak


def find_best_streak(db: Session, user: User, habit_id: int):
    habits = db.query(HabitAnalytics).filter(
        HabitAnalytics.habit_id == habit_id,
        HabitAnalytics.user_id == user.id
    ).all()
    
    if not habits:
        return 0
    
    return max([habit.current_streak for habit in habits])


def total_completions(db: Session, user: User, habit_id: int):
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
    ).count()

    return completions


def completion_rate(db: Session, habit_id: int, user: User):
    completions = total_completions(db=db, user=user, habit_id=habit_id)

    if completions == 0:
        return 0
    
    habit_at_day1 = db.query(HabitAnalytics).filter(
        HabitAnalytics.habit_id == habit_id,
        HabitAnalytics.user_id == user.id
    ).order_by(HabitAnalytics.date.asc()).first()

    last_habit = db.query(HabitAnalytics).filter(
        HabitAnalytics.habit_id == habit_id,
        HabitAnalytics.user_id == user.id
    ).order_by(HabitAnalytics.date.desc()).first()
    
    days_since_start = (last_habit.date - habit_at_day1.date).days + 1
    return round(completions / days_since_start * 100, 2)


def calculate_average_completion_time(db: Session, user: User, habit_id: int):
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
    ).all()
    
    if not completions:
        return "No completions"
    
    # Extract time from each completion_time (new field)
    times = []
    for completion in completions:
        if completion.completion_time is not None:
            time_part = completion.completion_time.time()
            times.append(time_part)

    if not times:
        return "No time data"
    
    # Calculate average time
    total_seconds = sum(t.hour * 3600 + t.minute * 60 + t.second for t in times)
    average_seconds = total_seconds / len(times)
    
    # Convert back to time
    avg_hour = int(average_seconds // 3600)
    avg_minute = int((average_seconds % 3600) // 60)
    
    # Determine AM/PM
    period = "AM" if avg_hour < 12 else "PM"
    
    return f"{avg_hour:02d}:{avg_minute:02d} {period}"


def habit_analytics(*, db: Session, user: User, habit_id: int):
    habit = _get_owned_habit(db=db, habit_id=habit_id, user=user)
    
    habit_analytics_info = db.query(HabitAnalytics).filter(
        HabitAnalytics.habit_id == habit.id,
        HabitAnalytics.user_id == user.id,
        HabitAnalytics.date == datetime.date.today()
        ).first()

    if not habit_analytics_info:
        current_streak = calculate_habit_streak(db=db, user=user, habit_id=habit_id)
        best_streak = find_best_streak(db=db, user=user, habit_id=habit_id)
        habit_analytics_info = HabitAnalytics(
            habit_id=habit.id,
            user_id=user.id,
            date=datetime.date.today(),
            current_streak=current_streak,
            best_streak=best_streak
        )

        db.add(habit_analytics_info)
        db.commit()
        db.refresh(habit_analytics_info)

    return HabitAnalyticsSchema(
        completion_rate=completion_rate(db=db, habit_id=habit.id, user=user),
        streak_days=calculate_habit_streak(db=db, user=user, habit_id=habit.id),
        longest_streak=find_best_streak(db=db, user=user, habit_id=habit.id),
        average_completion_time=calculate_average_completion_time(db=db, user=user, habit_id=habit.id),
        total_completions=total_completions(db=db, user=user, habit_id=habit.id)
    )


def weekly_days_with_completions(db: Session, user: User, habit_id: int) -> list:
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
    ).all()
    
    if not completions:
        return []

    week_start = min(c.completion_date for c in completions)
    week_end = week_start + datetime.timedelta(days=6)

    total_days = (datetime.datetime.now().date() - week_start).days
    week_count = total_days // 7 + 1
    
    weekly_data = []

    for i in range(week_count):
        week_completions = [
            c for c in completions 
            if week_start <= c.completion_date <= week_end
        ]
        weekly_data.append({
            "week_start": week_start,
            "days_with_completions": len(week_completions)
        })
        week_start += datetime.timedelta(days=7)
        week_end = week_start + datetime.timedelta(days=6)
    
    return weekly_data


