const express = require('express');
const app = express();
app.use(express.json());

let tasks = [];

const SKILL_ALIASES = {
  python: ['python'],
  django: ['django'],
  flask: ['flask'],
  'node.js': ['node.js', 'nodejs', 'node'],
  react: ['react', 'reactjs'],
  sql: ['sql', 'mysql', 'postgresql', 'postgres'],
  pandas: ['pandas'],
  'machine learning': ['machine learning', 'ml'],
  'data analysis': ['data analysis', 'analytics'],
  'manual testing': ['manual testing', 'manual qa'],
  selenium: ['selenium'],
  pytest: ['pytest'],
  jest: ['jest'],
  docker: ['docker'],
  kubernetes: ['kubernetes', 'k8s'],
  git: ['git'],
  jira: ['jira'],
  communication: ['communication', 'teamwork'],
  'problem solving': ['problem solving', 'critical thinking'],
  'rest api': ['rest api', 'restful api', 'api development'],
  'api testing': ['api testing', 'postman']
};

const JOB_ROLES = [
  {
    role: 'Backend Python Developer',
    category: 'Python',
    requiredSkills: ['python', 'django', 'sql', 'rest api'],
    preferredSkills: ['docker', 'git', 'pytest']
  },
  {
    role: 'Data Analyst Fresher',
    category: 'Data',
    requiredSkills: ['python', 'sql', 'pandas', 'data analysis'],
    preferredSkills: ['machine learning', 'communication', 'problem solving']
  },
  {
    role: 'QA Automation Engineer',
    category: 'QA',
    requiredSkills: ['manual testing', 'selenium', 'api testing'],
    preferredSkills: ['pytest', 'jira', 'git']
  },
  {
    role: 'Frontend React Developer',
    category: 'Web',
    requiredSkills: ['react', 'node.js', 'git'],
    preferredSkills: ['jest', 'rest api', 'communication']
  }
];

const LEARNING_RESOURCES = {
  django: ['Build a CRUD API in Django REST Framework'],
  sql: ['Practice SQL joins, aggregations, and indexing'],
  pandas: ['Complete a mini data-cleaning project using pandas'],
  'machine learning': ['Train and evaluate a simple classification model'],
  selenium: ['Automate 5 browser test scenarios with Selenium'],
  'api testing': ['Create API test collections in Postman'],
  'rest api': ['Design and document REST endpoints with examples'],
  docker: ['Containerize one app with a production-ready Dockerfile'],
  react: ['Build a React dashboard with reusable components'],
  jest: ['Add unit tests for components and API integrations'],
  communication: ['Prepare concise project summaries and demo scripts'],
  'problem solving': ['Solve 20 coding problems focused on fundamentals']
};

function normalizeSkill(skill) {
  const raw = String(skill || '').trim().toLowerCase();
  if (!raw) return null;

  for (const [canonicalSkill, aliases] of Object.entries(SKILL_ALIASES)) {
    if (aliases.includes(raw)) return canonicalSkill;
  }

  return raw;
}

function extractSkillsFromResume(resumeText) {
  const text = String(resumeText || '').toLowerCase();
  const extracted = new Set();

  for (const [canonicalSkill, aliases] of Object.entries(SKILL_ALIASES)) {
    const found = aliases.some((alias) => text.includes(alias));
    if (found) extracted.add(canonicalSkill);
  }

  return Array.from(extracted);
}

function calculateRoleMatch(candidateSkills, role) {
  const candidateSet = new Set(candidateSkills);
  const matchedRequired = role.requiredSkills.filter(skill => candidateSet.has(skill));
  const matchedPreferred = role.preferredSkills.filter(skill => candidateSet.has(skill));
  const missingRequired = role.requiredSkills.filter(skill => !candidateSet.has(skill));
  const missingPreferred = role.preferredSkills.filter(skill => !candidateSet.has(skill));

  const requiredWeight = role.requiredSkills.length
    ? (matchedRequired.length / role.requiredSkills.length) * 80
    : 0;
  const preferredWeight = role.preferredSkills.length
    ? (matchedPreferred.length / role.preferredSkills.length) * 20
    : 0;
  const score = Math.round(requiredWeight + preferredWeight);

  let confidence = 'Low';
  if (score >= 75) confidence = 'High';
  else if (score >= 50) confidence = 'Medium';

  return {
    role: role.role,
    category: role.category,
    score,
    confidence,
    matchedSkills: [...matchedRequired, ...matchedPreferred],
    missingSkills: {
      required: missingRequired,
      preferred: missingPreferred
    }
  };
}

function buildSkillGapSummary(recommendations) {
  const skillPriority = new Map();

  recommendations.forEach((rec) => {
    rec.missingSkills.required.forEach((skill) => {
      skillPriority.set(skill, 'high');
    });
    rec.missingSkills.preferred.forEach((skill) => {
      if (!skillPriority.has(skill)) skillPriority.set(skill, 'medium');
    });
  });

  return Array.from(skillPriority.entries()).map(([skill, importance]) => ({
    skill,
    importance,
    learningResources: LEARNING_RESOURCES[skill] || [`Complete guided practice for ${skill}`]
  }));
}

function getCandidateSkills(inputSkills, resumeText) {
  const normalizedInputSkills = Array.isArray(inputSkills)
    ? inputSkills.map(normalizeSkill).filter(Boolean)
    : [];

  const resumeSkills = extractSkillsFromResume(resumeText);
  return Array.from(new Set([...normalizedInputSkills, ...resumeSkills]));
}

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

app.get('/ai/roles', (req, res) => {
  res.json(JOB_ROLES.map(({ role, category, requiredSkills, preferredSkills }) => ({
    role,
    category,
    requiredSkills,
    preferredSkills
  })));
});

app.post('/ai/recommendations', (req, res) => {
  const { resumeText, skills } = req.body || {};
  const candidateSkills = getCandidateSkills(skills, resumeText);

  if (!candidateSkills.length) {
    return res.status(400).json({
      error: 'Provide resumeText or skills with at least one recognizable skill'
    });
  }

  const recommendations = JOB_ROLES
    .map(role => calculateRoleMatch(candidateSkills, role))
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)
    .map((recommendation) => ({
      ...recommendation,
      nextSteps: [
        ...recommendation.missingSkills.required.map(skill => `Learn ${skill}`),
        ...recommendation.missingSkills.preferred.slice(0, 2).map(skill => `Practice ${skill}`)
      ]
    }));

  const skillGapSummary = buildSkillGapSummary(recommendations);

  res.json({
    extractedSkills: candidateSkills,
    recommendations,
    skillGapSummary
  });
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => console.log(`TaskFlow running on port ${PORT}`));
}

module.exports = app;
