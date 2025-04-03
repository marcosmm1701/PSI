from django.db import models
from .other_models import LichessAPIError
import requests
from django.utils import timezone

class Player(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    
    lichess_username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    lichess_rating_bullet = models.IntegerField(default=0, null=True) # Rating del jugador en la modalidad Bullet en Lichess
    lichess_rating_blitz = models.IntegerField(default=0, null=True) # Rating del jugador en la modalidad Blitz en Lichess.
    lichess_rating_rapid = models.IntegerField(default=0, null=True) # Rating del jugador en la modalidad Rapid en Lichess.
    lichess_rating_classical = models.IntegerField(default=0, null=True)
    
    fide_id = models.IntegerField(unique=True, null=True, blank=True)
    fide_rating_blitz = models.IntegerField(default=0, null=True)
    fide_rating_rapid = models.IntegerField(default=0, null=True)
    fide_rating_classical = models.IntegerField(default=0, null=True)
    
    
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'email')  # La pareja (name, email) debe ser única

    
    def save(self, *args, **kwargs):
        """Sobrescribe save() para actualizar jugadores en lugar de duplicarlos."""
        if not self.id and not self.creation_date:
            self.creation_date = timezone.now()
        
        #Hemos separado las condiciones de jugador existente para evitar errores en los tests de tournament y game
        if self.lichess_username and self.lichess_username != "":
            existing_player = Player.objects.filter(models.Q(lichess_username=self.lichess_username)).exclude(id=self.id).first()
        
        if self.fide_id and self.fide_id != "" and not existing_player:
            existing_player = Player.objects.filter(models.Q(fide_id=self.fide_id)).exclude(id=self.id).first()
        
        if (self.email and self.email != "") and (self.name and self.name != "") and not existing_player:
            existing_player = Player.objects.filter(models.Q(email=self.email, name=self.name)).exclude(id=self.id).first()
            
        # Si encontramos un jugador existente, actualizamos sus datos
        if existing_player:
            self.id = existing_player.id  # Asignamos el ID del jugador existente
            # Copiamos los valores de los campos del modelo
            for field in self._meta.fields:
                field_name = field.name
                if field_name not in ["id", "creation_date", "update_date"]:
                    setattr(existing_player, field_name, getattr(self, field_name))

            # Actualizamos la fecha de modificación
            existing_player.update_date = timezone.now()
            existing_player.save()
            return

        # Si el jugador tiene un lichess_username, actualizar sus ratings desde Lichess
        if self.check_lichess_user_exists():
            self.get_lichess_user_ratings()

        # Guardamos el nuevo jugador
        super().save(*args, **kwargs)
        
        
        
    def get_lichess_user_ratings(self):
        """Obtiene las clasificaciones del usuario en Lichess y actualiza los valores en la base de datos."""
        if self.check_lichess_user_exists() == False:
            raise LichessAPIError("Nombre de usuario Lichess no proporcionado")
        
        url = f"https://lichess.org/api/user/{self.lichess_username}"
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                perfs = data.get("perfs", {})
                
                self.lichess_rating_bullet = perfs.get("bullet", {}).get("rating", 0)
                self.lichess_rating_blitz = perfs.get("blitz", {}).get("rating", 0)
                self.lichess_rating_rapid = perfs.get("rapid", {}).get("rating", 0)
                self.lichess_rating_classical = perfs.get("classical", {}).get("rating", 0)

                #self.save()
        except requests.exceptions.RequestException as e:
            raise LichessAPIError(f"Error al conectar con Lichess: {str(e)}")
    
    
    def check_lichess_user_exists(self):
        
        if not self.lichess_username:
            return False
        
        url = f"https://lichess.org/api/user/{self.lichess_username}"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        
        except requests.exceptions.RequestException as e:
            print(f"Error al verificar el usuario de Lichess: {str(e)}")
            return False
        

    def __str__(self):
        return self.lichess_username  or self.name or str(self.id)