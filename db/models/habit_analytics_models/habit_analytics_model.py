from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from db.session import Base
# from db.models.core_models import User
# from db.models.core_models import Habit
# from db.models.core_models import HabitCompletion
from sqlalchemy.orm import relationship

class HabitAnalytics(Base):
    __tablename__ = "habit_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    habit_id = Column(
        Integer,
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False
    )
    
    date = Column(Date, nullable=False)
    
    total_completions = Column(Integer, default=0)
    
    current_streak = Column(Integer, default=0)
    
    best_streak = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'habit_id', 'date', name='uq_analytics_user_habit_date'),
    )

    user = relationship("User", back_populates="habit_analytics")
    habit = relationship("Habit", back_populates="habit_analytics")

    