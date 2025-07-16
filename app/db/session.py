from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# TODO: Define SECRETS in Github Actions
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://usuario:senha@endpoint-do-rds:3306/nome_do_banco")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
