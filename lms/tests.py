# lms/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription


User = get_user_model()


class LessonCRUDAndSubscriptionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@test.com", password="12345")
        self.other = User.objects.create_user(email="other@test.com", password="12345")

        self.course = Course.objects.create(
            title="Course 1",
            description="Desc",
            owner=self.owner,
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Lesson 1",
            description="Lesson desc",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            owner=self.owner,
        )

    def test_lesson_list_auth_required(self):
        url = reverse("lesson-list")
        r = self.client.get(url)
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_lesson_create_ok_for_owner(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson-create")
        data = {
            "course": self.course.id,
            "title": "Lesson 2",
            "description": "Desc",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        r = self.client.post(url, data=data, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_reject_non_youtube_link(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson-create")
        data = {
            "course": self.course.id,
            "title": "Bad",
            "description": "Desc",
            "video_url": "https://example.com/video",
        }
        r = self.client.post(url, data=data, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", r.data)

    def test_lesson_retrieve_owner_ok(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson-get", kwargs={"pk": self.lesson.id})
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["id"], self.lesson.id)

    def test_lesson_update_forbidden_for_other(self):
        self.client.force_authenticate(user=self.other)

        url = reverse("lesson-update", kwargs={"pk": self.lesson.id})
        r = self.client.patch(url, data={"title": "Hacked"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_update_owner_ok(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson-update", kwargs={"pk": self.lesson.id})
        r = self.client.patch(url, data={"title": "Updated"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_lesson_delete_forbidden_for_other(self):
        self.client.force_authenticate(user=self.other)

        url = reverse("lesson-delete", kwargs={"pk": self.lesson.id})
        r = self.client.delete(url)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner_ok(self):
        self.client.force_authenticate(user=self.owner)

        url = reverse("lesson-delete", kwargs={"pk": self.lesson.id})
        r = self.client.delete(url)
        self.assertIn(r.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

    def test_subscription_toggle(self):
        self.client.force_authenticate(user=self.other)

        url = reverse("course-subscribe", kwargs={"pk": self.course.id})

        r1 = self.client.post(url, data={}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(user=self.other, course=self.course).exists())

        r2 = self.client.post(url, data={}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.other, course=self.course).exists())

    def test_course_returns_is_subscribed(self):
        self.client.force_authenticate(user=self.other)

        course = Course.objects.create(
            title="Course for other",
            description="Desc",
            owner=self.other,
        )
        Subscription.objects.create(user=self.other, course=course)

        url = reverse("courses-detail", kwargs={"pk": course.id})
        r = self.client.get(url)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", r.data)
        self.assertTrue(r.data["is_subscribed"])

