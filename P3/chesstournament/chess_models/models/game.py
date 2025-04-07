from django.db import models
from .player import Player
from .constants import Scores
from .other_models import LichessAPIError
from .round import Round
import requests
from django.utils import timezone

class Game(models.Model):
    white = models.ForeignKey(Player, null=True, on_delete=models.CASCADE, related_name='games_as_white')
    black = models.ForeignKey(Player, null=True, on_delete=models.CASCADE,related_name='games_as_black')
    finished = models.BooleanField(default=False)
    round = models.ForeignKey(Round, on_delete=models.RESTRICT) # Para eliminar importacion circular
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    result = models.CharField(
        max_length=1, 
        choices=Scores.choices, 
        default=Scores.NOAVAILABLE
    )
    rankingOrder = models.IntegerField(default=0, null=True)

    def __str__(self):
        white_name = self.white.lichess_username if self.white else "Bye"
        black_name = self.black.lichess_username if self.black else "Bye"
        result_label = dict(Scores.choices).get(self.result, self.result)
        return f'{white_name}({self.white.id}) vs {black_name}({self.black.id}) = {result_label}'
    
    def get_lichess_game_result(self, lichess_game_id):
        """
        Obtiene el resultado de la partida desde Lichess.
        """
        
        if not lichess_game_id or not self.white or not self.black:
            print("Game ID or players not set.")
            return None
        
        else:
            lichess_url = f"https://lichess.org/api/game/{lichess_game_id}"
            
            try:
                response = requests.get(lichess_url)
                
                if response.status_code != 200:
                    raise LichessAPIError("Error al conectar con Lichess en game")
                
                game_data = response.json()
                
                game_id = game_data['id']
                speed = game_data['speed']
                white_lichess_username = game_data['players']['white']['userId']
                black_lichess_username = game_data['players']['black']['userId']
                winner = game_data['winner']
                
                if winner == 'white':
                    self.result = Scores.WHITE
                elif winner == 'black':
                    self.result = Scores.BLACK
                else:
                    self.result = Scores.DRAW
                    
                    
                if self.white.lichess_username != white_lichess_username or self.black.lichess_username != black_lichess_username:
                    raise LichessAPIError("Los lichess usernames no coinciden con los jugadores de la partida.")
               
            except requests.exceptions.RequestException as e:
                raise LichessAPIError(f"Error al conectar con Lichess en game: {str(e)}") 
            
        return  self.result, white_lichess_username, black_lichess_username
    
"""  
#Ignoramos swissByes porque vamos por continua
def create_rounds(tournament, swissByes= []):
    
    if not tournament:
        print("Error: El torneo no existe.")
        return
    
    num_rounds = tournament.getRoundCount()
    num_players = tournament.getPlayersCount()
    if num_rounds == 0:
        print("No hay jugadores en el torneo.")
        return

    for round_num in range(1, num_rounds + 1):
        
        round_act = Round.objects.create(tournament=tournament)
        
        for num_A in range (1, num_players):
            
            
            num_B = round_num - num_A + 1
            
            #si num_B es menor a 1 o mayor a la cantidad de jugadores significa 
            #que el cálculo ha dado un número inválido. En este caso, usamos la segunda fórmula:
            if num_B < 1 or num_B > num_players:
                num_B = round_num - num_A + num_players
                
            if num_B == num_A:
                num_B = num_players
                
            if num_A < num_B: #Evitamos repetir emparejamintos, ya que si A>B, ya se ha emparejado antes
                
                #Determinamos colores
                if (num_A % 2 == num_B % 2):  # Ambos pares o impares
                    # Menor tiene negras
                    black_player = num_A
                    white_player = num_B
                else:
                    # Menor tiene blancas
                    black_player = num_B
                    white_player = num_A
    
                player_A = tournament.players.all()[white_player - 1] 
                player_B = tournament.players.all()[black_player - 1]
                
                if not player_A or not player_B:
                    print(f"Error: Jugador {num_A} o {num_B} no encontrado.")
                    return
                
                game = Game.objects.create(
                    white=player_A,
                    black=player_B,
                    round=round_act,
                )
"""


def create_rounds(tournament,swissByes= []):
    
    """Here I check if the round is even or odd
       because in even round the biggest number player takes white"""
    
    def emparejamiento_de_ronda(num_ronda, lista):
        """Función para crear los emparejamientos de una ronda"""
        round = Round.objects.create(name=f"Round {num_ronda}", tournament=tournament)
        
        if num_ronda %2 == 1:
            for pos in range(mitad):
                game = Game.objects.create(white=lista[pos], black=lista[num_players -1-pos], round=round)
            
        else:
            game = Game.objects.create(white=lista[num_players -1], black=lista[0], round=round)
            for pos in range(1,mitad):
                game = Game.objects.create(white=lista[pos], black=lista[num_players -1-pos], round=round)
    
    
    if not tournament or len(swissByes) < 0:
        print("Error: El torneo no existe.")
        return
            
    lista = tournament.getPlayers()
    
    if not lista:
        print("No hay jugadores en el torneo.")
        return
    
    num_players = tournament.getPlayersCount()

    if num_players == 0:
        print("No hay jugadores en el torneo.")
        return
    
    mitad = int(num_players/2)
    
    emparejamiento_de_ronda(1, lista)
    
    for num_ronda in range(2,num_players):
        jugador_fijo = lista[num_players-1] # Jugador fijo que no rota. Por convención, el último jugador.
        del lista[num_players-1]
        lista.extend(x for x in lista[0:mitad])
        lista[0:mitad-1]=lista[mitad:num_players-1]
        del lista[mitad-1:num_players-1]
        lista.append(jugador_fijo)
        emparejamiento_de_ronda(num_ronda, lista)
