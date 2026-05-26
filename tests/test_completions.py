def test_user_cannot_complete_same_habit_twice_a_day(
        auth_client1, api_habit_factory
        ):
    habit = api_habit_factory(auth_client=auth_client1)
    
    habit_id = habit.json()["id"]

    first_completion = auth_client1.post(f"/habits/{habit_id}/complete")
    assert first_completion.status_code == 201, first_completion.text

    second_completion = auth_client1.post(f"/habits/{habit_id}/complete")
    assert second_completion.status_code == 409, second_completion.text


def test_different_users_can_complete_their_own_habits_with_same_name(
        auth_client1, auth_client2, api_habit_factory
        ):
    habit1 = api_habit_factory(auth_client=auth_client1)

    habit1_id = habit1.json()["id"]
    
    habit2 = api_habit_factory(auth_client=auth_client2)

    habit2_id = habit2.json()["id"]

    completed1_habit = auth_client1.post(f"/habits/{habit1_id}/complete")
    assert completed1_habit.status_code == 201, completed1_habit.text

    completed2_habit = auth_client2.post(f"/habits/{habit2_id}/complete")
    assert completed2_habit.status_code == 201, completed2_habit.text


def test_user_cannot_complete_other_users_habit(
        auth_client1, auth_client2, api_habit_factory
        ):
    habit1 = api_habit_factory(auth_client=auth_client1)

    habit1_id = habit1.json()["id"]

    user2_complete_habit1 = auth_client2.post(f"/habits/{habit1_id}/complete")
    assert user2_complete_habit1.status_code == 404, user2_complete_habit1.text

        
def test_user_can_unmark_only_completed_habit(
        auth_client1, api_habit_factory
        ):
    habit = api_habit_factory(auth_client=auth_client1)    
    
    habit_id = habit.json()["id"]

    unmark_not_completed_habit = auth_client1.delete(
        f"/habits/{habit_id}/complete"
        )
    assert unmark_not_completed_habit.status_code == 409, unmark_not_completed_habit.text

    marked_habit = auth_client1.post(
        f"/habits/{habit_id}/complete"
    )
    assert marked_habit.status_code == 201, marked_habit.text

    unmark_completed_habit = auth_client1.delete(
        f"/habits/{habit_id}/complete"
        )
    assert unmark_completed_habit.status_code == 201, unmark_completed_habit.text


def test_user_cannot_mark_or_unmark_non_existent_habit(auth_client1):
    habit_id = -1

    mark_non_existent_habit = auth_client1.post(
        f"/habits/{habit_id}/complete"
    )
    assert mark_non_existent_habit.status_code == 404, mark_non_existent_habit.text

    unmark_non_existent_habit = auth_client1.delete(
        f"/habits/{habit_id}/complete"
    )
    assert unmark_non_existent_habit.status_code == 404, unmark_non_existent_habit.text

       