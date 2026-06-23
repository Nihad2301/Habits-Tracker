from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.core_models import User
from services.habit_analytics_service import (
    habit_analytics, 
    get_period_stats
)
from schemas.habit_analytics_schemas import (
    HabitAnalyticsSchema, 
    WeeklyStatsSchema, 
    MonthlyStatsSchema
)
from core.jwt_utils import get_current_user, require_verified_email

analytics_router = APIRouter()

@analytics_router.get("/habits/{habit_id}/analytics", response_model=HabitAnalyticsSchema)
def get_habit_analytics(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_verified_email)
):
    # Get analytics data
    analytics_data = habit_analytics(db=db, user=current_user, habit_id=habit_id)
    
    # Convert to schema format
    return analytics_data

@analytics_router.get("/habits/{habit_id}/weekly-stats", response_model=list[WeeklyStatsSchema])
def get_weekly_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_verified_email)
):
    # Get weekly stats
    weekly_stats = get_period_stats(db=db, user=current_user, habit_id=habit_id, period_name="week", period_days=7)
    
    # Convert to schema format
    return weekly_stats

@analytics_router.get("/habits/{habit_id}/monthly-stats", response_model=list[MonthlyStatsSchema])
def get_monthly_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_verified_email)
):
    # Get monthly stats
    monthly_stats = get_period_stats(db=db, user=current_user, habit_id=habit_id, period_name="month", period_days=30)
    
    # Convert to schema format
    return monthly_stats
