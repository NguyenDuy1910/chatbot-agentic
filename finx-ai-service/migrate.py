#!/usr/bin/env python3
"""
Migration script for FinX application
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web.internal.migration_manager import MigrationManager


def main():
    """Main migration script"""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command> [args]")
        print("Commands:")
        print("  init                    - Initialize migrations")
        print("  create <message>        - Create a new migration")
        print("  migrate [revision]      - Run migrations (default: head)")
        print("  rollback <revision>     - Rollback to revision")
        print("  current                 - Show current revision")
        print("  history                 - Show migration history")
        print("  create-tables           - Create all tables")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = MigrationManager()
    
    try:
        if command == "init":
            manager.init_alembic()
            print("✅ Migrations initialized")
            
        elif command == "create":
            if len(sys.argv) < 3:
                print("Error: Migration message required")
                sys.exit(1)
            message = " ".join(sys.argv[2:])
            manager.create_migration(message)
            print(f"✅ Migration created: {message}")
            
        elif command == "migrate":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            manager.run_migrations(revision)
            print(f"✅ Migrations applied to {revision}")
            
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Error: Target revision required")
                sys.exit(1)
            revision = sys.argv[2]
            manager.rollback_migration(revision)
            print(f"✅ Rolled back to {revision}")
            
        elif command == "current":
            current = manager.get_current_revision()
            if current:
                print(f"Current revision: {current}")
            else:
                print("No migrations applied yet")
                
        elif command == "history":
            manager.get_migration_history()
            
        elif command == "create-tables":
            manager.create_tables_if_not_exist()
            print("✅ All tables created")
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
