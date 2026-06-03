"""add_email_and_verified

Revision ID: add_email_and_verified
Revises: 9a12a30a2e8f
Create Date: 2026-06-02

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_email_and_verified'
down_revision = '9a12a30a2e8f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'email')