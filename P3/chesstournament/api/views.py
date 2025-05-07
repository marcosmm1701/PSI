from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from chess_models.models import Tournament
from .serializers import TournamentSerializer, GameSerializer
from .serializers import PlayerSerializer, RefereeSerializer, RoundSerializer
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from chess_models.models import Game
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from chess_models.models import create_rounds
import csv
import io
from chess_models.models import TournamentBoardType
from chess_models.models import TournamentPlayer
from chess_models.models import Player
from chess_models.models import getRanking
from chess_models.models import Round
from chess_models.models import Referee
from chess_models.models import LichessAPIError
from chess_models.models import Scores


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all().order_by('-start_date', '-id')
    serializer_class = TournamentSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
        return super().get_permissions()


class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        return Response({"result": False,
                         "message": "User creation not allowed via API"},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_permissions(self):
        """
        Permisos personalizados:
        - Permite actualización sin autenticación SOLO si:
          * Es una acción de actualización (update/partial_update)
          * El juego no está finalizado (finished=False)
        - Requiere autenticación para cualquier otro caso
        """
        if self.action in ['update', 'partial_update']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        game = self.get_object()

        if game.finished:
            if not request.user.is_authenticated:
                return Response(
                    {"result": False,
                     "message": (
                         "Authentication required to update finished games")
                     },
                    status=status.HTTP_403_FORBIDDEN
                )

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(game,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        game.finished = True
        game.save()

        return Response(serializer.data)


class RefereeViewSet(viewsets.ModelViewSet):
    queryset = Referee.objects.all()
    serializer_class = RefereeSerializer
    permission_classes = [AllowAny]


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
    permission_classes = [AllowAny]


class CreateRoundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tournament_id = request.data.get('tournament_id')
        if tournament_id is None:
            return Response({
                "result": False,
                "message": "Missing tournament_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        tournament_id = int(tournament_id)
        # Buscamos el torneo
        try:
            tournament = Tournament.objects.get(id=tournament_id)

        except Tournament.DoesNotExist:
            return Response({
                "result": False,
                "message": f"Tournament with id {tournament_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if tournament.getPlayersCount() == 0:
            return Response({
                "result": False,
                "message": (
                    f"Tournament with id {tournament_id} has no players")
            }, status=status.HTTP_400_BAD_REQUEST)

        # Llamamos a tu función
        res = create_rounds(tournament, [])
        res = res
        """
        if tournament.getRoundCount() == 0:
            return Response({
                "result": False,
                "message": f"Tournament with id {tournament_id} has no rounds"
            }, status=status.HTTP_400_BAD_REQUEST)
        """

        return Response({
                "result": True,
                "message": (
                    f"Rounds created successfully"
                    f"for tournament {tournament.name}")
            }, status=status.HTTP_201_CREATED)


class SearchTournamentsAPIView(APIView):
    permission_classes = []
    pagination_class = CustomPagination

    def post(self, request):
        search_string = request.data.get("search_string", "").strip()

        if not search_string:
            return Response({
                "result": False,
                "message": "search_string is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = Tournament.objects.filter(
            name__icontains=search_string
        ).order_by('-id')  # Orden consistente

        serializer = TournamentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TournamentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get("name")
            if Tournament.objects.filter(name=name).exists():
                return Response({
                    "result": False,
                    "message": "A tournament with that name already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Creamos el torneo con los datos principales
            tournament = Tournament.objects.create(
                name=name,
                # Usa el usuario autenticado como administrador
                administrativeUser=request.user,
                only_administrative=request.data.get("only_administrative",
                                                     False),
                tournament_type=request.data.get("tournament_type"),
                board_type=request.data.get("board_type"),
                win_points=request.data.get("win_points", 1.0),
                draw_points=request.data.get("draw_points", 0.5),
                lose_points=request.data.get("lose_points", 0.0),
                tournament_speed=request.data.get("tournament_speed"),
                # timeControl=request.data.get("timeControl", "15+0"),
                # number_of_rounds_for_swiss=request.data.
                # get("number_of_rounds_for_swiss", 0),
            )

            # Añadir rankingList si se proporciona
            ranking_list_ids = request.data.get("rankingList", [])
            print(f"ranking_list_ids: {ranking_list_ids}")
            if ranking_list_ids:
                for ranking_list_id in ranking_list_ids:
                    tournament.addToRankingList(ranking_list_id)
                #tournament.rankingList.set(ranking_list_ids)

            # Procesar CSV de jugadores si se incluye
            players_csv = request.data.get("players", "").strip()
            if players_csv:
                # Limpiar cada línea del CSV para quitar espacios innecesarios
                lines = [line.strip() for line in players_csv.strip().splitlines() if line.strip()]
                players_io = io.StringIO("\n".join(lines))
                reader = csv.DictReader(players_io)

                if tournament.board_type == TournamentBoardType.OTB:
                    for row in reader:
                        # Limpiar cada campo de espacios en blanco
                        cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                        
                        player = Player.objects.create(
                            # Limpiar y validar cada campo
                            name = cleaned_row.get("name", "").strip(),
                            email = cleaned_row.get("email", "").strip().lower(),
                            #ANADIDO NUEVO
                            
                            fide_rating_blitz = self.clean_int_field(cleaned_row.get("fide_rating_blitz")),
                            fide_rating_rapid = self.clean_int_field(cleaned_row.get("fide_rating_rapid")),
                            fide_rating_classical = self.clean_int_field(cleaned_row.get("fide_rating_classical"))
                            
                        )
                        TournamentPlayer.objects.create(tournament=tournament,
                                                        player=player)

                elif tournament.board_type == TournamentBoardType.LICHESS:
                    for row in reader:
                        # Limpiar cada campo de espacios en blanco
                        cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                        print(f"cleaned_row: {cleaned_row}")
                        player = Player.objects.create(
                            lichess_username=cleaned_row.get("lichess_username", "").strip()
                        )
                        if(player.check_lichess_user_exists() == False):
                            return Response({
                                "result": False,
                                "message": (
                                    f"Error: can not add players to tournament"
                                )
                            }, status=status.HTTP_400_BAD_REQUEST)
                            
                        
                        TournamentPlayer.objects.create(tournament=tournament,
                                                        player=player)

            # Crear las rondas automáticamente
            create_rounds(tournament, [])

            serializer = TournamentSerializer(tournament)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "result": False,
                "message": f"Error creating tournament: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
            
    def clean_int_field(self, value):
        if value is None:
            return None
        value = value.strip()
        return int(value) if value.isdigit() else None


class GetRanking(APIView):
    permission_classes = []  # no requiere autenticación

    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({
                "result": False,
                "message": (
                    f"Error: Tournament with ID {tournament_id} not found.")
            }, status=status.HTTP_404_NOT_FOUND)

        ranking_data = getRanking(tournament)
        result = {}

        for player, player_data in ranking_data.items():
            entry = {
                "id": player.id,
                "name": player.lichess_username
                if player.lichess_username else player.name,
                "score": player_data.get("PS", 0),
                "rank": player_data.get("rank", 0)
            }

            if "WI" in player_data:
                entry["WI"] = player_data["WI"]
            if "BT" in player_data:
                entry["BT"] = player_data["BT"]

            result[player.id] = entry

        return Response(result, status=status.HTTP_200_OK)


class GetRoundResults(APIView):
    permission_classes = []
    authentication_classes = []  # Disables authentication

    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({
                "result": False,
                "message": f"Tournament with ID {tournament_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        rounds = Round.objects.filter(tournament=tournament).order_by("id")
        results = {}

        for round_index, rnd in enumerate(rounds):
            games = Game.objects.filter(round=rnd)
            #games = sorted(games,
                           #key=lambda g: getattr(g.white, "ranking", 0),
                           #reverse=True)
            games = games.order_by("id")

            games_dict = {}

            for game_index, game in enumerate(games, start=1):
                games_dict[str(game_index)] = {
                    "id": game.id,
                    "rankingOrder": getattr(game.white, "ranking", 0),
                    "white": game.white.id if game.white else None,
                    "white_name": (
                        game.white.lichess_username
                        if game.white and game.white.lichess_username
                        else (game.white.name if game.white else None)
                    ),
                    "black": game.black.id if game.black else None,
                    "black_name": (
                        game.black.lichess_username
                        if game.black and game.black.lichess_username
                        else (game.black.name if game.black else None)
                    ),
                    "result": game.result
                }

            results[str(round_index)] = {
                "round_id": rnd.id,
                "round_name": rnd.name,
                "start_date": rnd.start_date,
                "games": games_dict
            }

        return Response(results, status=status.HTTP_200_OK)


class GetPlayers(APIView):
    permission_classes = []

    def get(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({
                "result": False,
                "message": f"Tournament with ID {tournament_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        t = tournament
        players = Player.objects.filter(tournamentplayer__tournament=t)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateLichessGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"result": False,
                             "message": "Game does not exist"
                             }, status=status.HTTP_404_NOT_FOUND)

        if game.finished:

            return Response({"result": False,
                             "message": (
                                 "Game is blocked, " +
                                 "only administrator can update it"
                                 )
                             }, status=status.HTTP_400_BAD_REQUEST)

        try:
            id = lichess_game_id
            winner, white, black = game.get_lichess_game_result(id)
        except LichessAPIError as e:
            return Response({"result": False, "message": str(e)
                             }, status=status.HTTP_400_BAD_REQUEST)

        game.result = winner.value  # 'w', 'b' o '='
        game.finished = True
        game.save()

        return Response({"result": True,
                         "message": "Game result updated from Lichess"
                         }, status=status.HTTP_200_OK)


class UpdateOTBGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []     # disables authentication

    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')  # debe ser 'w', 'b', o 'd'
        email = request.data.get('email')

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"result": False,
                             "message": "Game does not exist"
                             }, status=status.HTTP_404_NOT_FOUND)

        if game.finished:
            print("Game is finished")
            return Response({"result": False,
                             "message": (
                                "Game is blocked, " +
                                "only administrator can update it"
                             )
                             }, status=status.HTTP_400_BAD_REQUEST)

        valid_result = otb_result in ['w', 'b', 'd']
        if not valid_result:
            print("Unvalid result value")
            return Response({"result": False,
                             "message": "Invalid result value"
                             }, status=status.HTTP_400_BAD_REQUEST)

        # Verificamos si el email corresponde al jugador blanco o negro
        valid_email = ((game.white and game.white.email.lower() == email.lower())
                       or (game.black and game.black.email.lower() == email.lower()))

        if not valid_email:
            print("Email does not match any player")
            return Response({"result": False,
                             "message": (
                                 "Email does not match any player in this game"
                             )
                             }, status=status.HTTP_400_BAD_REQUEST)

        # Normalizamos resultados: traducimos 'd' → '=' (empate)
        if otb_result == 'd':
            otb_result = Scores.DRAW.value

        game.result = otb_result
        game.finished = True
        game.save()

        return Response({"result": True, "message": "Game updated by player"
                         }, status=status.HTTP_200_OK)


class AdminUpdateGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        game_id = request.data.get('game_id')
        otb_result = request.data.get('otb_result')

        try:
            game = Game.objects.select_related('round__tournament')
            game = game.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"result": False, "message": "Game does not exist"
                             }, status=status.HTTP_404_NOT_FOUND)

        tournament = game.round.tournament
        if tournament.administrativeUser != request.user:
            return Response({"result": False,
                             "message": (
                                 "Only the user that create " +
                                 "the tournament can update it"
                             )
                             }, status=status.HTTP_403_FORBIDDEN)

        if otb_result not in ['w', 'b', 'd']:
            return Response({"result": False, "message": "Invalid result value"
                             }, status=status.HTTP_400_BAD_REQUEST)

        # Normalizamos resultados: traducimos 'd' → '=' (empate)
        if otb_result == 'd':
            otb_result = Scores.DRAW.value

        # Actualizamos el resultado de la partida
        game.result = otb_result
        game.finished = True
        game.save()

        return Response({"result": True,
                         "message": "Game updated by administrator"
                         }, status=status.HTTP_200_OK)
