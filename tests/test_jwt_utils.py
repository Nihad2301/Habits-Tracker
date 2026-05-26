def test_expired_token(auth_client1, expired_token):
    habit = auth_client1.get(
        "/habits", 
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert habit.status_code == 401, habit.text

def test_missing_sub_field(auth_client1, missing_sub_field):
    habit = auth_client1.get(
        "/habits", 
        headers={"Authorization": f"Bearer {missing_sub_field}"}
    )
    assert habit.status_code == 401, habit.text