from django.conf import settings
from django.db import models


class Politica(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicada', 'Publicada'),
        ('archivada', 'Archivada'),
    ]

    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    version = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='politicas_creadas')
    publicado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='politicas_publicadas')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'politicas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} v{self.version}'
