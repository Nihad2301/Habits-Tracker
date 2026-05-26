from db.session import Base
from db.models.core_models.habit_model import Habit
from db.models.core_models.user_model import User
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class HabitCompletion(Base):
    __tablename__ = "habits_completion"

    id = Column(Integer, primary_key=True, index=True)

    habit_id = Column(
        Integer, 
        ForeignKey("habits.id", ondelete="CASCADE"), 
        nullable=False
        )
    
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    completion_date = Column(
        Date,
        nullable=False
    )

    completion_time = Column(
        DateTime,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            'habit_id',
            'user_id',
            'completion_date',
            name='uq_habit_user_date'
        ), 
    )
    
    habit = relationship("Habit", back_populates="habit_completions")
    user = relationship("User", back_populates="habit_completions")
    