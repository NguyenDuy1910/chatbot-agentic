# FinX Database Migrations

This directory contains the database migration system for the FinX application using Alembic (SQLAlchemy's migration tool).

## Overview

The migration system has been updated from Peewee to SQLAlchemy/Alembic to match the project's current database architecture. All models are now defined using SQLAlchemy ORM and migrations are managed through Alembic.

## Directory Structure

```
finx/internal/alembic/
├── README.md              # This file
├── env.py                 # Alembic environment configuration
├── script.py.mako         # Template for new migration files
└── versions/              # Migration files
    └── 001_initial_schema.py  # Initial database schema
```

## Database Models

The migration system supports all current FinX models:

### Core Models
- **User** - User accounts and authentication
- **Auth** - Authentication credentials
- **Chat** - Chat conversations
- **Folder** - Chat organization folders
- **Message** - Individual messages
- **MessageReaction** - Message reactions/emojis

### Content Models
- **File** - File uploads and metadata
- **Knowledge** - Knowledge base entries
- **Prompt** - Prompt templates
- **Tag** - Content tagging system
- **Memory** - AI memory system
- **Feedback** - User feedback

### System Models
- **Connection** - External system connections
- **ConnectionTemplate** - Connection templates
- **ConnectionLog** - Connection activity logs
- **Channel** - Communication channels
- **Group** - User groups and permissions
- **Model** - AI model configurations

## Usage

### Using the Migration Script

The easiest way to manage migrations is using the `migrate.py` script in the backend root:

```bash
# Initialize migrations (first time setup)
python migrate.py init

# Create a new migration
python migrate.py create "Add new feature"

# Run all pending migrations
python migrate.py migrate

# Rollback to a specific revision
python migrate.py rollback <revision_id>

# Show current revision
python migrate.py current

# Show migration history
python migrate.py history

# Create all tables (development only)
python migrate.py create-tables
```

### Using Alembic Directly

You can also use Alembic commands directly:

```bash
# From the backend directory
cd backend

# Initialize Alembic (first time)
alembic -c finx/internal/alembic.ini stamp head

# Create a new migration
alembic -c finx/internal/alembic.ini revision --autogenerate -m "Description"

# Run migrations
alembic -c finx/internal/alembic.ini upgrade head

# Rollback one revision
alembic -c finx/internal/alembic.ini downgrade -1

# Show current revision
alembic -c finx/internal/alembic.ini current

# Show history
alembic -c finx/internal/alembic.ini history
```

## Configuration

### Database Connection

The migration system automatically detects your database configuration from:

1. Environment variables (for production)
2. Configuration files (for development)
3. Falls back to SQLite for local development

### Supported Databases

- **PostgreSQL** (recommended for production)
- **Supabase** (PostgreSQL-based)
- **SQLite** (development only)

## Migration Best Practices

### Creating Migrations

1. **Always review auto-generated migrations** before applying them
2. **Test migrations on a copy of production data** before deploying
3. **Use descriptive names** for migration messages
4. **Keep migrations small and focused** on single changes

### Model Changes

When you modify SQLAlchemy models:

1. Create a new migration: `python migrate.py create "Description of change"`
2. Review the generated migration file
3. Test the migration: `python migrate.py migrate`
4. Commit both the model changes and migration file

### Data Migrations

For complex data transformations:

1. Create an empty migration: `alembic revision -m "Data migration"`
2. Add custom Python code to transform data
3. Always provide a rollback strategy

## Troubleshooting

### Common Issues

**Migration fails with "table already exists":**
- The database might have tables created outside of migrations
- Use `python migrate.py init` to mark current state as baseline

**Auto-generate doesn't detect changes:**
- Ensure all models are imported in `env.py`
- Check that model changes are saved
- Verify database connection is working

**Rollback fails:**
- Some operations (like dropping columns) may not be reversible
- Check the downgrade function in the migration file
- Consider creating a new migration instead

### Getting Help

1. Check the Alembic documentation: https://alembic.sqlalchemy.org/
2. Review SQLAlchemy documentation: https://docs.sqlalchemy.org/
3. Check the migration manager code in `finx/internal/migration_manager.py`

## Development Workflow

### Initial Setup

```bash
# 1. Set up your database (PostgreSQL/Supabase)
# 2. Configure environment variables
# 3. Initialize migrations
python migrate.py init

# 4. Apply initial schema
python migrate.py migrate
```

### Making Changes

```bash
# 1. Modify your SQLAlchemy models
# 2. Create migration
python migrate.py create "Add new field to User model"

# 3. Review generated migration file
# 4. Apply migration
python migrate.py migrate

# 5. Test your changes
# 6. Commit both model and migration files
```

### Production Deployment

```bash
# 1. Deploy code with new migration files
# 2. Run migrations on production database
python migrate.py migrate

# 3. Verify application works correctly
# 4. Monitor for any issues
```

## Security Considerations

- **Never commit database credentials** to version control
- **Use environment variables** for sensitive configuration
- **Test migrations thoroughly** before production deployment
- **Have a backup strategy** before running migrations on production
- **Encrypt sensitive data** in the database (credentials, etc.)

## File Formats

### JSONField Storage

All JSONField columns are stored as TEXT in the database with JSON serialization. This ensures compatibility across different database backends while maintaining the flexibility of JSON data structures.

### Timestamps

The system uses BigInteger timestamps (Unix epoch) for compatibility with the existing codebase. New tables may use DateTime fields for better database integration.

### Foreign Keys

All foreign key relationships include appropriate CASCADE options to maintain data integrity when parent records are deleted.
