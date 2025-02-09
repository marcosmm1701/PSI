from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    
    books_filtered = Book.objects.filter(title__icontains='el').count()
    genres_filtered = Genre.objects.filter(name__icontains='Fiction').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'books_filtered': books_filtered,
        'genres_filtered': genres_filtered
    }

    # Render the HTML template index.html with the data in the context variable
    # request: el objeto original , que es un HttpRequest
    # 'index.html': Una plantilla HTML con marcadores de posición para los datos
    # context: Un diccionario que contiene los datos a insertar en los marcadores de posición. Es decir, los parametros q se le pasan a index.html
    return render(request, 'index.html', context=context)
