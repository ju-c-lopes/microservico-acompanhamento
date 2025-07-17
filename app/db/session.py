import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: Define SECRETS in Github Actions
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", None)
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. Please configure it before running the application."
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
