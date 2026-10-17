import os
import sys
import types

os.environ["DATABASE_URL"] = "sqlite:///./test_authorization.db"
os.environ["SECRET_KEY"] = "test-secret"

embedding = types.ModuleType("app.services.embeddings.embedding_service")
embedding.generate_embedding = lambda text: [0.0] * 1024
sys.modules[embedding.__name__] = embedding

store = types.ModuleType("app.vectorstore.faiss_store")
store.add_embedding = lambda embedding, resume_id: None
store.search_embedding = lambda query_embedding, top_k=5: []
sys.modules[store.__name__] = store

semantic = types.ModuleType("app.services.embeddings.semantic_search")
semantic.semantic_resume_search = lambda query: []
sys.modules[semantic.__name__] = semantic

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.resume import Resume
from app.models.user import User

TEST_ENGINE = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)

@pytest.fixture()
def client(db):
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def make_user(db, email, role):
    from app.core.security import hash_password
    user = User(username=email.split("@")[0], email=email, hashed_password=hash_password("password123"), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return user

@pytest.fixture()
def users(db):
    recruiter = make_user(db, "recruiter@example.com", "recruiter")
    other = make_user(db, "other@example.com", "recruiter")
    candidate = make_user(db, "candidate@example.com", "candidate")
    db.add_all([Resume(filename="owned.pdf", extracted_text="owned", skills="Python", owner_id=recruiter.id), Resume(filename="other.pdf", extracted_text="other", skills="Go", owner_id=other.id), Resume(filename="legacy.pdf", extracted_text="legacy", skills="Rust")])
    db.commit()
    return recruiter, other, candidate

def token(client, email):
    response = client.post("/auth/login", data={"username": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()["access_token"]
