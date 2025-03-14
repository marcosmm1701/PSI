from django.urls import path
from . import views

# teniendo en cuenta que la url ya debe haber conocido /catalog
urlpatterns = [
    path('', views.index, name='index'),    # URL para la vista de index
    path(
        'books/',
        views.BookListView.as_view(),
        name='books'),
    # URL para la vista de books
    path(
        'book/<int:pk>',
        views.BookDetailView.as_view(),
        name='book-detail'),
    # URL para la vista de detalle de un libro
    path(
        'authors/',
        views.AuthorListView.as_view(),
        name='authors'),
    # URL para la vista de autores
    path(
        'author/<int:pk>',
        views.AuthorDetailView.as_view(),
        name='author-detail'),
    # URL para la vista de detalle de un autor
]

# para la vista de libros prestados por el usuario
urlpatterns += [
    path(
        'mybooks/',
        views.LoanedBooksByUserListView.as_view(),
        name='my-borrowed'),
]

# URL para ver todos los libros prestados
urlpatterns += [
    path(
        'borrowed/',
        views.LoanedBooksListView.as_view(),
        name='all-borrowed'
        ),
]

# URL para renovar un libro
urlpatterns += [
    path(
        'book/<uuid:pk>/renew/',
        views.renew_book_librarian,
        name='renew-book-librarian'),
]

# URL para crear, actualizar y eliminar autores
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path(
        'author/<int:pk>/update/',
        views.AuthorUpdate.as_view(),
        name='author-update'),
    path(
        'author/<int:pk>/delete/',
        views.AuthorDelete.as_view(),
        name='author-delete'),
]


# URL para crear, actualizar y eliminar libros
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path(
        'book/<int:pk>/update/',
        views.BookUpdate.as_view(),
        name='book-update'),
    path(
        'book/<int:pk>/delete/',
        views.BookDelete.as_view(),
        name='book-delete'),
]


urlpatterns += [
    # Otras rutas...
    path(
        'genre/<int:pk>',
        views.GenreDetailView.as_view(),
        name='genre-detail'),
    path(
        'language/<int:pk>',
        views.LanguageDetailView.as_view(),
        name='language-detail'),
]
