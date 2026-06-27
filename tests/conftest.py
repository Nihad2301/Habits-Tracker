import pytest
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from core.jwt_utils import make_access_token, SECRET_KEY, ALGORITHM
from datetime import timedelta

from main import app
from db.session import Base, get_db
from db.models.core_models.email_verification_token_model import EmailVerificationToken

@pytest.fixture
def db_session(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    api_test_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    Base.metadata.create_all(bind=engine)

    test_db = api_test_session()
    try: 
        yield test_db
    finally:
        test_db.close()

@pytest.fixture
def test_db(db_session):
    def override_get_db():
        db = db_session
        try: 
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client1(test_db):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def client2(test_db):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_client1(client1, db_session):
    user_payload1 = {
        "username": "test_user1", 
        "password": "test_password1",
        "email": "test_user1@example.com"
    }
    register_user = client1.post("/register", json=user_payload1)
    email_verification_token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_user.json()["id"]
    ).first().token
    login_user = client1.post("/login", json=user_payload1)
    verification_response = client1.get(f"/verify-email?token={email_verification_token}")
    
    jwt_token = login_user.json()["access_token"]
    client1.headers = {"Authorization": f"Bearer {jwt_token}"}

    return client1    

@pytest.fixture
def auth_client2(client2, db_session):
    user_payload2 = {
        "username": "test_user2", 
        "password": "test_password2",
        "email": "test_user2@example.com"
    }
    register_user = client2.post("/register", json=user_payload2)
    email_verification_token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_user.json()["id"]
    ).first().token
    login_user = client2.post("/login", json=user_payload2)
    verification_response = client2.get(f"/verify-email?token={email_verification_token}")
    
    jwt_token = login_user.json()["access_token"]
    client2.headers = {"Authorization": f"Bearer {jwt_token}"}
    
    return client2

@pytest.fixture
def unauthenticated_client(test_db):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def api_habit_factory():
    def _api_habit_factory(*, auth_client):    
        habit_payload = {
            "name": "Test Habit", 
            "description": "Test Description", 
            "frequency": "Every day"
            }
        
        habit = auth_client.post("/habits", json=habit_payload)

        data = habit.json()
        print("DEBUG: habit response", data)
        assert data["id"] is not None
        for key, value in habit_payload.items():
            assert data[key] == value 
            
        return habit
    return _api_habit_factory

@pytest.fixture
def test_empty_or_missing_value():
    def habit_payload(*, error_type: str):
        if "empty" in error_type.lower():
            payload = {
            "name": "",
            "description": "Something"
        }
        elif "missing" in error_type.lower():
            payload = {
            "name": "Some Value"
        }
        
        return payload
    return habit_payload

@pytest.fixture
def assert_status_code():
    def _assert_status_code(response, status_code):
        assert response.status_code == status_code, response.text
    return _assert_status_code    

@pytest.fixture
def expired_token():
    token = make_access_token(data={"sub": "1"}, expires_delta=timedelta(seconds=-1))
    return token  

@pytest.fixture
def missing_sub_field():
    def _missing_sub_field():
        # Create a valid JWT payload without 'sub' field
        payload = {
            "exp": 9999999999,  # Far future expiration
            # No 'sub' field - this is what we're testing
        }
        
        # Encode as JWT without 'sub' field
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token    
    return _missing_sub_field
