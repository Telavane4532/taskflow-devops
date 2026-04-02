from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CoreApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.post(reverse("user-register"), {"username": "john", "password": "password123"}, format="json")
        token_res = self.client.post(reverse("token_obtain_pair"), {"username": "tester", "password": "password123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_res.data['access']}")

    def test_health(self):
        self.client.credentials()
        res = self.client.get(reverse("health"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_project_and_task_crud(self):
        proj_res = self.client.post("/api/projects/", {"name": "Project A", "description": "Alpha"}, format="json")
        self.assertEqual(proj_res.status_code, status.HTTP_201_CREATED)
        project_id = proj_res.data["id"]

        task_res = self.client.post(
            "/api/tasks/",
            {"project": project_id, "title": "Do stuff", "description": "More details", "status": "todo"},
            format="json",
        )
        self.assertEqual(task_res.status_code, status.HTTP_201_CREATED)

        list_res = self.client.get("/api/tasks/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 1)
