from django.test import Client

from django.test import TestCase
import pytest


from django.urls import reverse
import pytest


# В тесте используем фикстуру заметки
# и фикстуру клиента с автором заметки.
def test_note_in_list_for_author(note, author_client):
    url = reverse('notes:list')
    # Запрашиваем страницу со списком заметок:
    response = author_client.get(url)
    # Получаем список объектов из контекста:
    object_list = response.context['object_list']
    # Проверяем, что заметка находится в этом списке:
    assert note in object_list


# В этом тесте тоже используем фикстуру заметки,
# но в качестве клиента используем admin_client;
# он не автор заметки, так что заметка не должна быть ему видна.
def test_note_not_in_list_for_another_user(note, admin_client):
    url = reverse('notes:list')
    response = admin_client.get(url)
    object_list = response.context['object_list']
    # Проверяем, что заметки нет в контексте страницы:
    assert note not in object_list


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, note_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('admin_client'), False),
    )
)
def test_notes_list_for_different_users(
        # Используем фикстуру заметки и параметры из декоратора:
        note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    # В качестве параметров передаем name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки
        # никакие дополнительные аргументы для reverse() не нужны.
        ('notes:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
'''


class TestNoteCreation(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('notes:add')

    def test_create_note_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        #  self.assertContains(response, 'id="id_title"')
        #  self.assertContains(response, 'id="id_content"')

    def test_create_note_post(self):
        response = self.client.post(
            self.url,
            data={'title': 'Test Note', 'text': 'Test Content'}
        )
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title='Test Note')
        self.assertEqual(note.content, 'Test Content')

    def tearDown(self):
        Note.objects.filter(title='Test Note').delete()
'''