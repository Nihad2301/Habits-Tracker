from db.models.core_models import User
from db.models.habit_analytics_models import HabitAnalytics
from db.models.core_models import HabitCompletion
from db.session import _commit_with_add
from sqlalchemy.orm import Session
from services.habit_service import _get_owned_habit
from config import settings
from datetime import datetime, timedelta
import pytz

local_tz = pytz.timezone(settings.TIMEZONE)

def calculate_habit_streak(db: Session, user: User, habit_id: int):
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
    ).order_by(HabitCompletion.completion_date.desc()).all()
        
    current_streak = 0

    current_date = datetime.now(local_tz).date()
    for completion in completions:
        # Convert completion_date to date for comparison
        completion_date = completion.completion_date
        if completion_date == current_date:
            current_streak += 1
            current_date -= timedelta(days=1)
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
        HabitAnalytics.date == datetime.now(local_tz).date()
        ).first()

    if not habit_analytics_info:
        current_streak = calculate_habit_streak(db=db, user=user, habit_id=habit_id)
        best_streak = find_best_streak(db=db, user=user, habit_id=habit_id)
        habit_analytics_info = HabitAnalytics(
            habit_id=habit.id,
            user_id=user.id,
            date=datetime.now(local_tz).date(),
            current_streak=current_streak,
            best_streak=best_streak
        )

        _commit_with_add(db=db, obj=habit_analytics_info)

    rate_of_completions = completion_rate(db=db, habit_id=habit.id, user=user)
    streak_days = calculate_habit_streak(db=db, user=user, habit_id=habit.id)
    longest_streak = find_best_streak(db=db, user=user, habit_id=habit.id)
    average_completion_time = calculate_average_completion_time(db=db, user=user, habit_id=habit.id)
    all_completions = total_completions(db=db, user=user, habit_id=habit.id)
    
    # Return the analytics data
    return {
        "completion_rate": rate_of_completions,
        "streak_days": streak_days,
        "longest_streak": longest_streak,
        "average_completion_time": average_completion_time,
        "total_completions": all_completions
    }

def _monthly_stats(completions: list) -> list:
    if not completions:
        return []
    
    latest_date = max(c.completion_date for c in completions)
    earliest_date = min(c.completion_date for c in completions)
    
    total_months = (latest_date.year - earliest_date.year) * 12 + \
                   (latest_date.month - earliest_date.month) + 1

    month_start = earliest_date.replace(day=1)
    next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)
    month_end = next_month - timedelta(days=1)                   

    monthly_stats = []
    
    for _ in range(total_months):
        month_completions = [
            c for c in completions 
            if month_start <= c.completion_date <= month_end
        ]
        monthly_stats.append({
            "month_start": month_start,
            "days_with_completions": len(month_completions)
        })
        month_start = next_month
        next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)
        month_end = next_month - timedelta(days=1)
    
    return monthly_stats
    
def _weekly_stats(completions: list) -> list:
    if not completions:
        return []
    
    latest_date = max(c.completion_date for c in completions)
    earliest_date = min(c.completion_date for c in completions)
    
    total_weeks = (latest_date - earliest_date).days // 7 + 1
    
    week_start = earliest_date - timedelta(days=earliest_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_stats = []
    
    for _ in range(total_weeks):
        week_completions = [
            c for c in completions 
            if week_start <= c.completion_date <= week_end
        ]
        weekly_stats.append({
            "week_start": week_start,
            "days_with_completions": len(week_completions)
        })
        week_start += timedelta(days=7)
        week_end = week_start + timedelta(days=6)
    
    return weekly_stats

def get_period_stats(
    period: str, 
    db: Session, 
    user: User, 
    habit_id: int, 
    skip: int, 
    limit: int
    ) -> list:
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.user_id == user.id
        ).all()
    if period == "monthly":
        return _monthly_stats(completions)[skip:skip+limit]
    elif period == "weekly":
        return _weekly_stats(completions)[skip:skip+limit]
    else:
        raise ValueError("Invalid period. Must be 'monthly' or 'weekly'")



    
    