def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_me(client):
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": "linus@example.com", "password": "password123", "name": "Linus"},
    )
    assert registered.status_code == 201
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {registered.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "linus@example.com"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "linus@example.com", "password": "password123"},
    )
    assert login.status_code == 200

    bad = client.post(
        "/api/v1/auth/login",
        json={"email": "linus@example.com", "password": "wrongpass"},
    )
    assert bad.status_code == 401


def test_duplicate_register(auth_client):
    again = auth_client.post(
        "/api/v1/auth/register",
        json={"email": "ada@example.com", "password": "password123", "name": "Ada"},
    )
    assert again.status_code == 409


def test_workspaces_and_workflows(auth_client):
    spaces = auth_client.get("/api/v1/workspaces")
    assert spaces.status_code == 200
    assert len(spaces.json()) >= 1
    workspace_id = spaces.json()[0]["id"]

    created = auth_client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "Lead capture",
            "description": "Webhook to log",
            "graph": {
                "nodes": [
                    {
                        "id": "t1",
                        "type": "manual_trigger",
                        "name": "Start",
                        "config": {},
                        "position": {"x": 0, "y": 0},
                    },
                    {
                        "id": "l1",
                        "type": "log",
                        "name": "Log payload",
                        "config": {"message": "hello {{trigger.name}}"},
                        "position": {"x": 240, "y": 0},
                    },
                    {
                        "id": "e1",
                        "type": "end",
                        "name": "End",
                        "config": {},
                        "position": {"x": 480, "y": 0},
                    },
                ],
                "edges": [
                    {"id": "e-t-l", "source": "t1", "target": "l1"},
                    {"id": "e-l-e", "source": "l1", "target": "e1"},
                ],
            },
        },
    )
    assert created.status_code == 201, created.text
    workflow_id = created.json()["id"]

    published = auth_client.post(f"/api/v1/workflows/{workflow_id}/publish")
    assert published.status_code == 200, published.text
    assert published.json()["workflow"]["status"] == "active"

    run = auth_client.post(
        f"/api/v1/workflows/{workflow_id}/run",
        json={"input": {"name": "Ada"}},
    )
    assert run.status_code == 202, run.text
    assert run.json()["status"] in {"pending", "running", "completed"}

    details = auth_client.get(f"/api/v1/runs/{run.json()['id']}")
    assert details.status_code == 200
    assert details.json()["status"] == "completed"
    assert details.json()["workflow_version_id"] == created.json()["current_version_id"]

    stats = auth_client.get("/api/v1/dashboard/stats")
    assert stats.status_code == 200
    assert stats.json()["total_workflows"] >= 1
    assert stats.json()["successful_runs"] >= 1


def test_rejects_inline_secrets(auth_client):
    workspace_id = auth_client.get("/api/v1/workspaces").json()[0]["id"]
    response = auth_client.post(
        "/api/v1/workflows",
        json={
            "workspace_id": workspace_id,
            "name": "bad",
            "graph": {
                "nodes": [
                    {
                        "id": "t1",
                        "type": "llm",
                        "name": "LLM",
                        "config": {"api_key": "sk-secret", "prompt": "hi"},
                        "position": {"x": 0, "y": 0},
                    }
                ],
                "edges": [],
            },
        },
    )
    assert response.status_code == 422
