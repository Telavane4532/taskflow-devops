# TaskFlow Django AI Service

Django microservice providing AI-enabled task management APIs.

## Features
- Django + DRF APIs
- JWT authentication
- PostgreSQL/SQLite support
- Redis + Celery async tasks
- AI endpoints: summarize, prioritize, parse task text, similar task retrieval
- Basic moderation, feature flags, quota and throttling
- Structured JSON logging

## Quick start
```bash
cd /home/runner/work/taskflow-devops/taskflow-devops/django_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## API overview
- `POST /api/users/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /health/`
- CRUD:
  - `/api/projects/`
  - `/api/tasks/`
  - `/api/comments/`
  - `/api/activity/`
- AI:
  - `POST /api/ai/summarize/`
  - `POST /api/ai/prioritize/`
  - `POST /api/ai/parse-task/`
  - `POST /api/ai/similar/<task_id>/`

## Environment variables
See `.env.example`.
