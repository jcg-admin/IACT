"""
Migración para crear vistas SQL de optimización del sistema de permisos.

Crea 2 vistas SQL:
1. vista_capacidades_usuario - Todas las capacidades efectivas de cada usuario
2. vista_grupos_usuario - Grupos asignados a usuarios con vigencia

Estas vistas optimizan consultas frecuentes del sistema de permisos.

Referencia: docs/backend/requisitos/prioridad_01_estructura_base_datos.md
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial_permisos_granular'),
    ]

    operations = [
        # Vista 1: Capacidades por usuario
        migrations.RunSQL(
            sql="""
            -- Vista que consolida todas las capacidades efectivas de cada usuario
            -- Incluye capacidades de grupos Y permisos excepcionales
            CREATE OR REPLACE VIEW vista_capacidades_usuario AS

            -- CAPACIDADES DE GRUPOS
            SELECT DISTINCT
                u.id AS usuario_id,
                u.username AS usuario_nombre,
                u.email AS usuario_email,
                c.id AS capacidad_id,
                c.codigo AS capacidad_codigo,
                f.nombre AS funcion_nombre,
                f.dominio AS funcion_dominio,
                c.nivel_riesgo,
                'grupo' AS origen,
                gp.codigo AS grupo_origen
            FROM auth_user u
            INNER JOIN usuarios_grupos ug ON u.id = ug.usuario_id
            INNER JOIN grupos_permisos gp ON ug.grupo_id = gp.id
            INNER JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
            INNER JOIN capacidades c ON gc.capacidad_id = c.id
            LEFT JOIN funcion_capacidades fc ON c.id = fc.capacidad_id
            LEFT JOIN funciones f ON fc.funcion_id = f.id
            WHERE ug.activo = TRUE
              AND gp.activo = TRUE
              AND c.activa = TRUE
              AND (ug.fecha_expiracion IS NULL OR ug.fecha_expiracion > NOW())

            UNION

            -- PERMISOS EXCEPCIONALES CONCEDIDOS
            SELECT DISTINCT
                u.id AS usuario_id,
                u.username AS usuario_nombre,
                u.email AS usuario_email,
                c.id AS capacidad_id,
                c.codigo AS capacidad_codigo,
                f.nombre AS funcion_nombre,
                f.dominio AS funcion_dominio,
                c.nivel_riesgo,
                'excepcional_concedido' AS origen,
                NULL AS grupo_origen
            FROM auth_user u
            INNER JOIN permisos_excepcionales pe ON u.id = pe.usuario_id
            INNER JOIN capacidades c ON pe.capacidad_id = c.id
            LEFT JOIN funcion_capacidades fc ON c.id = fc.capacidad_id
            LEFT JOIN funciones f ON fc.funcion_id = f.id
            WHERE pe.tipo = 'conceder'
              AND pe.activo = TRUE
              AND c.activa = TRUE
              AND pe.fecha_inicio <= NOW()
              AND (pe.fecha_expiracion IS NULL OR pe.fecha_expiracion > NOW())

            EXCEPT

            -- MENOS PERMISOS EXCEPCIONALES REVOCADOS
            SELECT DISTINCT
                u.id AS usuario_id,
                u.username AS usuario_nombre,
                u.email AS usuario_email,
                c.id AS capacidad_id,
                c.codigo AS capacidad_codigo,
                f.nombre AS funcion_nombre,
                f.dominio AS funcion_dominio,
                c.nivel_riesgo,
                'excepcional_revocado' AS origen,
                NULL AS grupo_origen
            FROM auth_user u
            INNER JOIN permisos_excepcionales pe ON u.id = pe.usuario_id
            INNER JOIN capacidades c ON pe.capacidad_id = c.id
            LEFT JOIN funcion_capacidades fc ON c.id = fc.capacidad_id
            LEFT JOIN funciones f ON fc.funcion_id = f.id
            WHERE pe.tipo = 'revocar'
              AND pe.activo = TRUE
              AND c.activa = TRUE
              AND pe.fecha_inicio <= NOW()
              AND (pe.fecha_expiracion IS NULL OR pe.fecha_expiracion > NOW());

            -- Comentarios
            COMMENT ON VIEW vista_capacidades_usuario IS
                'Vista consolidada de capacidades efectivas por usuario. Incluye capacidades de grupos Y permisos excepcionales (concedidos - revocados).';
            """,
            reverse_sql="DROP VIEW IF EXISTS vista_capacidades_usuario;",
        ),

        # Vista 2: Grupos por usuario
        migrations.RunSQL(
            sql="""
            -- Vista de grupos asignados a usuarios con estado de vigencia
            CREATE OR REPLACE VIEW vista_grupos_usuario AS
            SELECT
                u.id AS usuario_id,
                u.username AS usuario_nombre,
                u.email AS usuario_email,
                gp.id AS grupo_id,
                gp.codigo AS grupo_codigo,
                gp.nombre_display AS grupo_nombre,
                gp.tipo_acceso,
                gp.color_hex,
                ug.fecha_asignacion,
                ug.fecha_expiracion,
                ug.motivo,
                ug.activo,
                CASE
                    WHEN ug.activo = FALSE THEN FALSE
                    WHEN ug.fecha_expiracion IS NULL THEN TRUE
                    WHEN ug.fecha_expiracion > NOW() THEN TRUE
                    ELSE FALSE
                END AS vigente,
                asignado.username AS asignado_por_nombre
            FROM auth_user u
            INNER JOIN usuarios_grupos ug ON u.id = ug.usuario_id
            INNER JOIN grupos_permisos gp ON ug.grupo_id = gp.id
            LEFT JOIN auth_user asignado ON ug.asignado_por_id = asignado.id
            WHERE ug.activo = TRUE;

            -- Comentarios
            COMMENT ON VIEW vista_grupos_usuario IS
                'Vista de grupos asignados a usuarios con cálculo de vigencia basado en fecha_expiracion y campo activo.';
            """,
            reverse_sql="DROP VIEW IF EXISTS vista_grupos_usuario;",
        ),

        # Índices en tablas base para optimizar vistas
        migrations.RunSQL(
            sql="""
            -- Índice compuesto para query frecuente de capacidades
            CREATE INDEX IF NOT EXISTS idx_usuarios_grupos_vigencia
                ON usuarios_grupos(usuario_id, activo, fecha_expiracion);

            -- Índice para permisos excepcionales vigentes
            CREATE INDEX IF NOT EXISTS idx_permisos_exc_vigencia
                ON permisos_excepcionales(usuario_id, activo, tipo, fecha_inicio, fecha_expiracion);

            -- Índice para búsquedas por capacidad_codigo
            CREATE INDEX IF NOT EXISTS idx_capacidades_codigo_activa
                ON capacidades(codigo, activa);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS idx_usuarios_grupos_vigencia;
            DROP INDEX IF EXISTS idx_permisos_exc_vigencia;
            DROP INDEX IF EXISTS idx_capacidades_codigo_activa;
            """,
        ),
    ]
