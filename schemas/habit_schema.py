from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class FrequencyEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class HabitBuild(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    frequency: FrequencyEnum

    @validator("name")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        if value is None:
            raise ValueError("Missing field error")
        
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Field cannot be empty")
        
        return stripped_value

class HabitRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = Field(default=None)
    frequency: FrequencyEnum
    built_at: datetime

    class Config:
        from_attributes = True

class HabitUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    frequency: Optional[FrequencyEnum] = Field(default=None)

    @validator("name")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        if value is None:
            return value

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Field cannot be empty")
        return stripped_value
 
class PaginatedResponse(BaseModel):
    habits: list[HabitRead]
    total: int
 