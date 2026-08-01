from fastapi.testclient import TestClient


def test_create_and_get_task(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Write review harness",
            "description": "Seed a realistic pull request review testbed",
            "priority": "high",
            "owner": "alice@example.com",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Write review harness"
    assert created["status"] == "todo"
    assert created["owner"] == "alice@example.com"

    get_response = client.get(f"/api/v1/tasks/{created['id']}", headers=auth_headers)

    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


def test_create_task_trims_text_fields(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    longest_title = "x" * 120
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": f"  {longest_title}  ",
            "description": "  Exercise the full command surface.  ",
            "owner": "  alice@example.com  ",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == longest_title
    assert payload["description"] == "Exercise the full command surface."
    assert payload["owner"] == "alice@example.com"


def test_task_text_fields_reject_whitespace_only_values(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "   ",
            "description": "Validation task",
            "owner": "alice@example.com",
        },
    )

    assert create_response.status_code == 422

    short_owner_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Validation task",
            "description": "Exercise owner validation",
            "owner": " a ",
        },
    )

    assert short_owner_response.status_code == 422

    valid_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Validation task",
            "description": "Exercise update validation",
            "owner": "alice@example.com",
        },
    )
    task_id = valid_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"description": "\t\n"},
    )

    assert update_response.status_code == 422


def test_list_tasks_supports_pagination_and_status_filter(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    for index in range(4):
        client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={
                "title": f"Task {index}",
                "description": "A task in the backlog",
                "priority": "medium",
                "owner": "alice@example.com",
            },
        )

    response = client.get(
        "/api/v1/tasks?status=todo&limit=2&offset=1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) == 2


def test_complete_task_records_status(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Ship base repository",
            "description": "Push the main branch",
            "priority": "low",
            "owner": "alice@example.com",
        },
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_search_tasks_matches_title_and_description(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Review OpenRabbit findings",
            "description": "Check the generated pull request comments",
            "priority": "high",
            "owner": "alice@example.com",
        },
    )
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Pay invoices",
            "description": "Monthly finance task",
            "priority": "medium",
            "owner": "billing@example.com",
        },
    )

    response = client.get("/api/v1/tasks/search?q=openrabbit", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["title"] == "Review OpenRabbit findings"


def test_task_routes_require_token(client: TestClient) -> None:
    response = client.get("/api/v1/tasks")

    assert response.status_code == 401
