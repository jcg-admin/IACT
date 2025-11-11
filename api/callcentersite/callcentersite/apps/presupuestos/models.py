"""Modelos para presupuestos."""

from django.conf import settings
from django.db import models

from callcentersite.apps.common.models import TimeStampedModel


class Presupuesto(TimeStampedModel):
    """Modelo de presupuesto con workflow de aprobación."""

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente Aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=200, help_text='Título del presupuesto')
    descripcion = models.TextField(help_text='Descripción detallada')
    monto = models.DecimalField(max_digits=12, decimal_places=2, help_text='Monto total')
    periodo_inicio = models.DateField(help_text='Fecha de inicio del período')
    periodo_fin = models.DateField(help_text='Fecha de fin del período')
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='borrador',
        help_text='Estado actual del presupuesto'
    )
    
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='presupuestos_creados',
        help_text='Usuario que creó el presupuesto'
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='presupuestos_aprobados',
        help_text='Usuario que aprobó/rechazó el presupuesto'
    )

    class Meta:
        db_table = 'presupuestos'
        ordering = ['-created_at']
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'

    def __str__(self):
        return f'{self.titulo} - ${self.monto}'
