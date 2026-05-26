from sqlalchemy import (
    Column, Integer, 
    String, ForeignKey, 
    DateTime, UniqueConstraint
    )
from sqlalchemy.sql import func
from db.session import Base
from sqlalchemy.orm import relationship

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency = Column(String, nullable=False)

    built_at = Column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "name",           
            "user_id",
            name="uq_name_and_user_id"
        ),
    )

    user = relationship("User", back_populates="habits")
    habit_completions = relationship("HabitCompletion", back_populates="habit")
    habit_analytics = relationship("HabitAnalytics", back_populates="habit")
    weekly_stats = relationship("WeeklyStats", back_populates="habit")
    monthly_stats = relationship("MonthlyStats", back_populates="habit")

