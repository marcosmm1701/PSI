from django.db import models
from .constants import TournamentBoardType, TournamentSpeed, RankingSystem
from .player import Player
from .other_models import Referee
from django.contrib.auth.models import User

from django.utils import timezone


class RankingSystemClass(models.Model):
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
    )

    def __str__(self):
        return self.get_value_display()
    


class Tournament(models.Model):
    
    name = models.CharField(max_length=128, unique=True, null=True, blank=True)
    administrariveUser = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    players = models.ManyToManyField(Player, blank=True)
    referee = models.ForeignKey(Referee, on_delete=models.RESTRICT, null= True)
    start_date = models.DateTimeField(default=timezone.now, null=True)
    end_date = models.DateTimeField(null=True)
    max_update_time = models.IntegerField(default=43200)
    only_administrative = models.BooleanField(default=False)
    tournament_type = models.CharField(max_length=2)
    tournament_speed = models.CharField(max_length=2)
    board_type = models.CharField(max_length=3)
    win_points = models.FloatField(default=1.0)
    draw_points = models.FloatField(default=0.5)
    lose_points = models.FloatField(default=0.0)
    timeControl = models.CharField(max_length=32, default='15+0')
    number_of_rounds_for_swiss = models.IntegerField(default=0)
    rankingList = models.ManyToManyField(RankingSystemClass, blank=True)
    

    def __str__(self):
        return self.name
    
    
    def getPlayers(self, sorted=False):
        """
        Obtiene la lista de jugadores en el torneo.
        """
        
        if not sorted:
            # Retornamos los jugadores en el orden en que fueron añadidos
            return list(self.players.all())
        
        # Determinamos el campo de ordenación en base a tournament_speed y board_type
        if self.tournament_speed == TournamentSpeed.RAPID and self.board_type == TournamentBoardType.LICHESS:
            return list(self.players.order_by('-lichess_rating_rapid'))
        elif self.tournament_speed == TournamentSpeed.BULLET and self.board_type == TournamentBoardType.LICHESS:
            return list(self.players.order_by('-lichess_rating_bullet'))
        elif self.tournament_speed == TournamentSpeed.BLITZ and self.board_type == TournamentBoardType.LICHESS:
            return list(self.players.order_by('-lichess_rating_blitz'))
        elif self.tournament_speed == TournamentSpeed.CLASSICAL and self.board_type == TournamentBoardType.LICHESS:
            return list(self.players.order_by('-lichess_rating_classical'))
        elif self.tournament_speed == TournamentSpeed.RAPID and self.board_type == TournamentBoardType.OTB:
            return list(self.players.order_by('-fide_rating_rapid'))
        elif self.tournament_speed == TournamentSpeed.BLITZ and self.board_type == TournamentBoardType.OTB:
            return list(self.players.order_by('-fide_rating_blitz'))
        elif self.tournament_speed == TournamentSpeed.CLASSICAL and self.board_type == TournamentBoardType.OTB:
            return list(self.players.order_by('-fide_rating_classical'))
        else:
            # Si no hay criterio específico, devolvemos en orden de inserción
            return list(self.players.all())
        
    def getPlayersCount(self):
        """
        Retorna la cantidad de jugadores en el torneo.
        """
        return self.players.count()
    

"""    
class TournamentPlayer(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    order = models.IntegerField(null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.player.name} - {self.tournament.name}"
"""

def getRanking(self):
    pass