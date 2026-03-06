"""Add user features - password reset, email verification, notifications

Revision ID: 002
Revises: 001
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True))
    
    # Create password_resets table
    op.create_table(
        'password_resets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_password_resets_id'), 'password_resets', ['id'], unique=False)
    op.create_index(op.f('ix_password_resets_token'), 'password_resets', ['token'], unique=True)
    
    # Create email_verifications table
    op.create_table(
        'email_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_email_verifications_id'), 'email_verifications', ['id'], unique=False)
    op.create_index(op.f('ix_email_verifications_token'), 'email_verifications', ['token'], unique=True)
    
    # Add new columns to user_favorites table
    op.add_column('user_favorites', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('user_favorites', sa.Column('alert_enabled', sa.Boolean(), nullable=True))
    op.add_column('user_favorites', sa.Column('alert_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add new columns to user_strategies table
    op.add_column('user_strategies', sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('user_strategies', sa.Column('underlying_symbol', sa.String(length=20), nullable=True))
    op.add_column('user_strategies', sa.Column('underlying_price', sa.String(length=20), nullable=True))
    op.add_column('user_strategies', sa.Column('probability_of_profit', sa.String(length=20), nullable=True))
    op.add_column('user_strategies', sa.Column('initial_capital', sa.String(length=50), nullable=True))
    op.add_column('user_strategies', sa.Column('current_pnl', sa.String(length=50), nullable=True))
    op.add_column('user_strategies', sa.Column('pnl_percent', sa.String(length=20), nullable=True))
    op.add_column('user_strategies', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('user_strategies', sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create user_notifications table
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_notifications_id'), 'user_notifications', ['id'], unique=False)
    
    # Create login_history table
    op.create_table(
        'login_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('login_method', sa.String(length=20), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('failure_reason', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_login_history_id'), 'login_history', ['id'], unique=False)


def downgrade() -> None:
    # Drop login_history table
    op.drop_index(op.f('ix_login_history_id'), table_name='login_history')
    op.drop_table('login_history')
    
    # Drop user_notifications table
    op.drop_index(op.f('ix_user_notifications_id'), table_name='user_notifications')
    op.drop_table('user_notifications')
    
    # Remove columns from user_strategies
    op.drop_column('user_strategies', 'closed_at')
    op.drop_column('user_strategies', 'is_active')
    op.drop_column('user_strategies', 'pnl_percent')
    op.drop_column('user_strategies', 'current_pnl')
    op.drop_column('user_strategies', 'initial_capital')
    op.drop_column('user_strategies', 'probability_of_profit')
    op.drop_column('user_strategies', 'underlying_price')
    op.drop_column('user_strategies', 'underlying_symbol')
    op.drop_column('user_strategies', 'tags')
    
    # Remove columns from user_favorites
    op.drop_column('user_favorites', 'alert_settings')
    op.drop_column('user_favorites', 'alert_enabled')
    op.drop_column('user_favorites', 'notes')
    
    # Drop email_verifications table
    op.drop_index(op.f('ix_email_verifications_token'), table_name='email_verifications')
    op.drop_index(op.f('ix_email_verifications_id'), table_name='email_verifications')
    op.drop_table('email_verifications')
    
    # Drop password_resets table
    op.drop_index(op.f('ix_password_resets_token'), table_name='password_resets')
    op.drop_index(op.f('ix_password_resets_id'), table_name='password_resets')
    op.drop_table('password_resets')
    
    # Remove columns from users table
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar')
