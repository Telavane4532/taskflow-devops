from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Project, Task


class AIFeatureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.client.post(reverse("user-register"), {"username": "bob", "password": "password123"}, format="json")
        token_res = self.client.post(reverse("token_obtain_pair"), {"username": "alice", "password": "password123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_res.data['access']}")
        self.project = Project.objects.create(name="P1", owner=self.user)
        self.task = Task.objects.create(project=self.project, title="Urgent server issue", description="Fix blocker today")

    def test_summarize_task(self):
        res = self.client.post(reverse("ai-summarize"), {"task_id": self.task.id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("summary", res.data)

    def test_prioritize_task(self):
        res = self.client.post(reverse("ai-prioritize"), {"task_id": self.task.id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("priority_score", res.data)

    def test_parse_task(self):
        res = self.client.post(reverse("ai-parse-task"), {"text": "Prepare release checklist and notify QA."}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("title", res.data)

    def test_similar_tasks(self):
        Task.objects.create(project=self.project, title="Urgent prod incident", description="Fix outage now")
        res = self.client.post(reverse("ai-similar-tasks", kwargs={"task_id": self.task.id}), {"top_k": 3}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
