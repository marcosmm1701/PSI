from django.db import models
from django.utils import timezone


class Round(models.Model):
    name = models.CharField(max_length=128)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE) #CAMBIADO DE RESTRICT A CASCADE
    start_date = models.DateTimeField(default=timezone.now, null=True)
    end_date = models.DateTimeField(null=True)
    finish = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # funcion extra hecha para la comprobación de los tests
    def print_round_details(self):
        """Imprime los detalles de una ronda con sus juegos asociados."""
        print("=== Round Details ===")
        print(f"Round Name: {self.name}")
        tour_name = self.tournament.name if self.tournament else 'Unknown'
        print(f"Tournament: {tour_name}")
        print(f"Start Date: {self.start_date}")
        print(
            f"End Date: {self.end_date if self.end_date else 'Not Finished'}")
        print(f"Finished: {'Yes' if self.finish else 'No'}")
        print("\n--- Games in this Round ---")

        games = self.game_set.all()
        if games.exists():
            for game in games:
                print(game)
        else:
            print("No games in this round.")

        print("====================\n")
