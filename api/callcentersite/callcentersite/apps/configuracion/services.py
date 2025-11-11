"""Servicios de negocio para configuración del sistema."""

from __future__ import annotations

import json
from typing import Dict, List

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import AuditoriaConfiguracion, ConfiguracionSistema

User = get_user_model()


class ConfigService:
    """
    Servicio de gestión de configuraciones del sistema.

    Implementa casos de uso para administración de parámetros.
    """

    @staticmethod
    def ver_configuracion(clave: str) -> ConfiguracionSistema:
        """
        UC-024: Ver Configuración específica.

        Args:
            clave: Clave de la configuración

        Returns:
            Configuración solicitada

        Raises:
            ObjectDoesNotExist: Si configuración no existe

        Ejemplo:
            >>> config = ConfigService.ver_configuracion(clave='max_intentos_login')
        """
        return ConfiguracionSistema.objects.get(clave=clave)

    @staticmethod
    def listar_configuraciones() -> List[ConfiguracionSistema]:
        """
        UC-024: Listar todas las configuraciones.

        Returns:
            Lista de todas las configuraciones ordenadas por clave

        Ejemplo:
            >>> configs = ConfigService.listar_configuraciones()
        """
        return list(ConfiguracionSistema.objects.all().order_by('clave'))

    @staticmethod
    def modificar_configuracion(
        clave: str,
        nuevo_valor: str,
        usuario_id: int,
        motivo: str = ''
    ) -> ConfiguracionSistema:
        """
        UC-025: Modificar Configuración.

        Args:
            clave: Clave de la configuración
            nuevo_valor: Nuevo valor a establecer
            usuario_id: ID del usuario que modifica
            motivo: Razón del cambio (opcional)

        Returns:
            Configuración actualizada

        Raises:
            ObjectDoesNotExist: Si configuración no existe
            ValidationError: Si valor no es válido para el tipo

        Ejemplo:
            >>> config = ConfigService.modificar_configuracion(
            ...     clave='timeout_session',
            ...     nuevo_valor='60',
            ...     usuario_id=1,
            ...     motivo='Aumentar tiempo'
            ... )
        """
        usuario = User.objects.get(id=usuario_id)
        config = ConfiguracionSistema.objects.get(clave=clave)

        # Validar tipo de dato
        ConfigService._validar_tipo_valor(config.tipo, nuevo_valor)

        # Guardar valor anterior para auditoría
        valor_anterior = config.valor

        # Actualizar configuración
        config.valor = nuevo_valor
        config.modificado_por = usuario
        config.save()

        # Crear registro de auditoría
        AuditoriaConfiguracion.objects.create(
            configuracion=config,
            valor_anterior=valor_anterior,
            valor_nuevo=nuevo_valor,
            modificado_por=usuario,
            motivo=motivo
        )

        return config

    @staticmethod
    def _validar_tipo_valor(tipo: str, valor: str) -> None:
        """Valida que el valor sea compatible con el tipo esperado."""
        try:
            if tipo == 'integer':
                int(valor)
            elif tipo == 'float':
                float(valor)
            elif tipo == 'boolean':
                if valor.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'si'):
                    raise ValueError
            elif tipo == 'json':
                json.loads(valor)
        except (ValueError, json.JSONDecodeError):
            raise ValidationError(f'Valor "{valor}" no es válido para tipo {tipo}')

    @staticmethod
    def exportar_configuracion() -> str:
        """
        UC-026: Exportar Configuración.

        Exporta todas las configuraciones a formato JSON.

        Returns:
            String JSON con todas las configuraciones

        Ejemplo:
            >>> json_data = ConfigService.exportar_configuracion()
        """
        configs = ConfiguracionSistema.objects.all()

        data = [
            {
                'clave': c.clave,
                'valor': c.valor,
                'tipo': c.tipo,
                'descripcion': c.descripcion,
                'valor_default': c.valor_default
            }
            for c in configs
        ]

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def importar_configuracion(
        json_data: str,
        usuario_id: int
    ) -> Dict[str, int]:
        """
        UC-027: Importar Configuración.

        Importa configuraciones desde JSON, creando o actualizando según corresponda.

        Args:
            json_data: String JSON con configuraciones
            usuario_id: ID del usuario que importa

        Returns:
            Dict con contadores de creadas/actualizadas

        Raises:
            ValidationError: Si JSON es inválido
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> resultado = ConfigService.importar_configuracion(
            ...     json_data='[{"clave": "param1", ...}]',
            ...     usuario_id=1
            ... )
            >>> print(resultado)  # {'creadas': 5, 'actualizadas': 3}
        """
        usuario = User.objects.get(id=usuario_id)

        try:
            configs_data = json.loads(json_data)
        except json.JSONDecodeError:
            raise ValidationError('JSON inválido')

        if not isinstance(configs_data, list):
            raise ValidationError('JSON debe ser una lista de configuraciones')

        creadas = 0
        actualizadas = 0

        for config_data in configs_data:
            clave = config_data.get('clave')
            if not clave:
                continue

            # Validar tipo de valor antes de guardar
            tipo = config_data.get('tipo', 'string')
            valor = config_data.get('valor', '')
            ConfigService._validar_tipo_valor(tipo, valor)

            # Verificar si existe
            existing = ConfiguracionSistema.objects.filter(clave=clave).first()

            if existing:
                # Actualizar existente
                valor_anterior = existing.valor
                existing.valor = valor
                existing.tipo = tipo
                existing.descripcion = config_data.get('descripcion', '')
                existing.valor_default = config_data.get('valor_default', valor)
                existing.modificado_por = usuario
                existing.save()

                # Auditar
                AuditoriaConfiguracion.objects.create(
                    configuracion=existing,
                    valor_anterior=valor_anterior,
                    valor_nuevo=valor,
                    modificado_por=usuario,
                    motivo='Importación de configuración'
                )
                actualizadas += 1
            else:
                # Crear nueva
                ConfiguracionSistema.objects.create(
                    clave=clave,
                    valor=valor,
                    tipo=tipo,
                    descripcion=config_data.get('descripcion', ''),
                    valor_default=config_data.get('valor_default', valor),
                    modificado_por=usuario
                )
                creadas += 1

        return {
            'creadas': creadas,
            'actualizadas': actualizadas
        }

    @staticmethod
    def ver_historial_configuracion(clave: str) -> List[AuditoriaConfiguracion]:
        """
        UC-028: Ver historial de una configuración específica.

        Args:
            clave: Clave de la configuración

        Returns:
            Lista de auditorías ordenadas por timestamp descendente

        Raises:
            ObjectDoesNotExist: Si configuración no existe

        Ejemplo:
            >>> historial = ConfigService.ver_historial_configuracion(clave='timeout')
        """
        config = ConfiguracionSistema.objects.get(clave=clave)
        return list(
            AuditoriaConfiguracion.objects.filter(configuracion=config)
            .order_by('-timestamp')
        )

    @staticmethod
    def ver_historial_completo() -> List[AuditoriaConfiguracion]:
        """
        UC-028: Ver historial completo de todas las configuraciones.

        Returns:
            Lista de todas las auditorías ordenadas por timestamp descendente

        Ejemplo:
            >>> historial = ConfigService.ver_historial_completo()
        """
        return list(AuditoriaConfiguracion.objects.all().order_by('-timestamp'))
