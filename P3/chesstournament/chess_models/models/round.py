from django.db import models
from django.utils import timezone
from .tournament import Tournament

class Round(models.Model):
    name = models.CharField(max_length= 128)
    tournament = models.ForeignKey(Tournament, on_delete=models.RESTRICT)
    start_date = models.DateTimeField(default=timezone.now, null = True)
    end_date = models.DateTimeField(null = True)
    finish = models.BooleanField(default=False)
    