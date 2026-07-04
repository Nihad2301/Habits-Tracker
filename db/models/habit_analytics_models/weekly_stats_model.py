from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from db.session import Base
# from db.models.core_models import User
# from db.models.core_models import Habit
# from db.models.core_models import HabitCompletion
from sqlalchemy.orm import relationship

class WeeklyStats(Base):
    __tablename__ = "weekly_stats"
    
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
    
    week_start = Column(Date, nullable=False)
    
    days_with_completions = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'habit_id', 'week_start', name='uq_user_habit_week'),
    )

    user = relationship("User", back_populates="weekly_stats")
    habit = relationship("Habit", back_populates="weekly_stats")