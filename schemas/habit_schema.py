from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class HabitBuild(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = Field(default=None)
    frequency: str = Field(min_length=1)

    @validator("name", "frequency")
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
    frequency: str
    built_at: datetime

    class Config:
        from_attributes = True


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    frequency: Optional[str] = Field(default=None)

    @validator("name", "frequency")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        if value is None:
            raise ValueError("Missing field error")
        
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Field cannot be empty")
        
        return stripped_value
 