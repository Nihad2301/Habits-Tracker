from config import settings
from sqlalchemy import create_engine, inspect
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

def _commit_safely(db: Session, obj=None):
    try:
        if obj is not None:
            db.add(obj)
        db.commit()
        if obj is not None:            
            db.refresh(obj)
    except SQLAlchemyError:
        db.rollback()  
        raise        