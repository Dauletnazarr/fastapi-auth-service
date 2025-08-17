import uuid

import pytest
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from app.main import app
from fastapi.testclient import TestClient

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@pytest.fixture(scope="session", autouse=True)
def _reset_db_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture()
def unique_email():
    # Уникальная почта на каждый тест
    return f"u_{uuid.uuid4().hex[:8]}@example.com"
