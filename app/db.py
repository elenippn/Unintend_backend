import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unintend.db")

connect_args: dict | None = None
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # SQLite requirement

engine = create_engine(DATABASE_URL, connect_args=connect_args or {})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
