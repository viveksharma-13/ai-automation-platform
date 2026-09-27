# AI Automation Platform

AI-powered workflow automation platform for building, managing, and executing intelligent workflows through a visual web interface and scalable backend.

> **Status:** Active development

## Overview

The platform provides a visual workflow builder backed by a FastAPI execution engine. Workflows are represented as validated node-and-edge graphs, stored with version history, and executed through a backend worker architecture.

## Features

- Visual workflow editor with React Flow
- Manual and webhook triggers
- HTTP request nodes
- LLM nodes using the OpenAI API
- Conditional true/false branching
- Delay and logging nodes
- Workflow save, publish, versioning, and execution
- Workflow run history
- Cron-based scheduling
- Webhook endpoints
- User registration and login
- Workspace-based workflows and credentials
- Credential encryption configuration
- Graph validation before execution
- Node retries and timeout handling
- Execution cancellation support
- PostgreSQL persistence
- Redis + Celery asynchronous processing
- Docker Compose development environment
- Backend tests

## Architecture

```text
Next.js + React Flow
        |
        | REST API
        v
     FastAPI
     /      \
PostgreSQL  Redis
              |
           Celery Worker
              |
       Workflow Engine
              |
  Trigger / HTTP / LLM / Condition
       / Delay / Log / End
```

## Workflow Nodes

| Node | Purpose |
|---|---|
| Manual Trigger | Starts a workflow manually |
| Webhook Trigger | Starts a workflow through an HTTP webhook |
| HTTP Request | Calls an external HTTP endpoint |
| LLM | Executes an LLM-powered step |
| Condition | Routes execution through true/false branches |
| Delay | Pauses execution |
| Log | Records an execution message |
| End | Terminates the workflow |

## Execution Engine

The workflow engine validates graphs, determines entry nodes, resolves node handlers, executes nodes, applies mappings, handles conditional branches, supports retries and timeout checks, and records node outputs. A maximum step limit helps prevent runaway cyclic execution.

## Tech Stack

### Frontend
- Next.js 15
- React 19
- TypeScript
- React Flow
- Tailwind CSS
- Lucide React

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- OpenAI API
- JWT authentication
- Fernet-based credential encryption

### Development
- Docker / Docker Compose
- Pytest
- Ruff
- ESLint
- Prettier
- TypeScript

## Project Structure

```text
ai-automation-platform/
├── apps/
│   ├── api/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── security/
│   │   │   ├── services/
│   │   │   └── workflow/
│   │   ├── alembic/
│   │   └── pyproject.toml
│   └── web/                 # Next.js frontend
│       ├── src/
│       └── package.json
├── infra/docker/            # Dockerfiles
├── packages/shared/         # Shared definitions
├── tests/backend/           # Backend tests
├── workers/worker/          # Celery worker
├── docker-compose.yml
├── .env.example
├── .gitignore
└── LICENSE
```

## Getting Started

### Prerequisites

- Git
- Python 3.11+
- Node.js
- Docker Desktop with Docker Compose

### Clone

```bash
git clone https://github.com/viveksharma-13/ai-automation-platform.git
cd ai-automation-platform
```

### Configure environment

```bash
cp .env.example .env
```

Set strong values for `JWT_SECRET` and `CREDENTIALS_ENCRYPTION_KEY`.

For LLM nodes, configure:

```env
OPENAI_API_KEY=your_api_key
OPENAI_DEFAULT_MODEL=gpt-4o-mini
```

Never commit `.env` or real credentials.

### Run with Docker

```bash
docker compose up --build
```

Default endpoints:

| Service | Address |
|---|---|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Stop:

```bash
docker compose down
```

Remove development database volume:

```bash
docker compose down -v
```

## Backend Development

```bash
cd apps/api
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install:

```bash
pip install -e ".[dev]"
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend Development

```bash
cd apps/web
npm install
npm run dev
```

Useful commands:

```bash
npm run build
npm run lint
npm run typecheck
```

## Testing

Backend tests are under `tests/backend/`.

```bash
cd apps/api
pytest
```

The test suite includes workflow execution, template interpolation, and conditional branching tests.

## API Overview

The API is versioned under `/api/v1`.

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Workflows

```text
POST   /api/v1/workflows
GET    /api/v1/workflows
GET    /api/v1/workflows/{workflow_id}
PATCH  /api/v1/workflows/{workflow_id}
DELETE /api/v1/workflows/{workflow_id}

POST /api/v1/workflows/{workflow_id}/publish
POST /api/v1/workflows/{workflow_id}/versions
POST /api/v1/workflows/{workflow_id}/run
```

### Runs

```text
GET /api/v1/runs
GET /api/v1/runs/{run_id}
```

### Credentials

```text
POST /api/v1/workspaces/{workspace_id}/credentials
GET  /api/v1/workspaces/{workspace_id}/credentials
```

Interactive documentation is available at:

```text
http://localhost:8000/docs
```

## Security

The workflow DSL prevents secrets such as API keys, passwords, tokens, and authorization values from being embedded directly in node configuration. Credentials are intended to be referenced separately. The execution engine also validates graph structure and enforces a maximum step limit.

For production use, replace all development secrets with securely generated and managed values.

## Roadmap

- More workflow integrations
- Additional AI/LLM providers
- Richer execution observability
- Expanded scheduling controls
- Broader automated test coverage
- CI/CD automation
- Production deployment configurations
- Advanced workflow validation
- Human approval/intervention nodes

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Vivek Sharma**

GitHub: https://github.com/viveksharma-13

---

Built as a full-stack AI engineering project combining workflow orchestration, LLM integration, backend APIs, asynchronous processing, databases, and a visual workflow editor.
