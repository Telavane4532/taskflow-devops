const express = require('express');
const app = express();
app.use(express.json());

let tasks = [];

app.get('/tasks', (req, res) => {
  res.json(tasks);
});

app.post('/tasks', (req, res) => {
  const task = { id: Date.now(), title: req.body.title, done: false };
  tasks.push(task);
  res.status(201).json(task);
});

app.patch('/tasks/:id/done', (req, res) => {
  const task = tasks.find(t => t.id === Number(req.params.id));
  if (!task) return res.status(404).json({ error: 'Task not found' });
  task.done = true;
  res.json(task);
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => console.log(`TaskFlow running on port ${PORT}`));
}

module.exports = app;