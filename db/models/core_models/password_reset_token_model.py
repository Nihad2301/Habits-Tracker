from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from db.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Integer, default=0)  # 0 = not used, 1 = used

    user = relationship("User", back_populates="password_reset_tokens")

