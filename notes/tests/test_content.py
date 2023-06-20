'''from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


class PostTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create(
            username='author',
        )

        self.post1 = Note.objects.create(
            title='Test Post 1',
            text='This is a test post by author.',
            author=self.author
        )

        self.post2 = Note.objects.create(
            title='Test Post 2',
            text='This is another test post by author.',
            author=self.author
        )

    def test_author_can_view_list_of_posts(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
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
        self.note_reader = Note.objects.create(
            title='Test Note Reader',
            text='This is a test note.',
            author=self.reader
        )

    def test_anonymous_client_has_no_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', [self.note.slug]),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_list_notes_for_not_user_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        for note in object_list:
            self.assertNotEqual(note, self.note_reader)
