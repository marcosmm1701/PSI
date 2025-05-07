from django.db import models
from .constants import TournamentBoardType, TournamentSpeed, RankingSystem
from .player import Player
from .other_models import Referee
from django.contrib.auth.models import User
from .game import Game
from .constants import Scores


class RankingSystemClass(models.Model):
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
    )

    def __str__(self):
        return self.get_value_display()


class TournamentPlayer(models.Model):
    """
    Modelo intermedio para la relación muchos
    a muchos entre Tournament y Player.
    """
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tournament', 'player')

    def __str__(self):
        return f"{self.tournament.name} - {self.player.name}"


class Tournament(models.Model):

    name = models.CharField(max_length=128, unique=True, null=True, blank=True)
    administrativeUser = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True)
    players = models.ManyToManyField(
        Player, blank=True, through=TournamentPlayer)
    referee = models.ForeignKey(Referee, on_delete=models.RESTRICT, null=True)
    start_date = models.DateTimeField(auto_now=True, null=True)
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

        # Determinamos el campo de ordenación en base a tournament_speed y
        # board_type
        speed = self.tournament_speed
        board = self.board_type
        if (speed == TournamentSpeed.RAPID
                and board == TournamentBoardType.LICHESS):
            return list(self.players.order_by('-lichess_rating_rapid'))
        elif (speed == TournamentSpeed.BULLET
                and board == TournamentBoardType.LICHESS):
            return list(self.players.order_by('-lichess_rating_bullet'))
        elif (speed == TournamentSpeed.BLITZ
                and board == TournamentBoardType.LICHESS):
            return list(self.players.order_by('-lichess_rating_blitz'))
        elif (speed == TournamentSpeed.CLASSICAL
                and board == TournamentBoardType.LICHESS):
            return list(self.players.order_by('-lichess_rating_classical'))
        elif (speed == TournamentSpeed.RAPID
                and board == TournamentBoardType.OTB):
            return list(self.players.order_by('-fide_rating_rapid'))
        elif (speed == TournamentSpeed.BLITZ
                and board == TournamentBoardType.OTB):
            return list(self.players.order_by('-fide_rating_blitz'))
        elif (speed == TournamentSpeed.CLASSICAL
                and board == TournamentBoardType.OTB):
            return list(self.players.order_by('-fide_rating_classical'))
        else:
            # Si no hay criterio específico, devolvemos en orden de inserción
            return list(self.players.all())

    def getGames(self):
        """
        Obtiene la lista de juegos en el torneo.
        """
        rounds = self.round_set.all()
        games = []
        for round in rounds:
            games += round.game_set.all()

        return games

    def getPlayersCount(self):
        """
        Retorna la cantidad de jugadores en el torneo.
        """
        return self.players.count()

    def getRoundCount(self):
        """
        Retorna la cantidad de rondas en el torneo.
        """
        return self.round_set.count()

    def addToRankingList(self, ranking_value):
        """
        Añade un objeto de RankingSystem con el
        valor `ranking_value` a la lista de ranking del torneo.
        Si no existe, lo crea antes de añadirlo.
        """

        # Buscamos si existe el objeto de RankingSystem
        ranking_obj, created = RankingSystemClass.objects.get_or_create(
            value=ranking_value,
            defaults={'value': ranking_value}
        )
        
        if not created:
            print("Error: El objeto ya existe en la lista de ranking.")
        
        self.rankingList.add(ranking_obj)

        return

    def removeFromRankingList(self, ranking_value):
        """
        Elimina un objeto de RankingSystem
        con el valor `ranking_value` de la lista de ranking del torneo.
        No hace nada si no está presente en la lista.
        """

        try:
            ranking_obj = RankingSystemClass.objects.get(value=ranking_value)
            self.rankingList.remove(ranking_obj)
        except RankingSystemClass.DoesNotExist:
            print(
                f"No se encontró el ranking con valor "
                f"'{ranking_value}' en RankingSystemClass."
            )

    def cleanRankingList(self):
        """
        Limpia la lista de sistemas de ranking del torneo.
        """
        self.rankingList.clear()

    def get_number_of_rounds_with_games(self):
        """
        Devuelve el número de rondas en
        las que se ha jugado al menos una partida.

        Returns:
            int: Número de rondas con partidas jugadas
        """

        # Obtenemos todas las rondas del torneo que tienen al menos un juego
        return self.round_set.filter(
            game__isnull=False  # Que tengan al menos un juego
        ).distinct().count()

    def get_latest_round_with_games(self):
        """
        Devuelve la última ronda de este torneo que tiene partidas jugadas,
        basándose en la fecha de inicio de la ronda.

        Returns:
            Round or None: Última ronda con juegos o None si no hay ninguna
        """
        # Obtenemos la última ronda con juegos ordenada por fecha descendente
        latest_round = self.round_set.filter(
            game__isnull=False  # Que tengan al menos un juego
        ).order_by('-start_date').first()

        return latest_round


def getScores(tournament):
    """Devuelve un diccionario con los
    jugadores y su puntuación en el torneo."""

    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
    results = {}

    players = tournament.getPlayers()

    # Inicializamos las puntuaciones
    for player in players:
        results[player] = {PLAIN_SCORE: 0.0}

    # Sumamos puntos de las partidas jugadas
    for game in Game.objects.filter(
            round__tournament=tournament,
            finished=True):
        # Caso 1: Juego normal con dos jugadores
        if game.white and game.black:

            if game.result == Scores.WHITE.value:
                results[game.white][PLAIN_SCORE] += tournament.win_points
                results[game.black][PLAIN_SCORE] += tournament.lose_points
            elif game.result == Scores.BLACK.value:
                results[game.black][PLAIN_SCORE] += tournament.win_points
                results[game.white][PLAIN_SCORE] += tournament.lose_points
            elif game.result == Scores.DRAW.value:
                results[game.white][PLAIN_SCORE] += tournament.draw_points
                results[game.black][PLAIN_SCORE] += tournament.draw_points

            elif game.result == Scores.FORFEITWIN.value:
                results[game.white][PLAIN_SCORE] += tournament.win_points
            """
            elif game.result == Scores.FORFEITLOSS.value:
                results[game.black][PLAIN_SCORE] += tournament.win_points
            """
        else:

            if game.result == Scores.BYE_F.value:
                if game.white:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
                elif game.black:
                    results[game.black][PLAIN_SCORE] += tournament.win_points

            elif game.result == Scores.BYE_U.value:
                if game.white:
                    results[game.white][PLAIN_SCORE] += tournament.win_points
                elif game.black:
                    results[game.black][PLAIN_SCORE] += tournament.win_points

            elif game.result == Scores.BYE_H.value:
                if game.white:
                    results[game.white][PLAIN_SCORE] += tournament.draw_points
                elif game.black:
                    results[game.black][PLAIN_SCORE] += tournament.draw_points

            # elif game.result == Scores.BYE_Z.value:
                # continue

    return results


def getBlackWins(tournament, results):
    """Añade las claves de victorias y partidas
    jugadas con negras al diccionario de resultados."""

    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value

    # Inicializar los valores
    for player in results:
        results[player].update({
            WINS: 0,
            BLACKTIMES: 0
        })

    # Contabilizar victorias y partidas jugadas con negras
    for game in Game.objects.filter(
            round__tournament=tournament,
            finished=True):

        if (game.white and game.black
            and game.white.name != '0000'
                and game.black.name != '0000'):

            if game.black:

                if (game.result == Scores.WHITE.value
                        or game.result == Scores.BLACK.value
                        or game.result == Scores.DRAW.value):
                    results[game.black][BLACKTIMES] += 1
                # Si ganó jugando con negras
                if game.result == Scores.BLACK.value:
                    results[game.black][WINS] += 1
            if game.white:
                # Si ganó jugando con blancas
                if game.result == Scores.WHITE.value:
                    results[game.white][WINS] += 1

    return results


def getRanking(tournament):
    """Devuelve un diccionario ordenado de jugadores
    con ranking basado en puntuaciones y criterios de desempate."""

    results = getScores(tournament)
    results = getBlackWins(tournament, results)

    PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
    WINS = RankingSystem.WINS.value
    BLACKTIMES = RankingSystem.BLACKTIMES.value

    # Obtener criterios de desempate del torneo
    ranking_criteria = [PLAIN_SCORE] + \
        [rs.value for rs in tournament.rankingList.all()]

    # Ordenar jugadores
    players = list(results.keys())
    if not Game.objects.filter(round__tournament=tournament).exists():
        sorted_players = tournament.getPlayers()
    else:
        sorted_players = sorted(
            players,
            key=lambda p: tuple(
                -results[p].get(criterion, 0)
                if criterion in [PLAIN_SCORE, WINS]
                # más negras, mejor
                else -results[p].get(criterion, 0) if criterion == BLACKTIMES
                else results[p].get(criterion, 0)
                for criterion in ranking_criteria
            )
        )

    # Asignar rankings
    ranked_results = {}
    for rank, player in enumerate(sorted_players, start=1):
        ranked_results[player] = {
            'rank': rank,
            'PS': results[player][PLAIN_SCORE],
            'WI': results[player][WINS],
            'BT': results[player][BLACKTIMES]
        }

    return ranked_results
