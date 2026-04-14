# TaskFlow DevOps

Simple Express API for task tracking with an AI-powered job recommendation module.

## Run

```bash
npm install
npm test
npm start
```

## Existing Endpoints

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/:id/done`

## AI Job Recommendation Endpoints

### `GET /ai/roles`

Returns seeded job roles and their required/preferred skills.

### `POST /ai/recommendations`

Analyzes `resumeText` and/or `skills` and returns:

- extracted normalized skills
- top role recommendations with score and confidence
- skill-gap summary with learning recommendations

Example request:

```json
{
  "resumeText": "Python Django developer with SQL and REST API experience",
  "skills": ["Git", "Docker"]
}
```
