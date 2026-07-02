from fastapi.testclient import TestClient


def test_admin_can_reassign_task_owner(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    task = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Triage production alert",
            "description": "Move ownership to the on-call engineer",
            "priority": "high",
            "owner": "alice@example.com",
        },
    ).json()

    response = client.post(
        f"/api/v1/tasks/admin/{task['id']}/reassign",
        headers=auth_headers,
        json={"owner": "oncall@example.com", "reason": "On-call rotation changed"},
    )

    assert response.status_code == 200
    assert response.json()["owner"] == "oncall@example.com"

    get_response = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers)
    assert get_response.json()["owner"] == "oncall@example.com"
