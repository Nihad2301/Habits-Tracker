from db.session import engine, Base
from db.models.user_model import User
from db.models.habit_model import Habit
from db.models.habit_completion_model import HabitCompletion

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()