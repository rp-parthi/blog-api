from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Post


class PostAPITest(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username="tester1", password="pass12345")
        self.user2 = User.objects.create_user(username="tester2", password="pass12345")
        self.en_post = Post.objects.create(title="First", body="English body", author=self.user1, language="en")
        self.ta_post = Post.objects.create(title="தமிழ்", body="தமிழ் உடல்", author=self.user2, language="ta")

    def test_list_is_public(self):
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_requires_login(self):
        url = reverse("post-list")
        payload = {"title": "New", "body": "New body"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)

    def test_create_when_logged_in(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-list")
        payload = {"title": "New", "body": "New body"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)

    def test_reject_post_with_no_title(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-list")
        payload = {"body": "No title but body"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_language_filter(self):
        url = reverse("post-list")
        payload = {"language": "ta"}
        response = self.client.get(url, payload)
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

    def test_user1_can_rename_own_post(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-detail", kwargs={"pk": self.en_post.pk})
        payload = {"title": "Renamed"}
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.en_post.refresh_from_db()
        self.assertEqual(self.en_post.title, "Renamed")

    def test_patch_other_author_post(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-detail", kwargs={"pk": self.ta_post.pk})
        payload = {"title": "Hacked"}
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.ta_post.refresh_from_db()
        self.assertEqual(self.ta_post.title, "தமிழ்")

    def test_delete_own_post(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-detail", kwargs={"pk": self.en_post.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.en_post.pk).exists())

    def test_create_sets_author_from_logged_in_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("post-list")
        payload = {"title": "Mine", "body": "text", "author": "tester2"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_post = Post.objects.get(pk=response.data["id"])
        self.assertEqual(new_post.author, self.user1)