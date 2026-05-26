from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    if not isinstance(plain_password, str):
        raise TypeError(f"Expected str password, got {type(plain_password)}")
    
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str):
        raise TypeError(f"Expected str password, got {type(plain_password)}")
    
    return pwd_context.verify(plain_password, hashed_password)
