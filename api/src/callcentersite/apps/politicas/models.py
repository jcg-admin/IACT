"""Modelos para políticas."""

from django.conf import settings
from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class Politica(TimeStampedModel):
    """Modelo de política con versionamiento."""

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicada', 'Publicada'),
        ('archivada', 'Archivada'),
    ]

    titulo = models.CharField(max_length=200, help_text='Título de la política')
    contenido = models.TextField(help_text='Contenido completo de la política')
    version = models.IntegerField(default=1, help_text='Número de versión')
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='borrador',
        help_text='Estado actual de la política'
    )
    
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='politicas_creadas',
        help_text='Usuario que creó esta versión'
    )
    publicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='politicas_publicadas',
        help_text='Usuario que publicó la política'
    )

    class Meta:
        db_table = 'politicas'
        ordering = ['-created_at']
        verbose_name = 'Política'
        verbose_name_plural = 'Políticas'

    def __str__(self):
        return f'{self.titulo} v{self.version}'
