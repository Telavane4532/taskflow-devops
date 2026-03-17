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