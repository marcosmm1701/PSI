from django.urls import path
from . import views

#teniendo en cuenta que la url ya debe haber conocido /catalog
urlpatterns = [
    path('', views.index, name='index'),    # URL para la vista de index
    path('books/', views.BookListView.as_view(), name='books'), # URL para la vista de books
    path('book/<int:pk>', views.BookDetailView.as_view(), name = 'book-detail'),    # URL para la vista de detalle de un libro
    path('authors/', views.AuthorListView.as_view(),name = 'authors'),  # URL para la vista de autores
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name = 'author-detail'),  # URL para la vista de detalle de un autor
]
