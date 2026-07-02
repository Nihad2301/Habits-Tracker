from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from db.session import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    last_logout = Column(DateTime, nullable=True)
    full_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    language = Column(String, default="en")
    theme = Column(String, default="light")

    habits = relationship("Habit", back_populates="user")
    habit_completions = relationship("HabitCompletion", back_populates="user")
    habit_analytics = relationship("HabitAnalytics", back_populates="user")
    weekly_stats = relationship("WeeklyStats", back_populates="user")
    monthly_stats = relationship("MonthlyStats", back_populates="user")
    email_verification_tokens = relationship("EmailVerificationToken", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
