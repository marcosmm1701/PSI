from datetime import date, timedelta
from catalog.models import BookInstance, Book, Author, User, Language, Genre
from django.test import TestCase


class AuthorModelTest(TestCase):
    # se llama al método una vez para la clase
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(id=1, first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un género con id=1 para las pruebas
        Genre.objects.create(id=1, name='Science Fiction')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(str(genre), expected_object_name)

    def test_get_absolute_url(self):
        genre = Genre.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(genre.get_absolute_url(), '/catalog/genre/1')

    def test_name_case_insensitive_unique(self):
        # Intentar crear un género con el mismo nombre (ignorando
        # mayúsculas/minúsculas)
        with self.assertRaises(Exception):
            Genre.objects.create(name='science fiction')


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un idioma con id=1 para las pruebas
        Language.objects.create(id=1, name='English')

    def test_name_label(self):
        language = Language.objects.get(id=1)
        field_label = language._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        language = Language.objects.get(id=1)
        max_length = language._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        language = Language.objects.get(id=1)
        expected_object_name = language.name
        self.assertEqual(str(language), expected_object_name)

    def test_get_absolute_url(self):
        language = Language.objects.get(id=1)
        self.assertEqual(language.get_absolute_url(), '/catalog/language/1')

    def test_name_case_insensitive_unique(self):
        # Intentar crear un idioma con el mismo nombre (ignorando
        # mayúsculas/minúsculas)
        with self.assertRaises(Exception):
            Language.objects.create(name='english')


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un autor, género e idioma con ids específicos para las pruebas
        Author.objects.create(id=1, first_name='George', last_name='Orwell')
        Genre.objects.create(id=1, name='Dystopian')
        Language.objects.create(id=1, name='English')

        # Crear un libro con id=1 para las pruebas
        Book.objects.create(
            id=1,
            title='1984',
            author=Author.objects.get(id=1),
            summary='A dystopian novel by George Orwell.',
            isbn='9780451524935',
            language=Language.objects.get(id=1)
        )
        book = Book.objects.get(id=1)
        book.genre.add(Genre.objects.get(id=1))

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_summary_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('summary').max_length
        self.assertEqual(max_length, 1000)

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'ISBN')

    def test_isbn_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('isbn').max_length
        self.assertEqual(max_length, 13)

    def test_object_name_is_title(self):
        book = Book.objects.get(id=1)
        expected_object_name = book.title
        self.assertEqual(str(book), expected_object_name)

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), '/catalog/book/1')

    def test_display_genre(self):
        book = Book.objects.get(id=1)
        expected_genre = 'Dystopian'
        self.assertEqual(book.display_genre(), expected_genre)


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un autor, libro y usuario con ids específicos para las pruebas
        Author.objects.create(id=1, first_name='J.K.', last_name='Rowling')
        Book.objects.create(
            id=1,
            title='Harry Potter',
            author=Author.objects.get(id=1),
            summary='A fantasy novel by J.K. Rowling.',
            isbn='9780439554930',
        )
        User.objects.create(id=1, username='testuser')

        # Crear una instancia de libro con id=1 para las pruebas
        BookInstance.objects.create(
            id=1,
            book=Book.objects.get(id=1),
            imprint='Bloomsbury',
            due_back=date.today() + timedelta(days=7),
            borrower=User.objects.get(id=1),
            status='o'
        )

    def test_imprint_label(self):
        book_instance = BookInstance.objects.get(id=1)
        field_label = book_instance._meta.get_field('imprint').verbose_name
        self.assertEqual(field_label, 'imprint')

    def test_imprint_max_length(self):
        book_instance = BookInstance.objects.get(id=1)
        max_length = book_instance._meta.get_field('imprint').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_id_and_title(self):
        book_instance = BookInstance.objects.get(id=1)
        book_title = book_instance.book.title
        expected_object_name = f'{book_instance.id} ({book_title})'
        self.assertEqual(str(book_instance), expected_object_name)

    def test_is_overdue(self):
        book_instance = BookInstance.objects.get(id=1)
        # Prueba cuando el libro no está vencido
        self.assertFalse(book_instance.is_overdue)

        # Prueba cuando el libro está vencido
        book_instance.due_back = date.today() - timedelta(days=1)
        book_instance.save()
        self.assertTrue(book_instance.is_overdue)

    def test_status_label(self):
        book_instance = BookInstance.objects.get(id=1)
        field_label = book_instance._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')

    def test_status_max_length(self):
        book_instance = BookInstance.objects.get(id=1)
        max_length = book_instance._meta.get_field('status').max_length
        self.assertEqual(max_length, 1)
