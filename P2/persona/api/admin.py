from django.contrib import admin
from .models import Persona

# Register your models here.
class PersonaAdmin(admin.ModelAdmin):
    model=Persona
    list_display = ["id","nombre","apellido", "email"]

admin.site.register(Persona, PersonaAdmin)