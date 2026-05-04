from django.contrib.auth.models import User
from django.test import TestCase
from django.db.models.signals import post_save
from rest_framework import status
from rest_framework.test import APIClient
from backend.models.user_profile import create_user_profile, save_user_profile
from backend.models.subscription import create_user_subscription


class AuthAccessTests(TestCase):
    """M3 smoke: authentication boundary checks."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 测试库中的 UserProfile 历史迁移与当前模型字段不一致时，先隔离 profile 信号，避免阻塞接口权限 smoke。
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)
        post_save.disconnect(create_user_subscription, sender=User)

    @classmethod
    def tearDownClass(cls):
        post_save.connect(create_user_profile, sender=User)
        post_save.connect(save_user_profile, sender=User)
        post_save.connect(create_user_subscription, sender=User)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.trip_plans_url = "/api/v1/trip-plans/"
        self.user = User.objects.create_user(
            username="smoke_user",
            email="smoke@example.com",
            password="test-pass-123",
        )

    def test_trip_plan_create_requires_authentication(self):
        payload = {"title": "Unauthenticated should fail"}
        response = self.client.post(self.trip_plans_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_trip_plan_create_accepts_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        payload = {"title": "Authenticated trip"}
        response = self.client.post(self.trip_plans_url, payload, format="json")

        # Create should no longer fail due to authentication.
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("slug", response.data)
