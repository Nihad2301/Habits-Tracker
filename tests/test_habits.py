def test_same_user_cannot_build_duplicate_habit_name(
    auth_client1, api_habit_factory, assert_status_code
):
    habit1 = api_habit_factory(auth_client=auth_client1)
    assert_status_code(response=habit1, status_code=201)

    # Test duplicate habit creation using direct POST request
    # api_habit_factory includes assertions that expect 201 response
    # When duplicate fails (409), factory assertions would fail
    # Direct POST allows testing actual 409 error response
    habit2 = auth_client1.post("/habits", json={
        "name": "Test Habit",  
        "description": "Test Description", 
        "frequency": "daily"
    })  
    assert_status_code(response=habit2, status_code=409)


def test_different_users_can_build_same_habit_name(
    auth_client1, auth_client2, api_habit_factory, 
    assert_status_code
):
    # First user creates habit
    habit1 = api_habit_factory(auth_client=auth_client1)
    assert_status_code(response=habit1, status_code=201)

    # Second user (different auth_client) creates same habit name
    # This should work because they're different users
    habit2 = api_habit_factory(auth_client=auth_client2)
    assert_status_code(response=habit2, status_code=201)


def test_user_cannot_access_other_users_habit(
    auth_client1, auth_client2, api_habit_factory, 
    assert_status_code
):
    habit1 = api_habit_factory(auth_client=auth_client1)
    assert_status_code(response=habit1, status_code=201)

    # User2 tries to access user1's habit
    habit_id = habit1.json().get("data").get("id")
    fetched = auth_client2.get(f"/habits/{habit_id}")
    assert fetched.status_code == 403, fetched.text


