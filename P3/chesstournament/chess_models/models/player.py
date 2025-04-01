from django.db import models
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
        existing_player = Player.objects.filter(
            models.Q(email=self.email, name=self.name) |
            models.Q(lichess_username=self.lichess_username) |
            models.Q(fide_id=self.fide_id)
        ).exclude(id=self.id).first()

        if existing_player:
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
        if self.lichess_username:
            self.update_lichess_ratings()

        # Guardamos el nuevo jugador
        super().save(*args, **kwargs)
        
        
        
    def update_lichess_ratings(self):
        url = f"https://lichess.org/api/user/{self.lichess_username}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            perfs = data.get("perfs", {})
            self.lichess_rating_bullet = perfs.get("bullet", {}).get("rating", 0)
            self.lichess_rating_blitz = perfs.get("blitz", {}).get("rating", 0)
            self.lichess_rating_rapid = perfs.get("rapid", {}).get("rating", 0)
            self.lichess_rating_classical = perfs.get("classical", {}).get("rating", 0)
            
        

    def __str__(self):
        return self.name
