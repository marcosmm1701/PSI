from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    
    # Filter books and genres
    books_filtered = Book.objects.filter(title__icontains='el').count()
    genres_filtered = Genre.objects.filter(name__icontains='Fiction').count()
    
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'books_filtered': books_filtered,
        'genres_filtered': genres_filtered,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    # request: el objeto original , que es un HttpRequest
    # 'index.html': Una plantilla HTML con marcadores de posición para los datos
    # context: Un diccionario que contiene los datos a insertar en los marcadores de posición. Es decir, los parametros q se le pasan a index.html
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    ordering = ['title']    # Ordenar por título para evitar problemas y advertencias con la paginación de la lista de libros

    
    
class BookDetailView(generic.DetailView):
    model = Book
    
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    
class AuthorDetailView(generic.DetailView):
    model = Author
    



#clase para listar los libros prestados por el usuario
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    #filtra los libros que va a mostrar el html (solo los prestados al usuario)
    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')  # o = 'On loan'
            .order_by('due_back')   # Ordenar por fecha de devolución
        )
        
class LoanedBooksListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10
    permission_required = 'catalog.can_see_borrowed_books'
    
    #le manda al html los libros que tiene que mostrar
    def get_queryset(self):
        return (
            BookInstance.objects
            .filter(status__exact='o')  # o = 'On loan'
            .order_by('due_back')   # Ordenar por fecha de devolución
        )




import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm  
    
    

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)






from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


# Vistas de edición genéricas:
#Basicamente sirven para crear formularios de creación, actualización y eliminación de objetos de la base de datos

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'
    
    def get_success_url(self):
        return reverse('author-detail', kwargs={'pk': self.object.pk})

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')   # Redirige a la lista de autores si todo va bien
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )





#Vamos a hacer lo mismo pero con libros (ponte a prueba)
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'
    success_url = reverse_lazy('books')

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')   # Redirige a la lista de autores si todo va bien
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )



class LanguageDetailView(DetailView):
    model = Language
    template_name = 'catalog/language_detail.html'  # Nombre de la plantilla
    context_object_name = 'language'  # Nombre del objeto en el contexto
    
    
class GenreDetailView(DetailView):
    model = Genre
    template_name = 'catalog/genre_detail.html'  # Nombre de la plantilla
    context_object_name = 'genre'  # Nombre del objeto en el contexto
    