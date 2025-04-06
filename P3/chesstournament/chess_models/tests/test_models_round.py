from django.test import TestCase, tag
from chess_models.models import Tournament, Round, Game, Player, constants
from ..models.constants import Scores
from unittest.mock import patch
from io import StringIO


class RoundModelTest(TestCase):
    @tag("continua")
    def test_001_round_tournament(self):
        "assign round to tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        round_name = 'round_01'
        round = Round.objects.create(
            name=round_name, tournament=tournament)
        self.assertEqual(round.tournament, tournament)
        



        ################## TESTS EXTRA ################
        
        
        
    @tag("continua")
    def test_002_round_str_returns_name(self):
        "Test that __str__ method returns the name of the round"
        tournament = Tournament.objects.create(name="Tournament X")
        round = Round.objects.create(name="Round X", tournament=tournament)
        self.assertEqual(str(round), "Round X")

    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_003_print_round_details_no_games(self, mock_stdout):
        "Test print_round_details when there are no games"
        tournament = Tournament.objects.create(name="Torneo Test")
        round = Round.objects.create(name="Ronda Test", tournament=tournament)
        round.print_round_details()

        output = mock_stdout.getvalue()
        self.assertIn("=== Round Details ===", output)
        self.assertIn("Round Name: Ronda Test", output)
        self.assertIn("Tournament: Torneo Test", output)
        self.assertIn("End Date: Not Finished", output)
        self.assertIn("Finished: No", output)
        self.assertIn("No games in this round.", output)

    @tag("continua")
    @patch("sys.stdout", new_callable=StringIO)
    def test_004_print_round_details_with_games(self, mock_stdout):
        "Test print_round_details when the round has associated games"
        tournament = Tournament.objects.create(name="Torneo Con Juegos")
        round = Round.objects.create(name="Ronda Con Juegos", tournament=tournament)

        player1 = Player.objects.create(name="Jugador 1")
        player2 = Player.objects.create(name="Jugador 2")

        # Creamos un juego asociado a esta ronda
        game = Game.objects.create(
            white=player1,
            black=player2,
            round=round,
            result=Scores.WHITE.value,
        )

        round.print_round_details()
        output = mock_stdout.getvalue()

        self.assertIn("=== Round Details ===", output)
        self.assertIn("Round Name: Ronda Con Juegos", output)
        self.assertIn("Tournament: Torneo Con Juegos", output)
        self.assertIn("Finished: No", output)
        self.assertIn(str(game), output)