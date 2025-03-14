from django.shortcuts import render

# Create your views here.
from .models import Persona
from .serializers import PersonaSerializer
from rest_framework import viewsets


# ModelViewSet maneja automáticamente CRUD (GET, POST, PUT, DELETE)
class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer