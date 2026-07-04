from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

def _commit_with_add(db: Session, obj):
    try:
        db.add(obj)
        db.commit()           
        db.refresh(obj)
    except SQLAlchemyError:
        db.rollback()  
        raise     

def _simple_commit(db: Session):
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()  
        raise     