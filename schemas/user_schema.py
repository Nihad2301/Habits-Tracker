from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional

class UserBuild(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=254)
    
    @validator("username", "password")
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
    username: Optional[str] = Field(min_length=1, default=None, max_length=100)
    password: Optional[str] = Field(min_length=1, default=None, max_length=100)

    @validator("username", "password")
    @classmethod
    def strip_and_validate(cls, value) -> str:
        if value is None:
            return value

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Field cannot be empty")
        
        return stripped_value

class Login(BaseModel):
    username: str
    password: str

class ResendVerificationEmail(BaseModel):
    email: EmailStr    

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
 
        
            