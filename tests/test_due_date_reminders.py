from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def test_overdue_reminders_return_open_tasks_past_due(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    now = datetime.now(UTC)
    overdue = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Follow up on blocked task",
            "description": "Ping the owner about the overdue item",
            "priority": "high",
            "owner": "manager@example.com",
            "due_at": (now - timedelta(days=2)).isoformat(),
        },
    ).json()
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Future planning",
            "description": "Review tomorrow",
            "priority": "low",
            "owner": "manager@example.com",
            "due_at": (now + timedelta(days=1)).isoformat(),
        },
    )

    response = client.get("/api/v1/tasks/reminders/overdue", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["task_id"] == overdue["id"]
    assert payload["items"][0]["owner"] == "manager@example.com"
