"""
Migration management utilities for FinX application
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from finx.constants import SRC_LOG_LEVELS, get_database_url
from finx.internal.db import Base, init_database
# Import all models to ensure they're registered with SQLAlchemy
from finx.models import *

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["DB"])


class MigrationManager:
    """Manages database migrations using Alembic"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.alembic_cfg_path = self.project_root / "finx" / "internal" / "alembic.ini"
        self.alembic_dir = self.project_root / "finx" / "internal" / "alembic"
        
    def get_alembic_config(self) -> Config:
        """Get Alembic configuration"""
        if not self.alembic_cfg_path.exists():
            raise FileNotFoundError(f"Alembic config not found at {self.alembic_cfg_path}")
        
        config = Config(str(self.alembic_cfg_path))
        
        # Set the script location relative to the config file
        config.set_main_option("script_location", str(self.alembic_dir))
        
        # Set the database URL
        try:
            db_url = get_database_url()
            config.set_main_option("sqlalchemy.url", db_url)
        except Exception as e:
            log.warning(f"Could not get database URL: {e}")
            # Use a default SQLite URL for development
            config.set_main_option("sqlalchemy.url", "sqlite:///./finx.db")
        
        return config
    
    def init_alembic(self):
        """Initialize Alembic (create alembic_version table)"""
        try:
            config = self.get_alembic_config()
            command.stamp(config, "head")
            log.info("Alembic initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Alembic: {e}")
            raise
    
    def create_migration(self, message: str, autogenerate: bool = True):
        """Create a new migration"""
        try:
            config = self.get_alembic_config()
            if autogenerate:
                command.revision(config, message=message, autogenerate=True)
            else:
                command.revision(config, message=message)
            log.info(f"Migration created: {message}")
        except Exception as e:
            log.error(f"Failed to create migration: {e}")
            raise
    
    def run_migrations(self, revision: str = "head"):
        """Run migrations to the specified revision"""
        try:
            config = self.get_alembic_config()
            command.upgrade(config, revision)
            log.info(f"Migrations applied successfully to {revision}")
        except Exception as e:
            log.error(f"Failed to run migrations: {e}")
            raise
    
    def rollback_migration(self, revision: str):
        """Rollback to a specific revision"""
        try:
            config = self.get_alembic_config()
            command.downgrade(config, revision)
            log.info(f"Rolled back to revision {revision}")
        except Exception as e:
            log.error(f"Failed to rollback migration: {e}")
            raise
    
    def get_current_revision(self) -> Optional[str]:
        """Get the current database revision"""
        try:
            config = self.get_alembic_config()
            # This is a bit tricky - we need to check the database directly
            db_url = config.get_main_option("sqlalchemy.url")
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                try:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    row = result.fetchone()
                    return row[0] if row else None
                except Exception:
                    # Table doesn't exist yet
                    return None
        except Exception as e:
            log.error(f"Failed to get current revision: {e}")
            return None
    
    def get_migration_history(self):
        """Get migration history"""
        try:
            config = self.get_alembic_config()
            command.history(config)
        except Exception as e:
            log.error(f"Failed to get migration history: {e}")
            raise
    
    def show_current_revision(self):
        """Show current revision"""
        try:
            config = self.get_alembic_config()
            command.current(config)
        except Exception as e:
            log.error(f"Failed to show current revision: {e}")
            raise
    
    def create_tables_if_not_exist(self):
        """Create all tables if they don't exist (for development)"""
        try:
            # Initialize database connection
            init_database()

            # Create all tables
            from finx.internal.db import engine
            if engine:
                Base.metadata.create_all(bind=engine)
                log.info("All tables created successfully")
            else:
                log.error("Database engine not initialized")
        except Exception as e:
            log.error(f"Failed to create tables: {e}")
            raise
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            from finx.internal.db import engine
            if engine:
                Base.metadata.drop_all(bind=engine)
                log.info("All tables dropped successfully")
            else:
                log.error("Database engine not initialized")
        except Exception as e:
            log.error(f"Failed to drop tables: {e}")
            raise


# Convenience functions
def init_migrations():
    """Initialize migrations"""
    manager = MigrationManager()
    manager.init_alembic()


def create_migration(message: str, autogenerate: bool = True):
    """Create a new migration"""
    manager = MigrationManager()
    manager.create_migration(message, autogenerate)


def run_migrations(revision: str = "head"):
    """Run migrations"""
    manager = MigrationManager()
    manager.run_migrations(revision)


def rollback_migration(revision: str):
    """Rollback migration"""
    manager = MigrationManager()
    manager.rollback_migration(revision)


def get_current_revision() -> Optional[str]:
    """Get current revision"""
    manager = MigrationManager()
    return manager.get_current_revision()


def create_tables():
    """Create all tables"""
    manager = MigrationManager()
    manager.create_tables_if_not_exist()


if __name__ == "__main__":
    """Command line interface for migration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinX Migration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize migrations")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    create_parser.add_argument("--no-autogenerate", action="store_true", help="Don't auto-generate migration")
    
    # Run migrations command
    run_parser = subparsers.add_parser("migrate", help="Run migrations")
    run_parser.add_argument("--revision", default="head", help="Target revision")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migration")
    rollback_parser.add_argument("revision", help="Target revision")
    
    # Current revision command
    subparsers.add_parser("current", help="Show current revision")
    
    # History command
    subparsers.add_parser("history", help="Show migration history")
    
    # Create tables command
    subparsers.add_parser("create-tables", help="Create all tables")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = MigrationManager()
    
    try:
        if args.command == "init":
            manager.init_alembic()
        elif args.command == "create":
            manager.create_migration(args.message, not args.no_autogenerate)
        elif args.command == "migrate":
            manager.run_migrations(args.revision)
        elif args.command == "rollback":
            manager.rollback_migration(args.revision)
        elif args.command == "current":
            manager.show_current_revision()
        elif args.command == "history":
            manager.get_migration_history()
        elif args.command == "create-tables":
            manager.create_tables_if_not_exist()
    except Exception as e:
        log.error(f"Command failed: {e}")
        sys.exit(1)
