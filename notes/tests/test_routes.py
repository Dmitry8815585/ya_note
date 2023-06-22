from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='password'
        )
        self.reader = User.objects.create_user(
            username='reader',
            password='password'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            author=self.author
        )
        self.edit_url = reverse('notes:edit', args=[self.note.slug])
        self.delete_url = reverse('notes:delete', args=[self.note.slug])

    def test_availb_for_note_delete_and_edit(self):
        user_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_status:
            self.client.force_login(user)
            for name in ('notes:delete', 'notes:edit'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):

        urls = (
            ('notes:home', None),
            ('notes:detail', [self.note.slug]),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=[self.note.slug])
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_for_author(self):
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_author_of_note(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
