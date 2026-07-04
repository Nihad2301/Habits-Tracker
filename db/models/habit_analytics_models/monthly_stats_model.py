from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.session import Base
# from db.models.core_models import User
# from db.models.core_models import Habit
# from db.models.core_models import HabitCompletion

class MonthlyStats(Base):
    __tablename__ = "monthly_stats"
    
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
    
    month_start = Column(Date, nullable=False)
    
    days_with_completions = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'habit_id', 'month_start', name='uq_user_habit_month'),
    )

    user = relationship("User", back_populates="monthly_stats")
    habit = relationship("Habit", back_populates="monthly_stats")