from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
from .config import settings

class Base(DeclarativeBase):
    pass

db_url = settings.database_url

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, pool_pre_ping=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
