from django.test import tag, TransactionTestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from chess_models.models import Game, Player, Tournament, RankingSystemClass, Round, TournamentBoardType, TournamentType, Scores, TournamentPlayer, RankingSystem
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch



class TestCustomUserViewSet(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
    
    @tag("continua")
    def test_user_creation_not_allowed(self):
        response = self.client.post('/auth/users/', data={
            "email": "test@example.com",
            "password": "12345678"
        })
        self.assertEqual(response.status_code, 404)
        #self.assertFalse(response.data["result"])
        #self.assertEqual(response.data["message"], "User creation not allowed via API")


class TestGameViewSet(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        
    @tag("continua")
    def test_update_game_invalid_result_value(self):
        # Crear jugadores
        white = Player.objects.create(name="Player 1")
        black = Player.objects.create(name="Player 2")

        # Crear un torneo para asociar al Round
        tournament = Tournament.objects.create(name="Tournament 1", administrativeUser=None)

        # Crear un Round asociado al torneo
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        # Crear el juego con el round_id válido
        game = Game.objects.create(white=white, black=black, finished=False, round_id=round_obj.id)

        # Realizar la solicitud PATCH con un valor de resultado inválido
        url = reverse('game-detail', args=[game.id])
        response = self.client.patch(url, data={"result": "invalid_value"}, format="json")
        # Verificar que la respuesta sea la esperada
        self.assertEqual(response.status_code, 400)
        #self.assertFalse(response.data["result"])
        #self.assertEqual(response.data["message"], "Invalid result value")

class CustomUserViewSetTest(APITestCase):
    @tag("continua")
    def test_user_creation_not_allowed(self):
        # URL de la vista que maneja la creación de usuarios
        url = '/api/v1/users/'  # Ajusta esto al nombre de la URL de tu vista

        # Datos que se intentan enviar en la solicitud POST
        data = {
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com"
        }

        # Realiza la solicitud POST para crear un usuario
        response = self.client.post(url, data, format='json')

        # Verifica que la respuesta tenga el código de estado 405
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Verifica que el mensaje de la respuesta sea el esperado
        self.assertEqual(response.data["message"], "User creation not allowed via API")

        # Verifica que el campo 'result' en la respuesta sea False
        self.assertFalse(response.data["result"])
        

        
        
    
class CreateRoundAPIViewTest(TransactionTestCase):
    """Test the round API"""
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.create_round_url = '/api/v1/create_round/'  # URL de la API para crear ronda

    @tag("continua")
    def test_missing_tournament_id(self):
        """Test cuando falta el `tournament_id` en la solicitud."""
        # Realizamos la solicitud sin el campo `tournament_id`
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_round_url, {})
        
        # Verificamos que el código de estado es 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "Missing tournament_id")

    @tag("continua")
    def test_tournament_does_not_exist(self):
        """Test cuando el `tournament_id` no existe."""
        # Usamos un ID de torneo que no existe
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_round_url, {'tournament_id': 99999})

        # Verificamos que la respuesta indica que el torneo no existe
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "Tournament with id 99999 does not exist")

    @tag("continua")
    def test_tournament_has_no_players(self):
        """Test cuando el torneo no tiene jugadores."""
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            
            board_type=TournamentBoardType.LICHESS)
        self.client.force_authenticate(user=self.user)
        
        # Realizamos la solicitud para crear una ronda
        response = self.client.post(self.create_round_url, {'tournament_id': tournament.id})
        
        # Verificamos que la respuesta es un error debido a la falta de jugadores
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], f"Tournament with id {tournament.id} has no players")

    """
    @tag("continua")
    @patch("chess_models.models.create_rounds", side_effect=Exception("Error creating rounds"))
    def test_error_creating_rounds(self, mock_create_rounds):
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            
            board_type=TournamentBoardType.LICHESS)
        tournament.addToRankingList("R")
        player = Player.objects.create(lichess_username="Player1")
        tournament.players.add(player)
        
        self.client.force_authenticate(user=self.user)
        
        # Intentamos crear rondas cuando la función `create_rounds` lanza una excepción
        response = self.client.post(self.create_round_url, {'tournament_id': tournament.id})
        
        # Verificamos que la respuesta indique un error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "An error occurred while creating rounds: Error creating rounds")
    
    @tag("continua")
    def test_tournament_has_no_rounds_after_creation(self):
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            
            board_type=TournamentBoardType.LICHESS)
        tournament.addToRankingList("R")
        
        # Creamos un jugador para el torneo
        player = Player.objects.create(lichess_username="Player1")
        tournament.players.add(player)
        
        self.client.force_authenticate(user=self.user)
        
        # Realizamos la solicitud para crear la ronda
        response = self.client.post(self.create_round_url, {'tournament_id': tournament.id})
        
        # Verificamos que el código de estado sea 400 si no se crean rondas
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], f"Tournament with id {tournament.id} has no rounds")
    
    
    @tag("continua")
    def test_create_rounds_failure(self):
        
        # Crear un torneo para este test
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            board_type=TournamentBoardType.LICHESS
        )

        # Mockear la función create_rounds para que devuelva -1 (simulando un error)
        with patch('api.views.create_rounds', return_value=-1):
            self.client.force_authenticate(user=self.user)
            response = self.client.post(self.create_round_url, {'tournament_id': tournament.id})
        
        # Verificar que la respuesta es un error 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['result'], False)
        self.assertTrue(response.data['message'].startswith('An error occurred while creating rounds'))
    """
    
    @tag("continua")
    def test_create_round_success(self):
        """Test cuando la creación de la ronda es exitosa."""
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            
            board_type=TournamentBoardType.LICHESS)
        tournament.addToRankingList("R")
        
        # Añadir varios jugadores
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(lichess_username=f"Player{i+1}")
            tournament.players.add(player)
        
        # Creamos la ronda
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_round_url, {'tournament_id': tournament.id})
        
        # Verificamos que la respuesta es correcta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['result'], True)
        self.assertEqual(tournament.round_set.count(), NoItems - 1)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        self.assertEqual(len(tournament.getGames()), (NoItems - 1) * NoItems // 2)
        
        
        
class SearchTournamentsAPIViewTest(TransactionTestCase):
    """Test the search tournaments API"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/searchTournaments/'  # URL de la API de búsqueda de torneos

    @tag("continua")
    def test_missing_search_string(self):
        """Test cuando falta el `search_string` en la solicitud."""
        # Realizamos la solicitud sin el campo `search_string`
        response = self.client.post(self.url, {})
        
        # Verificamos que el código de estado es 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "search_string is required")

    @tag("continua")
    def test_empty_search_string(self):
        """Test cuando el `search_string` está vacío."""
        # Realizamos la solicitud con un `search_string` vacío
        response = self.client.post(self.url, {'search_string': ''})
        
        # Verificamos que el código de estado es 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "search_string is required")
        
        
        
        
class TournamentCreateAPIViewTest(TransactionTestCase):
    """Test for the Tournament creation API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = '/api/v1/tournament_create/'  # URL de la API para crear torneos

    @tag("continua")
    def test_create_tournament_success(self):
        """Test creating a tournament successfully"""
        data = {
            "name": "Test Tournament",
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
            "rankingList": [],
            "players": "",  # No players in CSV
        }

        self.client.force_authenticate(user=self.user)
        
        #print("URL:", self.url)
        #print("Data:", data)
        response = self.client.post(self.url, data)
        #print("Response:", response)
        #print("Response Data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['tournament_type'], data['tournament_type'])
        self.assertEqual(response.data['board_type'], data['board_type'])

    """"""
    @tag("continua")
    def test_create_tournament_duplicate_name(self):
        """Test creating a tournament with a duplicate name"""
        Tournament.objects.create(
            name="Test Tournament",
            administrativeUser=self.user,
            tournament_type=TournamentType.ROUNDROBIN,
            board_type=TournamentBoardType.OTB,
            win_points=1.0,
            draw_points=0.5,
            lose_points=0.0,
            tournament_speed="ra"
        )

        data = {
            "name": "Test Tournament",  # Same name as existing one
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "A tournament with that name already exists.")

    """
    @tag("continua")
    def test_missing_name(self):
        
        data = {
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertEqual(response.data['message'], "'name' is required")
    """

    @tag("continua")
    def test_create_tournament_with_csv_players(self):
        """Test creating a tournament with players from a CSV"""
        csv_data = '''nombre,email
        "Player One",player1@example.com
        "Player Two",player2@example.com
        '''

        data = {
            "name": "Test Tournament with Players",
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
            "players": csv_data,
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(TournamentPlayer.objects.count(), 2)  # Ensure two players were added


    @tag("continua")
    def test_create_tournament_with_invalid_csv(self):
        """Test when invalid CSV data is provided for players"""
        invalid_csv_data = '''name,email
        "Player One",player1@example.com
        "Player Two",player2@example.com
        '''

        data = {
            "name": "Test Tournament with Invalid CSV",
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
            "players": invalid_csv_data,
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertIn("Error creating tournament", response.data['message'])


    @tag("continua")
    def test_create_tournament_missing_required_fields(self):
        """Test when required fields are missing"""
        data = {
            "name": "Incomplete Tournament",
            "tournament_type": TournamentType.ROUNDROBIN,
            # Missing 'board_type'
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result'], False)
        self.assertIn("Error creating tournament", response.data['message'])
        
        
    @tag("continua")
    def test_create_tournament_with_lichess_players(self):
        """Test crear un torneo con jugadores de Lichess usando CSV"""
        csv_players = "lichess_username\nplayer1\nplayer2\n"

        data = {
            "name": "Lichess Test Tournament",
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.LICHESS,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
            "rankingList": [],
            "players": csv_players,
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)
        #print("Response:", response)
        # Asegura que el torneo fue creado correctamente
        self.assertEqual(response.status_code, 201)
        tournament_id = response.data['id']
        tournament = Tournament.objects.get(id=tournament_id)

        # Verifica que los jugadores fueron creados
        players = Player.objects.filter(lichess_username__in=["player1", "player2"])
        self.assertEqual(players.count(), 2)

        # Verifica que están vinculados al torneo
        tournament_players = TournamentPlayer.objects.filter(tournament=tournament)
        self.assertEqual(tournament_players.count(), 2)

        usernames = [tp.player.lichess_username for tp in tournament_players]
        self.assertIn("player1", usernames)
        self.assertIn("player2", usernames)
        
    @tag("continua")
    def test_create_tournament_with_ranking_list(self):
        """Debe asignar rankingList correctamente al crear el torneo"""

        # Crear instancias válidas de RankingSystemClass
        r1 = RankingSystemClass.objects.create(value=RankingSystem.BUCHHOLZ)
        r2 = RankingSystemClass.objects.create(value=RankingSystem.WINS)

        data = {
            "name": "Torneo con ranking list",
            "tournament_type": TournamentType.ROUNDROBIN,
            "board_type": TournamentBoardType.OTB,
            "win_points": 1.0,
            "draw_points": 0.5,
            "lose_points": 0.0,
            "tournament_speed": "ra",
            "rankingList": [r1.pk, r2.pk],
            "players": ""
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        #print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tournament = Tournament.objects.get(id=response.data["id"])
        self.assertEqual(set(tournament.rankingList.all()), {r1, r2})

        
        
        
        
        
class GetRankingAPIViewTest(TransactionTestCase):
    """Tests for the GetRanking API endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.url_base = '/api/v1/get_ranking/'  # Asegúrate de que este sea el prefijo correcto de tu endpoint

    @tag("continua")
    def test_tournament_not_found(self):
        """Test cuando el torneo no existe"""
        nonexistent_id = 99999  # ID que no existe
        url = f"{self.url_base}{nonexistent_id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["result"], False)
        self.assertIn("not found", response.data["message"])
        
        
        
        
class continuaAPITest(TransactionTestCase):
    """Test for the continua API"""

    def setUp(self):
        self.client = APIClient()
        self.base_url = "/api/v1/get_round_results/"

    @tag("continua")
    def test_tournament_does_not_exist(self):
        """Debe devolver 404 si el torneo no existe"""
        response = self.client.get(f"{self.base_url}9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["result"], False)
        self.assertIn("not found", response.data["message"])

    @tag("continua")
    def test_tournament_has_no_rounds(self):
        """Torneo existe pero no tiene rondas"""
        tournament = Tournament.objects.create(
            name="Empty Tournament",
            tournament_type=TournamentType.ROUNDROBIN,
            board_type=TournamentBoardType.OTB
        )

        response = self.client.get(f"{self.base_url}{tournament.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})  # Dict vacío si no hay rondas

    @tag("continua")
    def test_round_with_games_and_players(self):
        """Debe devolver información de rondas con partidas y jugadores"""
        tournament = Tournament.objects.create(
            name="Full Tournament",
            tournament_type=TournamentType.ROUNDROBIN,
            board_type=TournamentBoardType.OTB
        )

        player_white = Player.objects.create(name="Magnus")
        player_black = Player.objects.create(name="Ian")

        rnd = Round.objects.create(tournament=tournament, name="Round 1")
        Game.objects.create(round=rnd, white=player_white, black=player_black, result="W")

        response = self.client.get(f"{self.base_url}{tournament.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estructura del dict
        round_data = response.data["0"]
        self.assertEqual(round_data["round_name"], "Round 1")
        self.assertIn("games", round_data)

        game = round_data["games"]["1"]
        self.assertEqual(game["white_name"], "Magnus")
        self.assertEqual(game["black_name"], "Ian")
        self.assertEqual(game["result"], "W")

    @tag("continua")
    def test_round_with_lichess_usernames(self):
        """Verifica que use lichess_username si está disponible"""
        tournament = Tournament.objects.create(
            name="Lichess Tournament",
            tournament_type=TournamentType.ROUNDROBIN,
            board_type=TournamentBoardType.LICHESS
        )

        white = Player.objects.create(name="Jugador Blanco", lichess_username="superGM")
        black = Player.objects.create(name="Jugador Negro", lichess_username="anotherGM")

        rnd = Round.objects.create(tournament=tournament, name="Round 1")
        Game.objects.create(round=rnd, white=white, black=black, result="W")

        response = self.client.get(f"{self.base_url}{tournament.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        game = response.data["0"]["games"]["1"]
        self.assertEqual(game["white_name"], "superGM")
        self.assertEqual(game["black_name"], "anotherGM")
        self.assertEqual(game["result"], "W")
        
        
class GetPlayersAPIViewTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/get_players/'

    @tag("continua")
    def test_tournament_not_found(self):
        """Debe devolver 404 si el torneo no existe"""
        response = self.client.get(f"{self.url}9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["result"])
        self.assertIn("not found", response.data["message"])


class UpdateLichessGameAPIViewTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/update_lichess_game/"

    @tag("continua")
    def test_game_does_not_exist(self):
        """Debe devolver 404 si el game_id no corresponde a un juego existente"""
        data = {"game_id": 999, "lichess_game_id": "abcd1234"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["result"])
        self.assertIn("Game does not exist", response.data["message"])

    @tag("continua")
    def test_game_is_finished_blocked(self):
        """Debe devolver 400 si el juego está terminado y no se puede editar"""
        
        white = Player.objects.create(name="Player 1")
        black = Player.objects.create(name="Player 2")

        tournament = Tournament.objects.create(name="Tournament 1", administrativeUser=None)
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        game = Game.objects.create(
            white=white,
            black=black,
            round=round_obj,
            result="W",
            finished=True
        )

        data = {"game_id": game.id, "lichess_game_id": "abcd1234"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["result"])
        self.assertIn("Game is blocked", response.data["message"])




class UpdateOTBGameAPIViewTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/update_otb_game/"

    @tag("continua")
    def test_game_does_not_exist_otb(self):
        """Debe devolver 404 si el game_id no corresponde a un juego existente"""
        data = {"game_id": 999, "otb_result": "w", "email": "test@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["result"])
        self.assertIn("Game does not exist", response.data["message"])

    @tag("continua")
    def test_game_is_finished_otb(self):
        """Debe devolver 400 si el juego ya está terminado"""
        white = Player.objects.create(name="Player 1", email="white@example.com")
        black = Player.objects.create(name="Player 2", email="black@example.com")
        tournament = Tournament.objects.create(name="Torneo 1", administrativeUser=None)
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        game = Game.objects.create(
            white=white,
            black=black,
            round=round_obj,
            result="W",
            finished=True
        )

        data = {"game_id": game.id, "otb_result": "b", "email": black.email}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["result"])
        self.assertIn("Game is blocked", response.data["message"])

    @tag("continua")
    def test_invalid_result_value_otb(self):
        """Debe devolver 400 si el otb_result es inválido"""
        white = Player.objects.create(name="Player 1", email="white@example.com")
        black = Player.objects.create(name="Player 2", email="black@example.com")
        tournament = Tournament.objects.create(name="Torneo 1", administrativeUser=None)
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        game = Game.objects.create(
            white=white,
            black=black,
            round=round_obj,
            finished=False
        )

        data = {"game_id": game.id, "otb_result": "x", "email": white.email}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["result"])
        self.assertIn("Invalid result value", response.data["message"])

    @tag("continua")
    def test_invalid_email_otb(self):
        """Debe devolver 400 si el email no coincide con ningún jugador"""
        white = Player.objects.create(name="Player 1", email="white@example.com")
        black = Player.objects.create(name="Player 2", email="black@example.com")
        tournament = Tournament.objects.create(name="Torneo 1", administrativeUser=None)
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        game = Game.objects.create(
            white=white,
            black=black,
            round=round_obj,
            finished=False
        )

        data = {"game_id": game.id, "otb_result": "w", "email": "intruso@example.com"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["result"])
        self.assertIn("Email does not match", response.data["message"])

    @tag("continua")
    def test_draw_result_normalization_otb(self):
        """Debe actualizar correctamente un empate ('d' → '=')"""
        white = Player.objects.create(name="Player 1", email="white@example.com")
        black = Player.objects.create(name="Player 2", email="black@example.com")
        tournament = Tournament.objects.create(name="Torneo 1", administrativeUser=None)
        round_obj = Round.objects.create(name="Round 1", tournament=tournament)

        game = Game.objects.create(
            white=white,
            black=black,
            round=round_obj,
            finished=False
        )

        data = {"game_id": game.id, "otb_result": "d", "email": white.email}
        response = self.client.post(self.url, data)

        game.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["result"])
        self.assertEqual(game.result, Scores.DRAW.value)  # Debe ser "="
        self.assertTrue(game.finished)
        
        
        
class AdminUpdateGameAPIViewTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="admin", password="admin123")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/v1/admin_update_game/"

    @tag("continua")
    def test_game_does_not_exist_admin(self):
        """Debe devolver 404 si el game_id no corresponde a un juego existente"""
        data = {"game_id": 999, "otb_result": "w"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["result"])
        self.assertIn("Game does not exist", response.data["message"])

    @tag("continua")
    def test_invalid_result_value_admin(self):
        """Debe devolver 400 si el otb_result es inválido"""
        white = Player.objects.create(name="Player 1")
        black = Player.objects.create(name="Player 2")
        tournament = Tournament.objects.create(name="Torneo Admin", administrativeUser=self.user)
        round_obj = Round.objects.create(name="Ronda 1", tournament=tournament)
        game = Game.objects.create(white=white, black=black, round=round_obj)

        data = {"game_id": game.id, "otb_result": "x"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["result"])
        self.assertIn("Invalid result value", response.data["message"])

    @tag("continua")
    def test_draw_result_normalization_admin(self):
        """Debe actualizar correctamente un empate ('d' → '=')"""
        white = Player.objects.create(name="Player 1")
        black = Player.objects.create(name="Player 2")
        tournament = Tournament.objects.create(name="Torneo Admin", administrativeUser=self.user)
        round_obj = Round.objects.create(name="Ronda 1", tournament=tournament)
        game = Game.objects.create(white=white, black=black, round=round_obj, finished=False)

        data = {"game_id": game.id, "otb_result": "d"}
        response = self.client.post(self.url, data)

        game.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["result"])
        self.assertEqual(game.result, Scores.DRAW.value)  # "="
        self.assertTrue(game.finished)