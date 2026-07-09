def test_register_user(unauthenticated_client):
    user_payload = {
        "username": "test_user", 
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_user = unauthenticated_client.post("/register", json=user_payload)
    assert register_user.status_code == 201

def test_register_duplicate_username(unauthenticated_client):
    user_payload = {
        "username": "test_user", 
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_user = unauthenticated_client.post("/register", json=user_payload)
    assert register_user.status_code == 201

    # Try to register the same user again
    register_user = unauthenticated_client.post("/register", json=user_payload)
    assert register_user.status_code == 409

def test_login_success(unauthenticated_client):
    user_payload = {
        "username": "test_user", 
        "password": "test_password",
        "email": "test_user@example.com"
    }
    register_user = unauthenticated_client.post("/register", json=user_payload)
    assert register_user.status_code == 201
    login_user = unauthenticated_client.post("/login", json=user_payload)
    assert login_user.status_code == 200
    assert "access_token" in login_user.json().get("data")

def test_login_invalid_credentials(unauthenticated_client):
    correct_payload = {
        "username": "test_user", 
        "password": "correct_password",
        "email": "test_user@example.com"
    }
    wrong_payload = {
        "username": "test_user", 
        "password": "wrong_password",
        "email": "test_user@example.com"
    }

    register_user = unauthenticated_client.post("/register", json=correct_payload)
    assert register_user.status_code == 201
    login_user = unauthenticated_client.post("/login", json=wrong_payload)
    assert login_user.status_code == 401

def test_login_nonexistent_user(unauthenticated_client):
    user_payload = {
        "username": "nonexistent_user", 
        "password": "test_password",
        "email": "nonexistent_user@example.com"
    }
    login_user = unauthenticated_client.post("/login", json=user_payload)
    assert login_user.status_code == 404


    