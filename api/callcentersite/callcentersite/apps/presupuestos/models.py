"""Modelos para presupuestos."""

from django.conf import settings
from django.db import models


class Presupuesto(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente Aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='presupuestos_creados')
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='presupuestos_aprobados')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'presupuestos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} - {self.monto}'
