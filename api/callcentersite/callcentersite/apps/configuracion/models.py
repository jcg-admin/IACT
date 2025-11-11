"""Modelos para configuración del sistema."""

from django.conf import settings
from django.db import models


class ConfiguracionSistema(models.Model):
    """
    Parámetros de configuración del sistema.

    Almacena configuraciones clave-valor con metadatos.
    """

    TIPO_CHOICES = [
        ('string', 'Cadena de texto'),
        ('integer', 'Número entero'),
        ('float', 'Número decimal'),
        ('boolean', 'Booleano'),
        ('json', 'JSON'),
    ]

    clave = models.CharField(
        max_length=200,
        unique=True,
        help_text='Clave única de la configuración (ej: max_intentos_login)'
    )

    valor = models.TextField(
        help_text='Valor de la configuración'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='string',
        help_text='Tipo de dato del valor'
    )

    descripcion = models.TextField(
        blank=True,
        help_text='Descripción de qué hace este parámetro'
    )

    valor_default = models.TextField(
        help_text='Valor por defecto si se resetea'
    )

    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configuraciones_modificadas',
        help_text='Usuario que modificó este parámetro'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última modificación'
    )

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        ordering = ['clave']

    def __str__(self):
        return f'{self.clave} = {self.valor}'

    def get_valor_typed(self):
        """Retorna el valor convertido al tipo correcto."""
        if self.tipo == 'integer':
            return int(self.valor)
        elif self.tipo == 'float':
            return float(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'si')
        elif self.tipo == 'json':
            import json
            return json.loads(self.valor)
        return self.valor


class AuditoriaConfiguracion(models.Model):
    """
    Historial de cambios en configuraciones del sistema.

    Permite auditar quién cambió qué y cuándo.
    """

    configuracion = models.ForeignKey(
        ConfiguracionSistema,
        on_delete=models.CASCADE,
        related_name='historial',
        help_text='Configuración que fue modificada'
    )

    valor_anterior = models.TextField(
        help_text='Valor antes del cambio'
    )

    valor_nuevo = models.TextField(
        help_text='Valor después del cambio'
    )

    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditorias_configuracion',
        help_text='Usuario que realizó el cambio'
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='Cuándo se realizó el cambio'
    )

    motivo = models.TextField(
        blank=True,
        help_text='Razón del cambio (opcional)'
    )

    class Meta:
        db_table = 'auditoria_configuracion'
        verbose_name = 'Auditoría de Configuración'
        verbose_name_plural = 'Auditorías de Configuración'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.configuracion.clave} cambió de {self.valor_anterior} a {self.valor_nuevo}'
