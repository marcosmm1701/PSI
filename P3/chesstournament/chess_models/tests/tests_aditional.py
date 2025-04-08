from django.test import TransactionTestCase, tag
from chess_models.models import Player, Tournament, Round, Game
from chess_models.models import (
    LichessAPIError, TournamentType, Scores)
from ..models.game import create_rounds
import requests
from unittest.mock import patch, MagicMock
from chess_models.tests.constants import (
    lichess_usernames_6)
from django.test import TransactionTestCase, tag
from chess_models.models import Player, Referee, Tournament, Game, Round
from chess_models.models import (TournamentSpeed,
                                 TournamentType, TournamentBoardType,
                                 RankingSystem, getRanking, RankingSystemClass)
from chess_models.models import create_rounds, Scores
from chess_models.tests.constants import (
    lichess_usernames_6, lichess_usernames_8)
from unittest.mock import patch
from io import StringIO
from django.contrib.auth.models import User
from django.utils import timezone

from ..models.tournament import TournamentPlayer, getScores, getBlackWins


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
        """Comprehensive test for zero players case"""
        tournament = Tournament.objects.create(
            name='ComprehensiveZeroPlayers',
            tournament_type=TournamentType.DOUBLEROUNDROBIN
        )
        
        # Verify initial state
        self.assertEqual(tournament.getPlayersCount(), 0)
        
        # Call function
        result = create_rounds(tournament)
        
        # Verify results
        self.assertIsNone(result)
        self.assertEqual(Round.objects.filter(tournament=tournament).count(), 0)
        self.assertEqual(Game.objects.filter(round__tournament=tournament).count(), 0)
        
        # Verify no side effects on tournament
        tournament.refresh_from_db()
        self.assertEqual(tournament.name, 'ComprehensiveZeroPlayers')
        
    
    
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
        
    
    @tag("continua")
    @patch("builtins.print")
    def test_020_create_rounds_zero_players_verify_print_output(self, mock_print):
        """Test que verifica específicamente el print cuando hay 0 jugadores"""
        tournament = Tournament.objects.create(
            name='EmptyTournament',
            tournament_type=TournamentType.DOUBLEROUNDROBIN
        )
        
        # Verificar que no hay jugadores
        self.assertEqual(tournament.getPlayersCount(), 0)
        
        # Llamar a la función
        result = create_rounds(tournament)
        
        # Verificar resultados
        self.assertIsNone(result)
        
        # Verificar que se llamó a print con el mensaje correcto
        mock_print.assert_called_once_with("No hay jugadores en el torneo.")
        
        # Verificar que no se crearon rondas ni partidas
        self.assertEqual(Round.objects.filter(tournament=tournament).count(), 0)
        self.assertEqual(Game.objects.filter(round__tournament=tournament).count(), 0)

    @tag("continua")
    @patch("builtins.print")
    def test_021_create_rounds_zero_players_multiple_prints(self, mock_print):
        """Test para verificar múltiples prints cuando hay varios checks de 0 jugadores"""
        tournament = Tournament.objects.create(
            name='MultiCheckTournament',
            tournament_type=TournamentType.DOUBLEROUNDROBIN
        )
        
        # Llamar a create_rounds dos veces para verificar que el print ocurre cada vez
        result1 = create_rounds(tournament)
        result2 = create_rounds(tournament)
        
        # Verificar que se llamó a print dos veces con el mismo mensaje
        self.assertEqual(mock_print.call_count, 2)
        mock_print.assert_called_with("No hay jugadores en el torneo.")
        
        # Verificar resultados
        self.assertIsNone(result1)
        self.assertIsNone(result2)

    @tag("continua")
    @patch("builtins.print")
    def test_022_create_rounds_zero_players_with_swiss_byes(self, mock_print):
        """Test que verifica el print cuando hay 0 jugadores pero con swissByes"""
        tournament = Tournament.objects.create(
            name='SwissByesZeroPlayers',
            tournament_type=TournamentType.DOUBLEROUNDROBIN
        )
        
        # Llamar a create_rounds con swissByes pero sin jugadores
        result = create_rounds(tournament, swissByes=[1, 2])
        
        # Verificar que se imprimió el mensaje correcto
        mock_print.assert_called_once_with("No hay jugadores en el torneo.")
        
        # Verificar resultados
        self.assertIsNone(result)
        
        
        
        
        
class PlayerModelTest(TransactionTestCase):
    """Test the Player model"""
    # reset_sequences is used in the father class
    reset_sequences = True  # noqa E301

    def test_001_player_str_method(self):
        "create user and test str method"
        lichess_username = lichess_usernames_6[0]
        player = Player.objects.create(
            lichess_username=lichess_username)
        self.assertEqual(str(player), lichess_username)


    
    @tag("continua")
    @patch("requests.get", side_effect=requests.exceptions.RequestException("Error simulado"))
    def test_008_get_lichess_user_ratings_connection_error(self, mock_get):
        """Debe lanzar LichessAPIError si falla la conexión a Lichess en get_lichess_user_ratings"""
        player = Player(lichess_username="testuser")
        with self.assertRaises(LichessAPIError) as cm:
            player.get_lichess_user_ratings()
        self.assertIn("Nombre de usuario Lichess no proporcionado", str(cm.exception))
        
    
    @tag("continua")
    @patch("requests.get")
    def test_010_get_lichess_user_ratings_request_exception(self, mock_get):
        """
        Debe lanzar LichessAPIError si requests.get lanza una RequestException
        al intentar obtener los ratings de Lichess.
        """
        # Simulamos que requests.get lanza una RequestException
        mock_get.side_effect = requests.exceptions.RequestException("Falla de red simulada")

        player = Player(lichess_username="fake_user")

        with self.assertRaises(LichessAPIError) as context:
            player.get_lichess_user_ratings()

        self.assertIn("Nombre de usuario Lichess no proporcionado", str(context.exception))
        
        
        
    @tag("continua")
    @patch("builtins.print")
    @patch("requests.get", side_effect=requests.exceptions.RequestException("Error simulado"))
    def test_009_check_lichess_user_exists_connection_error(self, mock_get, mock_print):
        """Debe retornar False y mostrar un mensaje si falla la conexión en check_lichess_user_exists"""
        player = Player(lichess_username="testuser")
        exists = player.check_lichess_user_exists()
        self.assertFalse(exists)
        mock_print.assert_called_with("Error al verificar el usuario de Lichess: Error simulado")




class TournamentModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # Crear datos comunes
        self.referee = Referee.objects.create(name="Test Referee")
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Crear algunos jugadores de prueba
        self.player1 = Player.objects.create(
            name="Player1",
            lichess_username="player1",
            lichess_rating_rapid=1800,
            lichess_rating_bullet=1700,
            lichess_rating_blitz=1900,
            lichess_rating_classical=2000,
            fide_rating_rapid=2100,
            fide_rating_blitz=2200,
            fide_rating_classical=2300
        )
        self.player2 = Player.objects.create(
            name="Player2",
            lichess_username="player2",
            lichess_rating_rapid=1900,
            lichess_rating_bullet=1800,
            lichess_rating_blitz=2000,
            lichess_rating_classical=2100,
            fide_rating_rapid=2200,
            fide_rating_blitz=2300,
            fide_rating_classical=2400
        )
        
        self.player3 = Player.objects.create(
            name="Player3",
            lichess_rating_classical=2500,
            fide_rating_classical=2600
        )
        
    @tag("continua")
    def test_001_ranking_system_str(self):
        rs = RankingSystemClass.objects.create(value=RankingSystem.PLAIN_SCORE.value)
        self.assertEqual(str(rs), rs.get_value_display())

    @tag("continua")
    def test_002_tournament_player_str(self):
        tournament = Tournament.objects.create(name="Tournament A", referee=self.referee)
        tp = TournamentPlayer.objects.create(tournament=tournament, player=self.player1)
        self.assertEqual(str(tp), f"{tournament.name} - {self.player1.name}")

    @tag("continua")
    def test_003_get_players_unsorted(self):
        tournament = Tournament.objects.create(
            name="T1",
            referee=self.referee,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB
        )
        tournament.players.add(self.player1, self.player2)
        players = tournament.getPlayers(sorted=False)
        self.assertEqual(set(players), {self.player1, self.player2})

    @tag("continua")
    def test_004_get_players_sorted_fide_classical(self):
        tournament = Tournament.objects.create(
            name="T2",
            referee=self.referee,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player2, self.player1])

    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_005_add_duplicate_ranking_to_list(self, mock_stdout):
        tournament = Tournament.objects.create(name="T", referee=self.referee)
        
        # Primera adición
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)
        
        # Segunda adición del mismo valor
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)
        
        output = mock_stdout.getvalue()
        self.assertIn("Error: El objeto ya existe en la lista de ranking.", output)
        self.assertEqual(tournament.rankingList.count(), 1)  # Solo debería estar una vez

    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_006_remove_nonexistent_ranking_from_list(self, mock_stdout):
        tournament = Tournament.objects.create(name="T", referee=self.referee)
        
        # Intentar eliminar un ranking que no existe
        tournament.removeFromRankingList("ZZ")
        
        output = mock_stdout.getvalue()
        self.assertIn("No se encontró el ranking con valor 'ZZ' en RankingSystemClass.", output)

    @tag("continua")
    def test_007_get_players_sorted_lichess_rapid(self):
        tournament = Tournament.objects.create(
            name="T_Rapid_Lichess",
            referee=self.referee,
            tournament_speed=TournamentSpeed.RAPID,
            board_type=TournamentBoardType.LICHESS
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player1, self.player2])

    @tag("continua")
    def test_008_get_players_sorted_lichess_bullet(self):
        tournament = Tournament.objects.create(
            name="T_Bullet_Lichess",
            referee=self.referee,
            tournament_speed=TournamentSpeed.BULLET,
            board_type=TournamentBoardType.LICHESS
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player1, self.player2])

    @tag("continua")
    def test_009_get_players_sorted_lichess_blitz(self):
        tournament = Tournament.objects.create(
            name="T_Blitz_Lichess",
            referee=self.referee,
            tournament_speed=TournamentSpeed.BLITZ,
            board_type=TournamentBoardType.LICHESS
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player1, self.player2])

    @tag("continua")
    def test_010_get_players_sorted_lichess_classical(self):
        tournament = Tournament.objects.create(
            name="T_Classical_Lichess",
            referee=self.referee,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player1, self.player2])

    @tag("continua")
    def test_011_get_players_sorted_otb_rapid(self):
        tournament = Tournament.objects.create(
            name="T_OTB_Rapid",
            referee=self.referee,
            tournament_speed=TournamentSpeed.RAPID,
            board_type=TournamentBoardType.OTB
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player2, self.player1])

    @tag("continua")
    def test_012_get_players_sorted_default_case(self):
        tournament = Tournament.objects.create(
            name="T_Default",
            referee=self.referee,
            tournament_speed="ZZ",  # valores no contemplados
            board_type="XXX"
        )
        tournament.players.add(self.player1, self.player2)
        players = tournament.getPlayers(sorted=True)
        self.assertEqual(set(players), {self.player1, self.player2})

    @tag("continua")
    def test_013_get_games(self):
        tournament = Tournament.objects.create(name="T", referee=self.referee)
        round1 = Round.objects.create(tournament=tournament)
        round2 = Round.objects.create(tournament=tournament)

        game1 = Game.objects.create(round=round1, white=self.player1, black=self.player2)
        game2 = Game.objects.create(round=round2, white=self.player2, black=self.player1)

        games = tournament.getGames()
        self.assertEqual(len(games), 2)
        self.assertIn(game1, games)
        self.assertIn(game2, games)

    @tag("continua")
    def test_014_get_players_sorted_fide_blitz(self):
        tournament = Tournament.objects.create(
            name="T3",
            referee=self.referee,
            tournament_speed=TournamentSpeed.BLITZ,
            board_type=TournamentBoardType.OTB
        )
        tournament.players.add(self.player1, self.player2)
        sorted_players = tournament.getPlayers(sorted=True)
        self.assertEqual(sorted_players, [self.player2, self.player1])

    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_add_to_ranking_list_duplicate_raises_exception(self, mock_stdout):
        tournament = Tournament.objects.create(name="T4", referee=self.referee)
        
        # Primera adición
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)
        
        # Segunda adición
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)
        
        output = mock_stdout.getvalue()
        self.assertIn("Error: El objeto ya existe en la lista de ranking.", output)

    @tag("continua")
    def test_clean_ranking_list(self):
        tournament = Tournament.objects.create(name="T5", referee=self.referee)
        rs1 = RankingSystemClass.objects.create(value=RankingSystem.PLAIN_SCORE.value)
        rs2 = RankingSystemClass.objects.create(value=RankingSystem.WINS.value)
        tournament.rankingList.add(rs1, rs2)

        tournament.cleanRankingList()
        self.assertEqual(tournament.rankingList.count(), 0)

    @tag("continua")
    def test_get_scores_white_win_black_empty(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="T6", 
            referee=self.referee,
            win_points=1.0
        )
        round = Round.objects.create(tournament=tournament)

        game = Game.objects.create(
            round=round, 
            white=self.player1, 
            result=Scores.WHITE.value,
            finished=True
        )
        
        TournamentPlayer.objects.create(player=self.player1, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player2, tournament=tournament)

        scores = getScores(tournament)
        self.assertEqual(scores[self.player1][PLAIN_SCORE], 0.0)
        self.assertEqual(scores[self.player2][PLAIN_SCORE], 0.0)  # player2 no jugó

    @tag("continua")
    def test_015_get_players_count(self):
        tournament = Tournament.objects.create(name="PlayerCountTest", referee=self.referee)
        tournament.players.add(self.player1, self.player2)
        self.assertEqual(tournament.getPlayersCount(), 2)

    @tag("continua")
    def test_016_get_round_count(self):
        tournament = Tournament.objects.create(name="RoundCountTest", referee=self.referee)
        Round.objects.create(name="Round1", tournament=tournament)
        Round.objects.create(name="Round2", tournament=tournament)
        self.assertEqual(tournament.getRoundCount(), 2)

    @tag("continua")
    def test_017_number_of_rounds_with_games(self):
        tournament = Tournament.objects.create(name="RoundsWithGames", referee=self.referee)
        round1 = Round.objects.create(name="R1", tournament=tournament)
        round2 = Round.objects.create(name="R2", tournament=tournament)
        Game.objects.create(round=round1, white=self.player1, black=self.player2)
        
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 1)

    @tag("continua")
    def test_018_latest_round_with_games(self):
        tournament = Tournament.objects.create(name="LatestRoundTest", referee=self.referee)
        round1 = Round.objects.create(name="R1", tournament=tournament, start_date=timezone.now())
        round2 = Round.objects.create(name="R2", tournament=tournament, 
                                    start_date=timezone.now() + timezone.timedelta(days=1))
        Game.objects.create(round=round2, white=self.player1, black=self.player2)
        
        latest = tournament.get_latest_round_with_games()
        self.assertEqual(latest, round2)

    @tag("continua")
    def test_019_get_scores_draw(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="DrawTest",
            referee=self.referee,
            win_points=1.0,
            draw_points=0.5,
            lose_points=0.0
        )
        round = Round.objects.create(tournament=tournament)
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player2,
            result=Scores.DRAW.value,
            finished=True
        )
        
        TournamentPlayer.objects.create(player=self.player1, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player2, tournament=tournament)

        scores = getScores(tournament)
        self.assertEqual(scores[self.player1][PLAIN_SCORE], 0.5)
        self.assertEqual(scores[self.player2][PLAIN_SCORE], 0.5)

    @tag("continua")
    def test_020_get_scores_black_win(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="BlackWinTest",
            referee=self.referee,
            win_points=1.0,
            draw_points=0.5,
            lose_points=0.0
        )
        round = Round.objects.create(tournament=tournament)
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player2,
            result=Scores.BLACK.value,
            finished=True
        )
        
        TournamentPlayer.objects.create(player=self.player1, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player2, tournament=tournament)

        scores = getScores(tournament)
        self.assertEqual(scores[self.player1][PLAIN_SCORE], 0.0)
        self.assertEqual(scores[self.player2][PLAIN_SCORE], 1.0)

    @tag("continua")
    def test_021_get_black_wins_stats(self):
        WINS = RankingSystem.WINS.value
        BLACKTIMES = RankingSystem.BLACKTIMES.value
        
        tournament = Tournament.objects.create(
            name="BlackWinsTest",
            referee=self.referee
        )
        round = Round.objects.create(tournament=tournament)
        
        # Jugador 2 gana con negras
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player2,
            result=Scores.BLACK.value,
            finished=True
        )
        
        # Jugador 1 gana con blancas
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player3,
            result=Scores.WHITE.value,
            finished=True
        )
        
        TournamentPlayer.objects.create(player=self.player1, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player2, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player3, tournament=tournament)
        # Obtener estadísticas

        scores = getScores(tournament)
        results = getBlackWins(tournament, scores)
        
        self.assertEqual(results[self.player2][WINS], 1)  # Ganó con negras
        self.assertEqual(results[self.player2][BLACKTIMES], 1)  # Jugó con negras
        self.assertEqual(results[self.player1][WINS], 1)  # Ganó con blancas
        self.assertEqual(results[self.player1][BLACKTIMES], 0)  # No jugó con negras

    @tag("continua")
    def test_022_get_ranking_with_criteria(self):
        # Configurar torneo con criterios de desempate
        tournament = Tournament.objects.create(
            name="RankingTest",
            referee=self.referee
        )
        tournament.addToRankingList(RankingSystem.WINS.value)
        tournament.addToRankingList(RankingSystem.BLACKTIMES.value)
        
        # Crear partidas
        round = Round.objects.create(tournament=tournament)
        
        # player2 gana con negras
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player2,
            result=Scores.BLACK.value,
            finished=True
        )
        
        # player1 y player3 empatan
        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player3,
            result=Scores.DRAW.value,
            finished=True
        )
        
        TournamentPlayer.objects.create(player=self.player1, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player2, tournament=tournament)
        TournamentPlayer.objects.create(player=self.player3, tournament=tournament)
        
        ranking = getRanking(tournament)
        
        # Verificar orden esperado: player2 (1 victoria), player1 (0.5 puntos), player3 (0.5 puntos)
        self.assertEqual(ranking[self.player2]['rank'], 1)
        self.assertEqual(ranking[self.player1]['rank'], 3)
        self.assertEqual(ranking[self.player3]['rank'], 2)

    @tag("continua")
    def test_023_tournament_str(self):
        tournament = Tournament.objects.create(name="Test Tournament", referee=self.referee)
        self.assertEqual(str(tournament), "Test Tournament")

    @tag("continua")
    def test_024_add_player_through_tournament_player(self):
        tournament = Tournament.objects.create(name="PlayerAddTest", referee=self.referee)
        tp = TournamentPlayer.objects.create(tournament=tournament, player=self.player1)
        
        self.assertEqual(tournament.players.count(), 1)
        self.assertEqual(tp.tournament, tournament)
        self.assertEqual(tp.player, self.player1)

    @tag("continua")
    def test_025_tournament_creation_with_all_fields(self):
        tournament = Tournament.objects.create(
            name="Full Tournament",
            administrativeUser=self.user,
            referee=self.referee,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7),
            max_update_time=86400,
            only_administrative=True,
            tournament_type="RR",
            tournament_speed=TournamentSpeed.BLITZ.value,
            board_type=TournamentBoardType.LICHESS.value,
            win_points=1.0,
            draw_points=0.5,
            lose_points=0.0,
            timeControl="10+0",
            number_of_rounds_for_swiss=5
        )
        
        self.assertEqual(tournament.name, "Full Tournament")
        self.assertEqual(tournament.administrativeUser, self.user)
        self.assertEqual(tournament.tournament_speed, TournamentSpeed.BLITZ.value)

    @tag("continua")
    def test_026_get_ranking_without_games(self):
        tournament = Tournament.objects.create(
            name="EmptyRankingTest",
            referee=self.referee
        )
        tournament.players.add(self.player1, self.player2, self.player3)
        
        ranking = getRanking(tournament)
        
        # Debería devolver los jugadores en el orden por defecto
        self.assertEqual(len(ranking), 3)
        self.assertIn(self.player1, ranking)
        self.assertIn(self.player2, ranking)
        self.assertIn(self.player3, ranking)
        
        
    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_add_to_ranking_list_raises_exception_and_prints(self, mock_stdout):
        tournament = Tournament.objects.create(name="ErrorTest", referee=self.referee)

        # Creamos un ranking_obj válido
        ranking_obj = RankingSystemClass.objects.create(value=RankingSystem.PLAIN_SCORE.value)

        # Mockeamos el método 'add' para lanzar una excepción
        with patch.object(tournament.rankingList, 'add', side_effect=Exception("Simulated add error")):
            tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)

        output = mock_stdout.getvalue()

        self.assertIn("Error: El objeto ya existe en la lista de ranking.", output)
        self.assertIn("Error: El objeto ya existe en la lista de ranking.\n", output)
        
        
    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_add_to_ranking_list_forces_exception_in_add(self, mock_stdout):
        tournament = Tournament.objects.create(name="ErrorTest", referee=self.referee)

        # Creamos manualmente el objeto RankingSystemClass para que ya exista
        ranking_obj = RankingSystemClass.objects.create(value=RankingSystem.PLAIN_SCORE.value)

        # Agregamos el objeto para simular duplicado
        tournament.rankingList.add(ranking_obj)

        # Ahora parcheamos el método `add` del campo `rankingList` para que dispare una excepción
        with patch.object(tournament.rankingList, 'add', side_effect=Exception("Mocked exception on add")):
            # Volvemos a llamar al método (debería entrar al except)
            tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)

        output = mock_stdout.getvalue()

        self.assertIn("Error: El objeto ya existe en la lista de ranking.", output)
        self.assertIn("Error: El objeto ya existe en la lista de ranking.\n", output)
        
        
        
    @tag("continua")
    def test_get_scores_with_bye_for_white_player(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="ByeWhiteTest",
            referee=self.referee,
            win_points=1.0
        )
        tournament.players.add(self.player1)

        round = Round.objects.create(tournament=tournament)

        Game.objects.create(
            round=round,
            white=self.player1,
            black=None,
            result=Scores.BYE_F.value,
            finished=True
        )

        scores = getScores(tournament)

        self.assertEqual(scores[self.player1][PLAIN_SCORE], 1.0)
        
        
    @tag("continua")
    def test_get_scores_with_bye_for_black_player(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="ByeBlackTest",
            referee=self.referee,
            win_points=1.0
        )
        tournament.players.add(self.player2)

        round = Round.objects.create(tournament=tournament)

        Game.objects.create(
            round=round,
            white=None,
            black=self.player2,
            result=Scores.BYE_F.value,
            finished=True
        )

        scores = getScores(tournament)

        self.assertEqual(scores[self.player2][PLAIN_SCORE], 1.0)



    @tag("continua")
    def test_get_scores_with_unforced_bye_black(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="ByeUBlackTest",
            referee=self.referee,
            win_points=1.0
        )
        tournament.players.add(self.player2)

        round = Round.objects.create(tournament=tournament)

        Game.objects.create(
            round=round,
            white=None,
            black=self.player2,
            result=Scores.BYE_U.value,
            finished=True
        )

        scores = getScores(tournament)

        self.assertEqual(scores[self.player2][PLAIN_SCORE], 1.0)




    @tag("continua")
    def test_get_scores_with_forced_bye_black(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="ByeHBlackTest",
            referee=self.referee,
            draw_points=0.5
        )
        tournament.players.add(self.player2)

        round = Round.objects.create(tournament=tournament)

        Game.objects.create(
            round=round,
            white=None,
            black=self.player2,
            result=Scores.BYE_H.value,
            finished=True
        )

        scores = getScores(tournament)

        self.assertEqual(scores[self.player2][PLAIN_SCORE], 0.5)


    
    @tag("continua")
    def test_get_scores_with_bye_z_is_ignored(self):
        PLAIN_SCORE = RankingSystem.PLAIN_SCORE.value
        tournament = Tournament.objects.create(
            name="ByeZIgnoreTest",
            referee=self.referee,
            win_points=1.0,
            draw_points=0.5,
            lose_points=0.0
        )
        tournament.players.add(self.player1, self.player2)

        round = Round.objects.create(tournament=tournament)

        Game.objects.create(
            round=round,
            white=self.player1,
            black=self.player2,
            result=Scores.BYE_Z.value,
            finished=True
        )

        scores = getScores(tournament)

        self.assertEqual(scores[self.player1][PLAIN_SCORE], 0.0)
        self.assertEqual(scores[self.player2][PLAIN_SCORE], 0.0)

