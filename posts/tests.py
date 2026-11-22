from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Post


class PostAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.en_post = Post.objects.create(title="First", body="English body", language="en")
        self.ta_post = Post.objects.create(title="தமிழ்", body="தமிழ் உடல்", language="ta")

    def test_list_is_public(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_requires_login(self):
        response = self.client.post(
            reverse("post-list"), {"title": "New", "body": "New body"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)

    def test_create_when_logged_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("post-list"), {"title": "New", "body": "New body"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)

    def test_reject_post_with_no_title(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("post-list"), {"body": "No title but body"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_language_filter(self):
        response = self.client.get(reverse("post-list"), {"language": "ta"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["language"], "ta")

    def test_reject_delete_without_login(self):
        url = reverse("post-detail", kwargs={"pk": self.ta_post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=self.ta_post.pk).exists())

    def test_post_not_found(self):
        url = reverse("post-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)