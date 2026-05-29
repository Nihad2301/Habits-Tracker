from datetime import date
from pydantic import BaseModel

class HabitAnalyticsSchema(BaseModel):
    completion_rate: float
    streak_days: int
    longest_streak: int
    average_completion_time: str
    total_completions: int
    
    class Config:
        from_attributes = True

class WeeklyStatsSchema(BaseModel):
    week_start: date
    days_with_completions: int
    
    class Config:
        from_attributes = True

class MonthlyStatsSchema(BaseModel):
    month_start: date
    days_with_completions: int
    
    class Config:
        from_attributes = True
