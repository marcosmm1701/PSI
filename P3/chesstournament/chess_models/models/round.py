from django.db import models
from django.utils import timezone

class Round(models.Model):
    name = models.CharField(max_length= 128)
    tournament = models.ForeignKey("chess_models.Tournament", on_delete=models.RESTRICT, related_name="rounds")
    start_date = models.DateTimeField(default=timezone.now, null = True)
    end_date = models.DateTimeField(null = True)
    finish = models.BooleanField(default=False)
    game_set = models.ManyToManyField("chess_models.Game", blank=True, related_name="games_set")
    
    
    
    #funcion extra hecha para la comprobación de los tests
    def print_round_details(round_obj):
        """Imprime los detalles de una ronda con sus juegos asociados."""
        print("=== Round Details ===")
        print(f"Round Name: {round_obj.name}")
        print(f"Tournament: {round_obj.tournament.name if round_obj.tournament else 'Unknown'}")
        print(f"Start Date: {round_obj.start_date}")
        print(f"End Date: {round_obj.end_date if round_obj.end_date else 'Not Finished'}")
        print(f"Finished: {'Yes' if round_obj.finish else 'No'}")
        print("\n--- Games in this Round ---")
        
        games = round_obj.games.all()
        if games.exists():
            for game in games:
                print(game)
        else:
            print("No games in this round.")
        
        print("====================\n")