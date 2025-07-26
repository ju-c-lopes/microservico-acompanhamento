from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
import os
import sys
from app.db.base import Acompanhamento

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
config = context.config
fileConfig(config.config_file_name)

# DATABASE_URL = os.getenv("DATABASE_URL")  # Já está setado no alembic.ini

target_metadata = Acompanhamento.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    db_url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
