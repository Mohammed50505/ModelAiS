# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL. This will create a file named "sql_app.db" in your project directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite to allow multiple threads
# to interact with the database, which FastAPI (and Uvicorn) often do.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
# The `autocommit=False` means changes won't be saved automatically.
# The `autoflush=False` means changes won't be flushed to the database automatically on query.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

# Dependency to get a database session for each request
# This function will be called for each request that needs a database session.
# It creates a new session, yields it, and then closes it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
