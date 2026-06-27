from pydantic import BaseModel, Field, validator
from typing import Optional


class UserBuild(BaseModel):
    username: str = Field("", min_length=1)
    password: str = Field("", min_length=1)
    email: str = Field("", min_length=1)

    @validator("username", "password", "email")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("Field cannot be empty")
        
        return stripped_value


class UserRead(BaseModel):
    id: int
    username: str
    is_verified: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)

    @validator("username", "password")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("Field cannot be empty")
        
        return stripped_value

class Login(BaseModel):
    username: str
    password: str
 
        
            