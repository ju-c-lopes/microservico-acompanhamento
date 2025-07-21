"""
Production Alembic environment.
This handles MySQL database migrations for production/staging environments.
These migrations ARE committed to repository.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_database_url():
    """
    Get database URL for production environment.
    Expects MySQL database URL and converts async to sync for Alembic.
    """
    # Check environment variable first (production usage)
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        # Convert async MySQL to sync for Alembic
        if "aiomysql" in env_url:
            env_url = env_url.replace("mysql+aiomysql://", "mysql+pymysql://")
        return env_url

    # Fall back to alembic config
    config_url = config.get_main_option("sqlalchemy.url")
    if config_url:
        return config_url

    # This should not happen in production
    raise ValueError(
        "DATABASE_URL must be set for production migrations. "
        "Expected MySQL URL format: mysql+aiomysql://user:pass@host:port/db"
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode for production."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode for production MySQL."""
    database_url = get_database_url()

    # Override the alembic config with our dynamic URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url

    # MySQL-specific configuration for production
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Standard for MySQL production
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
