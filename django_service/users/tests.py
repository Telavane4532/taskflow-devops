from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserAuthTests(APITestCase):
    def test_register_and_token(self):
        reg = self.client.post(reverse("user-register"), {"username": "newuser", "password": "password123"}, format="json")
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)

        token = self.client.post(reverse("token_obtain_pair"), {"username": "newuser", "password": "password123"}, format="json")
        self.assertEqual(token.status_code, status.HTTP_200_OK)
        self.assertIn("access", token.data)
