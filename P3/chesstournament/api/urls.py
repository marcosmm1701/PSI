from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RefereeViewSet, PlayerViewSet, GameViewSet, TournamentViewSet,
    RoundViewSet, CustomUserViewSet,
    CreateRoundAPIView, SearchTournamentsAPIView, TournamentCreateAPIView,
    GetRanking, GetPlayers, GetRoundResults,
    UpdateLichessGameAPIView, UpdateOTBGameAPIView, AdminUpdateGameAPIView
)

router = DefaultRouter()
router.register(r'referees', RefereeViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'rounds', RoundViewSet)
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create_round/', CreateRoundAPIView.as_view()),
    path('searchTournaments/', SearchTournamentsAPIView.as_view()),
    path('tournament_create/', TournamentCreateAPIView.as_view()),
    path('get_ranking/<int:tournament_id>/', GetRanking.as_view()),
    path('get_players/<int:tournament_id>/', GetPlayers.as_view()),
    path('get_round_results/<int:tournament_id>/', GetRoundResults.as_view()),
    path('update_lichess_game/', UpdateLichessGameAPIView.as_view()),
    path('update_otb_game/', UpdateOTBGameAPIView.as_view()),
    path('admin_update_game/', AdminUpdateGameAPIView.as_view()),
]
