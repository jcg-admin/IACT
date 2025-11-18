from django.apps import apps
from django.test import SimpleTestCase


class RelatedNamesConflictTest(SimpleTestCase):
    def test_configuration_related_names_are_unique(self):
        configuracion_field = apps.get_model(
            "configuracion", "ConfiguracionSistema"
        )._meta.get_field("modificado_por")
        configuration_field = apps.get_model(
            "configuration", "Configuracion"
        )._meta.get_field("updated_by")

        related_names = {
            configuracion_field.remote_field.related_name,
            configuration_field.remote_field.related_name,
        }

        self.assertEqual(
            {"configuracion_sistema_modificaciones", "configuraciones_actualizadas"},
            related_names,
        )

    def test_permission_related_names_are_unique(self):
        permissions_field = apps.get_model(
            "permissions", "PermisoExcepcional"
        )._meta.get_field("usuario")
        users_field = apps.get_model("users", "PermisoExcepcional")._meta.get_field(
            "usuario"
        )

        related_names = {
            permissions_field.remote_field.related_name,
            users_field.remote_field.related_name,
        }

        self.assertEqual(
            {"permisos_excepcionales_permissions", "permisos_excepcionales_granular"},
            related_names,
        )
