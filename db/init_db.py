from db.session import engine, Base
from db.models.user_model import User  # noqa: F401
from db.models.habit_model import Habit  # noqa: F401
from db.models.habit_completion_model import HabitCompletion  # noqa: F401

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()