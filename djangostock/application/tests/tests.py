import json

from django.contrib.auth import authenticate
from django.test import TestCase
from rest_framework import status

from .factories import UserFactory, setup_test_environment

from ..models import User


class UserListTest(TestCase):
    NUM_USERS = 10

    def setUp(self):
        setup_test_environment()
        for _ in range(self.NUM_USERS):
            UserFactory().save()

    def test_get(self):
        resp = self.client.get("/users/")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data), self.NUM_USERS)

    def test_post(self):
        resp = self.client.post(
            "/users/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(resp.data["first_name"], "Maciej")
        self.assertEquals(resp.data["last_name"], "Tester")
        self.assertEquals(resp.data["email"], "Tester@example.com")
        self.assertEquals(resp.data["is_admin"], False)
        self.assertIsNotNone(authenticate(username="Tester@example.com", password="Password123"))
        user = User.objects.get(pk=resp.data["id"])
        self.assertEquals(user.first_name, "Maciej")
        self.assertEquals(user.last_name, "Tester")
        self.assertEquals(user.is_active, True)
        self.assertEquals(user.is_admin, False)


class UserDetailTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user = UserFactory()
        self.user.save()

    def test_get(self):
        resp = self.client.get(f"/users/{self.user.id}/")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["id"], self.user.id)

    def test_post(self):
        resp = self.client.post(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        resp = self.client.put(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.data["last_name"], "Testero")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")
        self.assertEquals(user.last_name, "Testero")

    def test_patch2(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")

    def test_patch3(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                    "password": "new_passwd",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.data["last_name"], "Testero")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(authenticate(username=self.user.email, password="new_passwd"))
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")
        self.assertEquals(user.last_name, "Testero")

    def test_delete(self):
        resp = self.client.delete(f"/users/{self.user.id}/")
        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user.id)
