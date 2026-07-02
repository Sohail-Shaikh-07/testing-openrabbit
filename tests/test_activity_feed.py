from fastapi.testclient import TestClient


def test_activity_feed_shows_recent_task_events(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Draft review notes",
            "description": "Summarize latest branch changes",
            "priority": "medium",
            "owner": "reviewer@example.com",
        },
    ).json()

    client.patch(
        f"/api/v1/tasks/{created['id']}",
        headers=auth_headers,
        json={"status": "in_progress"},
    )

    response = client.get("/api/v1/tasks/activity", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["task_id"] == created["id"]
    assert payload["items"][0]["status"] == "in_progress"
    assert payload["items"][0]["event_type"] == "task_updated"
