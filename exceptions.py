from fastapi import Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError

class AppException(Exception):
    status_code = 500
    default_message = "Something went wrong"

    def __init__(self, message=None):
        self.message = message or self.default_message    


class CustomErrorResponse(BaseModel):
    status_code: int
    message: str
    path: str
    method: str

class CustomErrorResponseModel(BaseModel):
    success: bool = False
    error: CustomErrorResponse


class NotFoundError(AppException):
    status_code = 404
    default_message = "Not found"

class AllFieldsEmptyError(AppException):
    status_code = 400
    default_message = "No fields provided for update"

class OwnershipError(AppException):
    status_code = 403
    default_message = "You do not own it"

class AlreadyExistsError(AppException):  
    status_code = 409
    default_message = "Already exists"

class WeakPasswordError(AppException):
    status_code = 400
    default_message = "Password must be at least 8 characters long"

class IncorrectPasswordError(AppException):
    status_code = 401
    default_message = "Incorrect password"

class AlreadyMarkedTodayError(AppException):
    status_code = 409
    default_message = "This habit is already marked today"

class NotMarkedYetError(AppException):
    status_code = 409
    default_message = "This habit is not marked today"    

class ForbiddenError(AppException):
    status_code = 403
    default_message = "Forbidden"  

class ExpiredTokenError(AppException):
    status_code = 401
    default_message = "Token is expired"

class InvalidTokenError(AppException):
    status_code = 401
    default_message = "Token is invalid"


async def custom_exception_handler(request: Request, exc: AppException):
    error_data = CustomErrorResponse(
        status_code=exc.status_code,
        message=exc.message,
        path=request.url.path,
        method=request.method
        )
    
    return JSONResponse(
        status_code=exc.status_code, 
        content=CustomErrorResponseModel(error=error_data).model_dump()
        )     

def _safe_errors(exc: RequestValidationError):
    safe = []

    for e in exc.errors():
        item = {
            "type": e.get("type"),
            "loc": e.get("loc"),
            "msg": e.get("msg")
        }

        if "ctx" in e:
            item["ctx"] = {k: str(v) for k, v in e["ctx"].items()}   

        safe.append(item)

    return safe         

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    method = getattr(request, "method", None)
    url = getattr(request, "url", None)
    path = getattr(url, "path", None)

    return JSONResponse(
        status_code = 422,
        content={
            "success": False,
            "error": {               
                "status_code": 422,
                "message": "Validation error",
                "details": _safe_errors(exc=exc),
                "path": path,
                "method": method
                }
            }      
        )

def jwt_exception_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "error": {
                "status_code": 401,
                "message": "Token is invalid",
                "details": str(exc),
                "path": request.url.path,
                "method": request.method
            }
        }
    )