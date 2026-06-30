from db.models.core_models.password_reset_token_model import PasswordResetToken
from db.models.core_models.user_model import User
from services.auth_service import hash_password, verify_password
def test_password_reset_token_generated_on_request(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201
    
    password_reset_request_response = unauthenticated_client.post(
        "reset-password/request?email=test_user@example.com"
    )
    assert password_reset_request_response.status_code == 200
    
    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False

def test_reset_password_confirm(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201
    
    password_reset_request_response = unauthenticated_client.post(
        "reset-password/request?email=test_user@example.com"
    )
    assert password_reset_request_response.status_code == 200
    
    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False

    old_hashed_password = token.user.hashed_password
    
    password_reset_confirm_response = unauthenticated_client.post(
        f"reset-password/confirm?token={token.token}&new_password=test_password2"
    )
    assert password_reset_confirm_response.status_code == 200
    
    user = db_session.query(User).filter(
        User.id == register_response.json()["id"]
    ).first()
    assert user is not None
    assert not verify_password("test_password", user.hashed_password)
    assert verify_password("test_password2", user.hashed_password)
    
def test_reset_password_confirm_invalid_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201
    
    password_reset_confirm = unauthenticated_client.post(
        "reset-password/confirm?token=invalid_token&new_password=test_password2"
    )
    assert password_reset_confirm.status_code == 404

def test_reset_password_confirm_with_expires_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    password_reset_request_response = unauthenticated_client.post(
        "reset-password/request?email=test_user@example.com&expires_at=-1"
    )
    assert password_reset_request_response.status_code == 200
    
    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False
    
    password_reset_confirm_response = unauthenticated_client.post(
        f"reset-password/confirm?token={token.token}&new_password=test_password2"
    )
    assert password_reset_confirm_response.status_code == 401

def test_reset_password_confirm_with_used_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    password_reset_request_response = unauthenticated_client.post(
        "reset-password/request?email=test_user@example.com"
    )
    assert password_reset_request_response.status_code == 200
    
    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False
    
    password_reset_confirm_response = unauthenticated_client.post(
        f"reset-password/confirm?token={token.token}&new_password=test_password2"
    )
    assert password_reset_confirm_response.status_code == 200

    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token.is_used == True
    
    password_reset_confirm_response = unauthenticated_client.post(
        f"reset-password/confirm?token={token.token}&new_password=test_password3"
    )
    assert password_reset_confirm_response.status_code == 409

def test_reset_password_confirm_with_weak_password(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    password_reset_request_response = unauthenticated_client.post(
        "reset-password/request?email=test_user@example.com"
    )
    assert password_reset_request_response.status_code == 200
    
    token = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False
    
    password_reset_confirm_response = unauthenticated_client.post(
        f"reset-password/confirm?token={token.token}&new_password=test"
    )
    assert password_reset_confirm_response.status_code == 400
    

  

