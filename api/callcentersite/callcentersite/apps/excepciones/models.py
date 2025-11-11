from django.conf import settings
from django.db import models


class Excepcion(models.Model):
    ESTADO_CHOICES = [
        ('solicitada', 'Solicitada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    titulo = models.CharField(max_length=200)
    justificacion = models.TextField()
    tipo = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='solicitada')
    
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='excepciones_solicitadas')
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='excepciones_aprobadas')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'excepciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} - {self.estado}'
