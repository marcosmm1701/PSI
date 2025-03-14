from django.db import models

# Create your models here.
from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ['id']
