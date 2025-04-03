from django.db import models


class Referee(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    refereeNumber = models.CharField(max_length=32, default=-1, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.refereeNumber})"
    
    
class LichessAPIError(Exception):
    """Excepción para errores de la API de Lichess"""
    pass


class Color(models.TextChoices):
    WHITE = 'w', 'White'
    BLACK = 'b', 'Black'
    NOCOLOR = '-', 'No color'