from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.core_models import User
from services.habit_analytics_service import habit_analytics, weekly_days_with_completions
from schemas.habit_analytics_schemas import HabitAnalyticsSchema, WeeklyStatsSchema
from core.jwt_utils import get_current_user

analytics_router = APIRouter()

@analytics_router.get("/habits/{habit_id}/analytics", response_model=HabitAnalyticsSchema)
def get_habit_analytics(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get analytics data
    analytics_data = habit_analytics(db=db, user=current_user, habit_id=habit_id)
    
    # Convert to schema format
    return analytics_data

@analytics_router.get("/habits/{habit_id}/weekly-stats", response_model=list[WeeklyStatsSchema])
def get_weekly_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get weekly stats
    weekly_stats = weekly_days_with_completions(db=db, user=current_user, habit_id=habit_id)
    
    # Convert to schema format
    return weekly_stats
