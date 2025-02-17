from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextvars import ContextVar
import time

# Use ContextVar for thread-safe query duration tracking
query_duration = ContextVar("query_duration", default=0.0)

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/playstore"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    start_time = conn.info.get("query_start_time", None)
    if start_time is not None:
        total = (time.time() - start_time) * 1000 
        query_duration.set(round(total,2))

def get_last_query_duration():
    return query_duration.get()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
