from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Comment


class TestComments(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
        )
        self.other_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
        )
        self.own_comment = Comment.objects.create(
            author=self.user,
            content="My own comment",
        )
        self.other_comment = Comment.objects.create(
            author=self.other_user,
            content="Another user comment",
        )

    def test_logged_out_users_see_login_prompt_to_comment(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Log in to comment")
        self.assertNotContains(response, "Post Comment")

    def test_logged_in_user_sees_comment_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Post Comment")

    def test_empty_comments_are_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("index"),
            data={"content": "   "},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Comment.objects.count(), 2)

    def test_user_cannot_edit_comment_owned_by_someone_else(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("edit_comment", args=[self.other_comment.id]),
            data={"content": "Attempted edit"},
        )
        self.other_comment.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.other_comment.content, "Another user comment")

    def test_user_cannot_delete_comment_owned_by_someone_else(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("delete_comment", args=[self.other_comment.id]),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Comment.objects.filter(id=self.other_comment.id).exists()
        )

    def test_user_can_edit_and_delete_own_comment(self):
        self.client.force_login(self.user)

        edit_response = self.client.post(
            reverse("edit_comment", args=[self.own_comment.id]),
            data={"content": "Updated comment"},
        )
        self.assertEqual(edit_response.status_code, 302)
        self.own_comment.refresh_from_db()
        self.assertEqual(self.own_comment.content, "Updated comment")

        delete_response = self.client.post(
            reverse("delete_comment", args=[self.own_comment.id]),
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.own_comment.id).exists())
