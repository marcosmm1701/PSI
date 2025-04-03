from django.db import models
from .player import Player
from .round import Round
from .constants import Scores
from .other_models import LichessAPIError
import requests
from django.utils import timezone

class Game(models.Model):
    white = models.ForeignKey(Player, null=True, on_delete=models.CASCADE, related_name='games_as_white')
    black = models.ForeignKey(Player, null=True, on_delete=models.CASCADE,related_name='games_as_black')
    finished = models.BooleanField(default=False)
    round = models.ForeignKey(Round, on_delete=models.RESTRICT)
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    result = models.CharField(
        max_length=1, 
        choices=Scores.choices, 
        default=Scores.NOAVAILABLE
    )
    rankingOrder = models.IntegerField(default=0, null=True)

    def __str__(self):
        white_name = self.white.name if self.white else "Bye"
        black_name = self.black.name if self.black else "Bye"
        return f"Game {self.id}: {self.white} vs {self.black}"
    
    def get_lichess_game_result(self):
        """
        Obtiene el resultado de la partida desde Lichess.
        """
        
        if not self.id or not self.white or not self.black:
            print("Game ID or players not set.")
            return None
        
        else:
            lichess_url = f"https://lichess.org/api/game/{self.id}"
            
            try:
                response = requests.get(lichess_url)
                
                if response.status_code != 200:
                    raise LichessAPIError("Error al conectar con Lichess en game")
                
                game_data = response.json()
                
                # Procesamos el resultado del json
                if game_data['id'] != self.id:
                    raise LichessAPIError("ID de partida no coincide con el proporcionado")
                
                speed = game_data['speed']
                self.white = game_data['players']['white']['userId']
                self.black = game_data['players']['black']['userId']
                winner = game_data['winner']
                
                if winner == 'white':
                    self.result = Scores.WHITE
                elif winner == 'black':
                    self.result = Scores.BLACK
                else:
                    self.result = Scores.DRAW
                    
                    
            except requests.exceptions.RequestException as e:
                raise LichessAPIError(f"Error al conectar con Lichess en game: {str(e)}") 
            
        return {
            "result": self.result,
            "white": self.white,
            "black": self.black
        }
        
#Ignoramos swissByes porque vamos por continua
def create_rounds(tournament, swissByes= []):
        
    return