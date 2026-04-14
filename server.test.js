const request = require('supertest');
const app = require('./server');

test('GET /health returns ok', async () => {
  const res = await request(app).get('/health');
  expect(res.statusCode).toBe(200);
  expect(res.body.status).toBe('ok');
});

test('POST /tasks creates a task', async () => {
  const res = await request(app).post('/tasks').send({ title: 'Learn DevOps' });
  expect(res.statusCode).toBe(201);
  expect(res.body.title).toBe('Learn DevOps');
});

test('GET /ai/roles returns available job roles', async () => {
  const res = await request(app).get('/ai/roles');
  expect(res.statusCode).toBe(200);
  expect(Array.isArray(res.body)).toBe(true);
  expect(res.body.length).toBeGreaterThan(0);
});

test('POST /ai/recommendations analyzes resume and returns ranked matches', async () => {
  const resumeText = `
    Python developer with Django project experience.
    Built REST API services with MySQL and Docker.
    Wrote tests using pytest and collaborated with Git.
  `;

  const res = await request(app).post('/ai/recommendations').send({ resumeText });
  expect(res.statusCode).toBe(200);
  expect(res.body.extractedSkills).toContain('python');
  expect(res.body.extractedSkills).toContain('django');
  expect(res.body.extractedSkills).toContain('sql');
  expect(res.body.recommendations[0].role).toBe('Backend Python Developer');
});

test('POST /ai/recommendations supports direct skill input and returns skill gaps', async () => {
  const res = await request(app).post('/ai/recommendations').send({
    skills: ['Manual QA', 'Selenium', 'Jira']
  });

  expect(res.statusCode).toBe(200);
  expect(res.body.recommendations[0].category).toBe('QA');
  expect(Array.isArray(res.body.skillGapSummary)).toBe(true);
  expect(res.body.skillGapSummary.length).toBeGreaterThan(0);
});

test('POST /ai/recommendations returns 400 for empty payload', async () => {
  const res = await request(app).post('/ai/recommendations').send({});
  expect(res.statusCode).toBe(400);
  expect(res.body.error).toContain('Provide resumeText or skills');
});
