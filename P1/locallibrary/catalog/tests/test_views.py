from django.contrib.contenttypes.models import ContentType
# Required to grant the permission needed to set a book as returned.
from django.contrib.auth.models import Permission
import uuid
from catalog.models import BookInstance, Book, Genre, Language
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
from django.test import TestCase
from django.urls import reverse


from catalog.models import Author


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Dominique {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['author_list']), 2)

    def test_lists_all_authors(self):
        # Se ha cambiado este test para que que se adapte a la paginacion de 2.
        # Dando como resultado, q en la pagina 7(la ultima), habra solo 1 autor
        response = self.client.get(reverse('authors') + '?page=7')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['author_list']), 1)


# tests para probar las vistas que requieren estar logeado en la web
# Get user model from settings
User = get_user_model()


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        # Direct assignment of many-to-many types not allowed.
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            date1 = timezone.localtime()
            date2 = datetime.timedelta(days=book_copy % 5)
            return_date = date1 + date2
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for book_item in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], book_item.borrower)
            self.assertEqual(book_item.status, 'o')

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


# test para probar vistas con formularios (más complicado)


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        # Direct assignment of many-to-many types not allowed.
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the
        # redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right
        # permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any
        # users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={
                    'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        date1 = datetime.date.today()
        date2 = datetime.timedelta(weeks=3)
        date_3_weeks_in_future = date1 + date2
        self.assertEqual(
            response.context['form'].initial['renewal_date'],
            date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        date1 = datetime.date.today()
        date2 = datetime.timedelta(weeks=2)
        valid_date_in_future = date1 + date2
        response = self.client.post(
            reverse(
                'renew-book-librarian', kwargs={
                    'pk': self.test_bookinstance1.pk, }), {
                'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        date1 = datetime.date.today()
        date2 = datetime.timedelta(weeks=1)
        date_in_past = date1 - date2
        response = self.client.post(
            reverse(
                'renew-book-librarian', kwargs={
                    'pk': self.test_bookinstance1.pk}), {
                'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'renewal_date',
            'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD')
        date1 = datetime.date.today()
        date2 = datetime.timedelta(weeks=5)
        invalid_date_in_future = date1 + date2
        response = self.client.post(
            reverse(
                'renew-book-librarian', kwargs={
                    'pk': self.test_bookinstance1.pk}), {
                'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'renewal_date',
            'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""

    def setUp(self):
        # Crear usuario sin permisos
        self.user_no_perms = User.objects.create_user(
            username='user1', password='password123')

        # Crear usuario con permiso para agregar autores
        self.user_with_perms = User.objects.create_user(
            username='user2', password='password123')
        content_type = ContentType.objects.get_for_model(Author)
        permission = Permission.objects.get(
            codename="add_author", content_type=content_type)
        self.user_with_perms.user_permissions.add(permission)
        self.user_with_perms.save()

    # Verificamos que los usuarios no autenticados sean redirigidos al login.
    def test_redirect_if_not_logged_in(self):
        """Verifica que los usuarios no autenticados
            sean redirigidos al login."""
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 302)  # Redirección al login
        self.assertTrue(response.url.startswith('/accounts/login/'))

    # Verificamos que los usuarios sin permisos reciban un error 403
    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """Verifica que los usuarios sin permisos reciban un error 403."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    # Verifica que un usuario con permisos pueda acceder y que se use la
    # plantilla correcta.
    def test_logged_in_with_permission(self):
        """Verifica que un usuario con permisos puede acceder a la vista."""
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertTemplateUsed(
            response, 'catalog/author_form.html')  # Verificar plantilla

    # Vemos que el campo date_of_death tenga la fecha inicial correcta
    # (11/11/2023).
    def test_initial_date_of_death(self):
        """Verifica que el campo `date_of_death`
            tenga el valor inicial correcto."""
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].initial['date_of_death'],
            '11/11/2023')

    # Verifica que un usuario con permisos pueda acceder y que se use la
    # plantilla correcta.
    def test_uses_correct_template(self):
        """Verifica que se usa la plantilla correcta."""
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertTemplateUsed(
            response, 'catalog/author_form.html')  # Verificar plantilla

    # Vemos que el campo date_of_death tenga la fecha inicial correcta
    # (11/11/2023).
    def test_form_date_of_death_initially_set_to_expected_date(self):
        """Verifica que el campo `date_of_death`
            tenga el valor inicial correcto."""
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].initial['date_of_death'],
            '11/11/2023')

    # Verificamos que se redirige a la página de detalle del autor tras un
    # POST exitoso.
    def test_redirects_to_detail_view_on_success(self):
        """Verifica que tras un POST exitoso,
            se redirige a la página de detalle del autor."""
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('author-create'), {
            'first_name': 'Julio',
            'last_name': 'Verne',
            'date_of_birth': '1828-02-08',
            'date_of_death': '1905-03-24'
        })
        self.assertEqual(response.status_code, 302)  # Redirección tras éxito
        self.assertTrue(response.url.startswith('/catalog/author/'))

        # Verificar que el autor se ha creado en la base de datos
        self.assertTrue(
            Author.objects.filter(
                first_name="Julio",
                last_name="Verne").exists())
