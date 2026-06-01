"""change_completion_date_to_datetime

Revision ID: 8dabe73065b0
Revises: e970c1223abd
Create Date: 2026-05-03 17:35:00.980079

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8dabe73065b0'
down_revision: Union[str, Sequence[str], None] = 'e970c1223abd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Clean up any failed migration attempts first
    op.execute('DROP TABLE IF EXISTS habits_completion_new')
    
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    op.execute('CREATE TABLE habits_completion_new ('
               'id INTEGER NOT NULL, '
               'habit_id INTEGER NOT NULL, '
               'user_id INTEGER NOT NULL, '
               'completion_date DATE NOT NULL DEFAULT CURRENT_DATE, '
               'completion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, '
               'PRIMARY KEY (id), '
               'FOREIGN KEY(habit_id) REFERENCES habits (id) ON DELETE CASCADE, '
               'FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, '
               'UNIQUE (habit_id, user_id, completion_date))')
    
    # Copy data from old table to new table
    # Set completion_time to NULL for now, will be populated by new completions
    op.execute('INSERT INTO habits_completion_new (id, habit_id, user_id, completion_date, completion_time) '
               'SELECT id, habit_id, user_id, completion_date, NULL FROM habits_completion')
    
    # Drop old table and rename new table
    op.execute('DROP TABLE habits_completion')
    op.execute('ALTER TABLE habits_completion_new RENAME TO habits_completion')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the original table
    op.execute('CREATE TABLE habits_completion_new ('
               'id INTEGER NOT NULL, '
               'habit_id INTEGER NOT NULL, '
               'user_id INTEGER NOT NULL, '
               'completion_date DATE NOT NULL DEFAULT CURRENT_DATE, '
               'PRIMARY KEY (id), '
               'FOREIGN KEY(habit_id) REFERENCES habits (id) ON DELETE CASCADE, '
               'FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, '
               'UNIQUE (habit_id, user_id, completion_date))')
    
    # Copy data from new table to old table
    op.execute('INSERT INTO habits_completion_new (id, habit_id, user_id, completion_date) '
               'SELECT id, habit_id, user_id, completion_date FROM habits_completion')
    
    # Drop new table and rename old table
    op.execute('DROP TABLE habits_completion')
    op.execute('ALTER TABLE habits_completion_new RENAME TO habits_completion')
