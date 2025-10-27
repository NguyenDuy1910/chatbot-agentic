import logging
from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import your models and database configuration
from src.web.internal.db import Base, JSONField
from src.web.constants.config import DATABASE_PROVIDER, get_database_url

# Import all models to ensure they are registered with SQLAlchemy
from src.web.models.users import User
from src.web.models.auths import Auth
from src.web.models.chats import Chat, Folder
from src.web.models.messages import Message, MessageReaction
from src.web.models.connections import Connection, ConnectionTemplate, ConnectionLog
from src.web.models.files import File
from src.web.models.knowledge import Knowledge
from src.web.models.prompts import Prompt
from src.web.models.tags import Tag
from src.web.models.groups import Group
from src.web.models.memories import Memory
from src.web.models.feedback import Feedback
from src.web.models.models import Model
from src.web.models.channels import Channel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from configuration"""
    try:
        return get_database_url()
    except Exception as e:
        # Fallback for development
        return os.getenv("DATABASE_URL", "sqlite:///./finx.db")


def render_item(type_, obj, autogen_context):
    """Render custom types for Alembic autogenerate"""
    if type_ == "type" and isinstance(obj, JSONField):
        # Import statement will be added to the migration file
        autogen_context.imports.add("from src.web.internal.db import JSONField")
        return "JSONField()"

    # Return None for default rendering
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Override the sqlalchemy.url in the alembic config
    config.set_main_option("sqlalchemy.url", get_url())
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
