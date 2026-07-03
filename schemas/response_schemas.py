from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    message: str
    data: T
    
class MessageResponse(BaseModel):
    message: str