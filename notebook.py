"""
12.04.2026

what we did today:
- Fixed JWT error handling in verify_token() 
- Removed redundant malformed token test
- Added missing 'sub' field test
- Cleaned up conftest.py imports
- Completed JWT security testing suite

what's next (simple & productive):
1. Run full test suite to ensure everything works
2. Test multi-user functionality one more time
3. Review and clean up any remaining code smells
4. Plan next feature or improvement

"""

"""
14.04.2026

what we are going to do:
- Clean conftest.py to simplify fixture complexity
- Reduce test fixture dependencies
- Fix broken test patterns
- Make tests easier to maintain

what we did today:
- Identified conftest.py complexity issues
- Started refactoring auth_client patterns
- Separated client1/client2 to avoid conflicts
- Working on simplifying test dependencies
"""

"""
14.04.2026 - Analytics Development

what we are going to do:
- Design analytics database schema (HabitAnalytics + 3 dependent tables)
- Create analytics API endpoints (summary, streaks, trends, charts)
- Build habit completion tracking logic
- Add streak calculation (current/best streaks)
- Create analytics response schemas
- Write analytics tests

what we did today:
- Completed conftest.py cleanup (all 11 tests passing)
- Fixed fixture complexity issues
- Reduced test dependencies
- Planned analytics system architecture
- Decided on 4-table analytics schema
"""


"""
23.04.2026 - Analytics & Database Setup

what we did today:
- Fixed SQLAlchemy relationship back_populates issues across all models
- Fixed Alembic imports to match new model structure after reorganization
- Generated and applied analytics tables migration (habit_analytics, daily_stats, weekly_stats, monthly_stats)
- Fixed database connectivity issues - all tables now exist
- Analytics API endpoint now works (returns empty list, but no errors)
- Learned about back_populates = exact variable name in other model

what's next (today's plan):
1. Build habit completion tracking logic (when habit is completed, create/update analytics)
2. Add streak calculation (current streak and best streak logic)
3. Complete analytics API endpoints (add more endpoints beyond basic analytics)
4. Fix Pydantic V1 to V2 deprecation warnings
5. Fix datetime.utcnow() deprecation warning
6. Write analytics tests

key learning:
- back_populates always points to the exact variable name in the other model
- Alembic migrations need to be updated when model structure changes
- Handle infrastructure issues yourself for maximum learning
"""



"""
Todo:
- Calculate completion stats only daily for now, 
  but in the future add considered frequency for this as well.
"""