from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task

User = get_user_model()


class TaskAuthenticationTests(APITestCase):
    def test_list_requires_authentication(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_and_login_flow(self):
        register_url = "/api/auth/register/"
        response = self.client.post(
            register_url,
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "SuperSecret123",
                "password_confirm": "SuperSecret123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login_url = "/api/auth/token/"
        response = self.client.post(
            login_url, {"username": "alice", "password": "SuperSecret123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "bob",
                "password": "SuperSecret123",
                "password_confirm": "DifferentPass456",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass12345")
        self.other_user = User.objects.create_user(username="intruder", password="pass12345")
        login = self.client.post(
            "/api/auth/token/", {"username": "owner", "password": "pass12345"}
        )
        self.access_token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def _create_task(self, **overrides):
        payload = {"title": "Write tests", "description": "Cover the API", "priority": "high"}
        payload.update(overrides)
        return self.client.post("/api/tasks/", payload)

    def test_create_task_sets_owner_automatically(self):
        response = self._create_task()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], "owner")
        self.assertEqual(Task.objects.get().owner, self.user)

    def test_list_only_returns_own_tasks(self):
        self._create_task(title="Mine")
        Task.objects.create(owner=self.other_user, title="Not mine")

        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Mine"])

    def test_retrieve_update_delete_own_task(self):
        create_response = self._create_task()
        task_id = create_response.data["id"]
        detail_url = f"/api/tasks/{task_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(detail_url, {"completed": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completed"])

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_cannot_access_other_users_task(self):
        other_task = Task.objects.create(owner=self.other_user, title="Secret")
        response = self.client.get(f"/api/tasks/{other_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_priority(self):
        self._create_task(title="High one", priority="high")
        self._create_task(title="Low one", priority="low")

        response = self.client.get("/api/tasks/?priority=low")
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Low one"])

    def test_search_by_title(self):
        self._create_task(title="Buy groceries")
        self._create_task(title="Write report")

        response = self.client.get("/api/tasks/?search=report")
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Write report"])
