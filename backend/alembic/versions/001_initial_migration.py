"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_vip', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    # Create user_favorites table
    op.create_table(
        'user_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_favorites_id'), 'user_favorites', ['id'], unique=False)

    # Create user_strategies table
    op.create_table(
        'user_strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strategy_type', sa.String(length=50), nullable=False),
        sa.Column('strategy_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('max_profit', sa.String(length=50), nullable=True),
        sa.Column('max_loss', sa.String(length=50), nullable=True),
        sa.Column('breakeven_points', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_strategies_id'), 'user_strategies', ['id'], unique=False)

    # Create market_snapshots table
    op.create_table(
        'market_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('name_en', sa.String(length=50), nullable=True),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=True),
        sa.Column('latest_price', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('price_change', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('price_change_percent', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('days_to_expiry', sa.Integer(), nullable=True),
        sa.Column('implied_vol', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('iv_change', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('iv_speed', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('realized_vol', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('premium', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('skew', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('iv_percentile', sa.Integer(), nullable=True),
        sa.Column('skew_percentile', sa.Integer(), nullable=True),
        sa.Column('is_main', sa.Boolean(), nullable=True),
        sa.Column('is_foreign', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index(op.f('ix_market_snapshots_category'), 'market_snapshots', ['category'], unique=False)
    op.create_index(op.f('ix_market_snapshots_exchange'), 'market_snapshots', ['exchange'], unique=False)
    op.create_index(op.f('ix_market_snapshots_id'), 'market_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_iv_percentile'), 'market_snapshots', ['iv_percentile'], unique=False)
    op.create_index(op.f('ix_market_snapshots_symbol'), 'market_snapshots', ['symbol'], unique=False)

    # Create option_contracts table
    op.create_table(
        'option_contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('underlying', sa.String(length=20), nullable=False),
        sa.Column('option_type', sa.String(length=4), nullable=False),
        sa.Column('strike', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('contract_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index(op.f('ix_option_contracts_expiry_date'), 'option_contracts', ['expiry_date'], unique=False)
    op.create_index(op.f('ix_option_contracts_id'), 'option_contracts', ['id'], unique=False)
    op.create_index(op.f('ix_option_contracts_symbol'), 'option_contracts', ['symbol'], unique=False)
    op.create_index(op.f('ix_option_contracts_underlying'), 'option_contracts', ['underlying'], unique=False)

    # Create market_quotes table (for TimescaleDB)
    op.create_table(
        'market_quotes',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('latest_price', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('price_change', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('price_change_percent', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('open_interest', sa.BigInteger(), nullable=True),
        sa.Column('implied_vol', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('iv_change', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('realized_vol', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('premium', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('skew', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.PrimaryKeyConstraint('time', 'symbol')
    )
    op.create_index(op.f('ix_market_quotes_symbol_time'), 'market_quotes', ['symbol', 'time'], unique=False)

    # Create option_quotes table (for TimescaleDB)
    op.create_table(
        'option_quotes',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('bid', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('ask', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('last_price', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.Column('open_interest', sa.Integer(), nullable=True),
        sa.Column('implied_vol', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('delta', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('gamma', sa.Numeric(precision=12, scale=8), nullable=True),
        sa.Column('theta', sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column('vega', sa.Numeric(precision=12, scale=6), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['option_contracts.id'], ),
        sa.PrimaryKeyConstraint('time', 'contract_id')
    )

    # Create unusual_flows table
    op.create_table(
        'unusual_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('underlying', sa.String(length=20), nullable=False),
        sa.Column('option_type', sa.String(length=4), nullable=False),
        sa.Column('strike', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('open_interest', sa.BigInteger(), nullable=True),
        sa.Column('premium', sa.BigInteger(), nullable=False),
        sa.Column('sentiment', sa.String(length=10), nullable=False),
        sa.Column('trade_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unusual_flows_sentiment'), 'unusual_flows', ['sentiment'], unique=False)
    op.create_index(op.f('ix_unusual_flows_symbol'), 'unusual_flows', ['symbol'], unique=False)
    op.create_index(op.f('ix_unusual_flows_symbol_time'), 'unusual_flows', ['symbol', 'trade_time'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_unusual_flows_symbol_time'), table_name='unusual_flows')
    op.drop_index(op.f('ix_unusual_flows_symbol'), table_name='unusual_flows')
    op.drop_index(op.f('ix_unusual_flows_sentiment'), table_name='unusual_flows')
    op.drop_table('unusual_flows')
    op.drop_table('option_quotes')
    op.drop_index(op.f('ix_market_quotes_symbol_time'), table_name='market_quotes')
    op.drop_table('market_quotes')
    op.drop_index(op.f('ix_option_contracts_underlying'), table_name='option_contracts')
    op.drop_index(op.f('ix_option_contracts_symbol'), table_name='option_contracts')
    op.drop_index(op.f('ix_option_contracts_id'), table_name='option_contracts')
    op.drop_index(op.f('ix_option_contracts_expiry_date'), table_name='option_contracts')
    op.drop_table('option_contracts')
    op.drop_index(op.f('ix_market_snapshots_symbol'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_iv_percentile'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_id'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_exchange'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_category'), table_name='market_snapshots')
    op.drop_table('market_snapshots')
    op.drop_index(op.f('ix_user_strategies_id'), table_name='user_strategies')
    op.drop_table('user_strategies')
    op.drop_index(op.f('ix_user_favorites_id'), table_name='user_favorites')
    op.drop_table('user_favorites')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
