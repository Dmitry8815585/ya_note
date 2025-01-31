from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    NOTE_TEXT = 'Text'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='author',
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.form_data = {
            'title': cls.NOTE_TEXT,
            'text': cls.NOTE_TEXT,
        }

        cls.url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):

    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TEXT,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NOTE_TEXT,
            'text': cls.NEW_NOTE_TEXT,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestSlug(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='author',
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.url = reverse('notes:add')

        cls.form_data = {
            'title': 'Test Title',
            'text': 'Test Content',
            'slug': ''
        }

    def test_empty_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get(title=self.form_data['title'])
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestSlugUniq(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Test Note',
            text='Test Content',
            slug='test-slug',
            author=cls.user
        )

        cls.url = reverse('notes:add')

    def test_not_unique_slug(self):
        not_uniq_slug = {'slug': f'{self.note.slug}'}
        response = self.auth_client.post(self.url, data=not_uniq_slug)

        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
