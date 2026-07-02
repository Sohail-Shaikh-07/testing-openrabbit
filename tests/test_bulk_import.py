from fastapi.testclient import TestClient


def test_bulk_import_creates_tasks_from_csv(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    csv_body = (
        "title,description,owner,priority\n"
        "Review queue,Check incoming pull requests,qa@example.com,high\n"
        "Write notes,Summarize review outcomes,qa@example.com,medium\n"
    )

    response = client.post(
        "/api/v1/tasks/import/csv",
        headers={**auth_headers, "Content-Type": "text/csv"},
        content=csv_body,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["created"] == 2
    assert [item["title"] for item in payload["items"]] == [
        "Review queue",
        "Write notes",
    ]
