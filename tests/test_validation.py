def test_cannot_create_habit_with_empty_or_missing_name(
    test_empty_or_missing_value, auth_client1, auth_client2
    ):
    habit1 = test_empty_or_missing_value(
        error_type="empty"
       )
    habit2 = test_empty_or_missing_value(
        error_type="missing"
        )

    data1 = auth_client1.post("/habits", json=habit1)
    data2 = auth_client2.post("/habits", json=habit2)
    assert data1.status_code == 422, data1.text
    assert data2.status_code == 422, data2.text