"""Initial schema for FinX application

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

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
    op.create_table('user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('profile_image_url', sa.Text(), nullable=True),
        sa.Column('last_active_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('info', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('oauth_sub', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key'),
        sa.UniqueConstraint('oauth_sub')
    )

    # Create auth table
    op.create_table('auth',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create folder table
    op.create_table('folder',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('items', sa.Text(), nullable=True),     # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('is_expanded', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['folder.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat table
    op.create_table('chat',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('chat', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.Column('share_id', sa.Text(), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=True, default=False),
        sa.Column('pinned', sa.Boolean(), nullable=True, default=False),
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('folder_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['folder_id'], ['folder.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_id')
    )

    # Create channel table
    op.create_table('channel',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('access_control', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create message table
    op.create_table('message',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=True),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['message.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create message_reaction table
    op.create_table('message_reaction',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['message.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create file table
    op.create_table('file',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('hash', sa.Text(), nullable=True),
        sa.Column('filename', sa.Text(), nullable=True),
        sa.Column('path', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('access_control', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create knowledge table
    op.create_table('knowledge',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=True),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('access_control', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )

    # Create prompt table
    op.create_table('prompt',
        sa.Column('command', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.BigInteger(), nullable=True),
        sa.Column('access_control', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.PrimaryKeyConstraint('command')
    )

    # Create tag table
    op.create_table('tag',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.PrimaryKeyConstraint('id')
    )

    # Create group table
    op.create_table('group',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('user_ids', sa.Text(), nullable=True),     # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create memory table
    op.create_table('memory',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create feedback table
    op.create_table('feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create model table
    op.create_table('model',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('base_model_id', sa.String(), nullable=True),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('params', sa.Text(), nullable=True),    # JSONField stored as Text
        sa.Column('meta', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create connection table
    op.create_table('connection',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('config', sa.Text(), nullable=True),    # JSONField stored as Text
        sa.Column('credentials', sa.Text(), nullable=True),  # JSONField stored as Text (encrypted)
        sa.Column('health_check', sa.Text(), nullable=True), # JSONField stored as Text
        sa.Column('tags', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('last_connected', sa.DateTime(), nullable=True),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True, default=0),
        sa.Column('success_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create connection_template table
    op.create_table('connection_template',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('config_schema', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('credentials_schema', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('health_check_config', sa.Text(), nullable=True),  # JSONField stored as Text
        sa.Column('tags', sa.Text(), nullable=True),      # JSONField stored as Text
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create connection_log table
    op.create_table('connection_log',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('connection_id', sa.String(), nullable=False),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),   # JSONField stored as Text
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connection.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('connection_log')
    op.drop_table('connection_template')
    op.drop_table('connection')
    op.drop_table('model')
    op.drop_table('feedback')
    op.drop_table('memory')
    op.drop_table('group')
    op.drop_table('tag')
    op.drop_table('prompt')
    op.drop_table('knowledge')
    op.drop_table('file')
    op.drop_table('message_reaction')
    op.drop_table('message')
    op.drop_table('channel')
    op.drop_table('chat')
    op.drop_table('folder')
    op.drop_table('auth')
    op.drop_table('user')
