def test_get_habit_analytics(auth_client1, api_habit_factory):
    habit = api_habit_factory(auth_client=auth_client1)
    habit_id = habit.json().get("data").get("id")
    marked_habit = auth_client1.post(f"/habits/{habit_id}/complete")
    assert marked_habit.status_code == 201

    analytics = auth_client1.get(f"/habits/{habit_id}/analytics")
    print("DEBUG: analytics response", analytics.json())
    assert analytics.status_code == 200
    data = analytics.json().get("data")
    assert data.get("completion_rate") is not None
    assert data.get("streak_days") is not None
    assert data.get("longest_streak") is not None
    assert data.get("average_completion_time") is not None
    assert data.get("total_completions") is not None

def test_get_weekly_stats(auth_client1, api_habit_factory):
    habit = api_habit_factory(auth_client=auth_client1)
    habit_id = habit.json().get("data").get("id")
    marked_habit = auth_client1.post(f"/habits/{habit_id}/complete")
    assert marked_habit.status_code == 201

    stats = auth_client1.get(f"/habits/{habit_id}/weekly-stats")
    print("DEBUG: weekly-stats response", stats.json())
    assert stats.status_code == 200
    
    data = stats.json().get("data")
    for item in data:
        assert item.get("week_start") is not None
        assert item.get("days_with_completions") is not None
   

def test_get_monthly_stats(auth_client1, api_habit_factory):
    habit = api_habit_factory(auth_client=auth_client1)
    habit_id = habit.json().get("data").get("id")
    marked_habit = auth_client1.post(f"/habits/{habit_id}/complete")
    assert marked_habit.status_code == 201

    stats = auth_client1.get(f"/habits/{habit_id}/monthly-stats")
    print("DEBUG: monthly-stats response", stats.json())
    assert stats.status_code == 200
    data = stats.json().get("data")
    for item in data:
        assert item.get("month_start") is not None
        assert item.get("days_with_completions") is not None

def test_analytics_unauthorized(unauthenticated_client, auth_client1, api_habit_factory):
    habit = api_habit_factory(auth_client=auth_client1)
    habit_id = habit.json().get("data").get("id")

    analytics = unauthenticated_client.get(f"/habits/{habit_id}/analytics")
    assert analytics.status_code == 403

def test_analytics_other_users_habit(auth_client1, auth_client2, api_habit_factory):
    habit = api_habit_factory(auth_client=auth_client1)
    habit_id = habit.json().get("data").get("id")

    analytics = auth_client2.get(f"/habits/{habit_id}/analytics")
    assert analytics.status_code == 403