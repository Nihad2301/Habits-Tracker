from db.models.core_models.email_verification_token_model import EmailVerificationToken

def test_verification_token_generated_on_registration(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False

def test_verify_email_with_valid_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_response.json()["id"]
    ).first()
    assert token is not None
    assert token.is_used == False
    assert register_response.json().get("is_verified") == False
    
    verification_response = unauthenticated_client.get(f"/verify-email?token={token.token}")
    assert verification_response.status_code == 200

    token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_response.json()["id"]
    ).first()
    assert token.is_used == True
    
    assert verification_response.json().get("is_verified") == True
    
def test_verify_email_with_invalid_token(auth_client1):
    verification_response = auth_client1.get("/verify-email?token=invalid_token")
    assert verification_response.status_code == 404

def test_verify_email_with_expired_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register?expires_at=-1", json=register_payload)
    token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_response.json()["id"]
    ).first()
    verification_response = unauthenticated_client.get(f"/verify-email?token={token.token}")
    assert verification_response.status_code == 401

def test_verify_email_with_already_used_token(db_session, unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201

    token = db_session.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == register_response.json()["id"]
    ).first()
    
    verification_response = unauthenticated_client.get(f"/verify-email?token={token.token}")
    assert verification_response.status_code == 200
Please provide all the commands in a single message so I can paste them into my terminal at once instead of copying and pasting multiple times.
    
    verification_response = unauthenticated_client.get(f"/verify-email?token={token.token}")
    assert verification_response.status_code == 409

def test_verify_email_with_nonexistent_token(unauthenticated_client):
    register_payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_response = unauthenticated_client.post("/register", json=register_payload)
    assert register_response.status_code == 201
    
    verification_response = unauthenticated_client.get("/verify-email?token=nonexistent_token")
    assert verification_response.status_code == 404