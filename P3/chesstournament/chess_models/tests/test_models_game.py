from django.test import TransactionTestCase, tag
from chess_models.models import Player, Tournament, Round, Game
from chess_models.models import (
    LichessAPIError, TournamentType, Scores)
from ..models.game import create_rounds
import requests
from unittest.mock import patch, MagicMock
# from chess_models.models import getPoints, getRanking


class GameModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # create Tournament
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.DOUBLEROUNDROBIN)
        # create round
        round_name = 'round_01'
        self.round = Round.objects.create(
            name=round_name, tournament=tournament)
        # create two players
        self.players = []
        player = Player.objects.create(
            lichess_username='alpega')
        tournament.players.add(player)
        self.players.append(player)
        player = Player.objects.create(
            lichess_username='fernanfer')
        tournament.players.add(player)
        self.players.append(player)
        tournament.save()

    @tag("continua")
    def test_001_game_str_method(self):
        "create a game and test str method"
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.result = Scores.WHITE
        game.save()
        white = self.players[0]
        black = self.players[1]
        self.assertIn(
            f'{str(white)}({white.id}) vs {str(black)}({black.id}) ='
            f' {Scores.WHITE.label}',
            str(game)
            )

    # ROB: get_lichess_game_result needed
    @tag("continua")
    def test_002_game_get_result_from_lichess(self):
        """given a lichess game_id get the result of the game
        This function should connect to the lichess API
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        winner, white, black = game.get_lichess_game_result('HsdNrFxG')
        self.assertEqual(white, self.players[0].lichess_username)
        self.assertEqual(black, self.players[1].lichess_username)
        self.assertEqual(winner.lower(), Scores.WHITE.value)

    @tag("continua")
    def test_003_game_get_result_from_lichess_invalid_game_id(self):
        """given a lichess game_id get the result of the game.
        gameID points to a game that has not been 
        played by the players 'white.lichess_username' and 
        'black.lichess_username". A exception should be raised
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        with self.assertRaises(LichessAPIError):
            winner, white, black = game.get_lichess_game_result('kJfWZqUL')

    @tag("continua")
    def test_004_game_get_result_from_lichess_invalid_game_id(self):
        """given a lichess game_id get the result of the game.
        gameID is invalid thererefore a exception occurs.
        In this test the game does not exist.
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        with self.assertRaises(LichessAPIError):
            winner, white, black = game.get_lichess_game_result(
                'AAAAAAAAAAAAAAAAAAAAA')

    def test_010_getcross_table(self):
        "test get_cross_table"
        pass
    
    
    
    
    
    
        ################## TESTS EXTRA ################
        
    @tag("continua")
    def test_005_game_get_result_from_lichess_missing_data(self):
        """
        La función debe retornar None si faltan datos como game_id, white o black.
        """
        # Caso 1: faltan ambos jugadores
        game = Game.objects.create(round=self.round)
        result = game.get_lichess_game_result('some_game_id')
        self.assertIsNone(result)

        # Caso 2: falta solo game_id
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        result = game.get_lichess_game_result('')
        self.assertIsNone(result)

        # Caso 3: falta jugador blanco
        game = Game.objects.create(round=self.round)
        game.black = self.players[1]
        game.save()
        result = game.get_lichess_game_result('some_game_id')
        self.assertIsNone(result)

        # Caso 4: falta jugador negro
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.save()
        result = game.get_lichess_game_result('some_game_id')
        self.assertIsNone(result)
        
        
    @tag("continua")
    @patch('requests.get')
    def test_006_game_get_result_draw(self, mock_get):
        """Test que verifica que la partida se marque como empate (DRAW) si no hay ganador"""
        game = Game.objects.create(round=self.round, white=self.players[0], black=self.players[1])
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'dummy_id',
            'speed': 'blitz',
            'players': {
                'white': {'userId': self.players[0].lichess_username},
                'black': {'userId': self.players[1].lichess_username},
            },
            'winner': None  # Caso DRAW
        }
        mock_get.return_value = mock_response

        result, white, black = game.get_lichess_game_result('some_game_id')
        self.assertEqual(result, Scores.DRAW)
        
        
        
    @tag("continua")
    @patch('requests.get')
    def test_007_game_get_result_raises_on_connection_error(self, mock_get):
        """Debe lanzar LichessAPIError si falla la conexión con la API de Lichess"""
        game = Game.objects.create(round=self.round, white=self.players[0], black=self.players[1])
        
        mock_get.side_effect = requests.exceptions.RequestException("No se pudo conectar")

        with self.assertRaises(LichessAPIError) as context:
            game.get_lichess_game_result('some_game_id')

        self.assertIn("Error al conectar con Lichess en game", str(context.exception))


    @tag("continua")
    def test_009_create_rounds_no_players_list(self):
        """Debe salir temprano si la lista de jugadores está vacía"""
        tournament = Tournament.objects.create(name='EmptyTournament', tournament_type=TournamentType.DOUBLEROUNDROBIN)
        result = create_rounds(tournament)
        self.assertIsNone(result)


    @tag("continua")
    def test_010_create_rounds_zero_players(self):
        """Debe salir si el número de jugadores es 0"""
        tournament = Tournament.objects.create(name='ZeroPlayers', tournament_type=TournamentType.DOUBLEROUNDROBIN)
        result = create_rounds(tournament)
        self.assertIsNone(result)
        
    
    
    @tag("continua")
    def test_011_create_rounds_none_tournament(self):
        """Debe devolver None si el torneo es None"""
        result = create_rounds(None)
        self.assertIsNone(result)

    
    @tag("continua")
    def test_013_create_rounds_zero_players(self):
        """Debe devolver None si el torneo tiene 0 jugadores"""
        tournament = Tournament.objects.create(name="Sin jugadores", tournament_type=TournamentType.DOUBLEROUNDROBIN)
        self.assertEqual(tournament.getPlayersCount(), 0)
        result = create_rounds(tournament)
        self.assertIsNone(result)

    @tag("continua")
    @patch("builtins.print")
    def test_015_create_rounds_prints_error_if_no_players(self, mock_print):
        tournament = Tournament.objects.create(name="Sin jugadores", tournament_type=TournamentType.DOUBLEROUNDROBIN)
        result = create_rounds(tournament)
        mock_print.assert_called_with("No hay jugadores en el torneo.")
        self.assertIsNone(result)

