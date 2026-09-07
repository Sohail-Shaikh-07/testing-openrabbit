from fastapi.testclient import TestClient


def test_advanced_search_filters_by_keyword_and_owner(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Prepare launch checklist",
            "description": "Coordinate API release tasks",
            "priority": "high",
            "owner": "launch@example.com",
        },
    )
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Prepare billing checklist",
            "description": "Review invoice task owners",
            "priority": "medium",
            "owner": "billing@example.com",
        },
    )

    response = client.get(
        "/api/v1/tasks/search/advanced?q=checklist&owner=launch@example.com",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["owner"] == "launch@example.com"
