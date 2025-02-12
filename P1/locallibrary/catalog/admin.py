from django.contrib import admin

# Register your models here.
# importa los modelos y luego realiza una llamada admin.site.registerpara registrarlos en la base de datos
from .models import Author, Genre, Book, BookInstance, Language



#Esto indica que cada autor mostrará una tabla con las instancias de libros (BookInstance) asociadas a él.
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0 #para que no se muestren instancias adicionales en blanco
    
# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    
    #hace que los registros relacionados con BookInstance aparezcan dentro de la página de edición de un Author
    inlines = [BooksInstanceInline]
    

    
# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )
    

class BooksInline(admin.TabularInline):
    model = Book
    extra = 0
    
# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
                        
    #atributo q enumera solo los campos que se mostrarán en el formulario, en orden
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [BooksInline]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

#admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)
