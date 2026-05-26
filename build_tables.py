from db.session import Base, engine
from db.models.core_models import User
from db.models.core_models import Habit
from db.models.habit_completion_model import HabitCompletion
from db.models.habit_analytics_models import HabitAnalytics

def make_tables():
    Base.metadata.create_all(bind=engine)


