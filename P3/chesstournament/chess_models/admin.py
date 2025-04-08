from django.contrib import admin
from .models import Game, Round, Tournament
from .models import RankingSystemClass, Referee, Player

admin.site.register(Game)
admin.site.register(Round)
admin.site.register(Tournament)
admin.site.register(RankingSystemClass)
admin.site.register(Referee)
admin.site.register(Player)
