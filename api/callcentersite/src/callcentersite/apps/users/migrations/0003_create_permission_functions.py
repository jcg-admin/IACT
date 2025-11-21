"""
Migración para crear funciones SQL del sistema de permisos.

Crea funciones SQL nativas para:
1. usuario_tiene_permiso() - Verificación rápida de permisos
2. obtener_capacidades_usuario() - Lista de capacidades de un usuario
3. obtener_grupos_usuario() - Lista de grupos de un usuario
4. verificar_permiso_y_auditar() - Verifica y audita en una sola operación
5. obtener_menu_usuario() - Genera menú dinámico basado en permisos

Estas funciones se crean solo en motores compatibles (omitidas en SQLite).
"""

from django.db import migrations

FUNCTIONS_SQL = [
    """
    CREATE OR REPLACE FUNCTION usuario_tiene_permiso(
        p_usuario_id INTEGER,
        p_capacidad_codigo VARCHAR(200)
    ) RETURNS BOOLEAN AS $$
    DECLARE
        v_tiene_permiso BOOLEAN;
    BEGIN
        SELECT EXISTS (
            SELECT 1
            FROM vista_capacidades_usuario
            WHERE usuario_id = p_usuario_id
              AND capacidad_codigo = p_capacidad_codigo
        ) INTO v_tiene_permiso;

        RETURN v_tiene_permiso;
    END;
    $$ LANGUAGE plpgsql
    STABLE
    PARALLEL SAFE;

    COMMENT ON FUNCTION usuario_tiene_permiso(INTEGER, VARCHAR) IS
        'Verifica si un usuario tiene una capacidad específica. Usa vista_capacidades_usuario para performance óptimo.';
    """,
    """
    CREATE OR REPLACE FUNCTION obtener_capacidades_usuario(
        p_usuario_id INTEGER
    ) RETURNS TEXT[] AS $$
    DECLARE
        v_capacidades TEXT[];
    BEGIN
        SELECT ARRAY_AGG(DISTINCT capacidad_codigo ORDER BY capacidad_codigo)
        INTO v_capacidades
        FROM vista_capacidades_usuario
        WHERE usuario_id = p_usuario_id;

        RETURN COALESCE(v_capacidades, ARRAY[]::TEXT[]);
    END;
    $$ LANGUAGE plpgsql
    STABLE
    PARALLEL SAFE;

    COMMENT ON FUNCTION obtener_capacidades_usuario(INTEGER) IS
        'Retorna array de códigos de capacidades que tiene un usuario. Retorna array vacío si no tiene permisos.';
    """,
    """
    CREATE OR REPLACE FUNCTION obtener_grupos_usuario(
        p_usuario_id INTEGER
    ) RETURNS JSONB AS $$
    DECLARE
        v_grupos JSONB;
    BEGIN
        SELECT COALESCE(
            JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'grupo_id', grupo_id,
                    'grupo_codigo', grupo_codigo,
                    'grupo_nombre', grupo_nombre,
                    'tipo_acceso', tipo_acceso,
                    'color_hex', color_hex,
                    'vigente', vigente,
                    'fecha_asignacion', fecha_asignacion,
                    'fecha_expiracion', fecha_expiracion
                ) ORDER BY grupo_codigo
            ),
            '[]'::JSONB
        )
        INTO v_grupos
        FROM vista_grupos_usuario
        WHERE usuario_id = p_usuario_id
          AND vigente = TRUE;

        RETURN v_grupos;
    END;
    $$ LANGUAGE plpgsql
    STABLE
    PARALLEL SAFE;

    COMMENT ON FUNCTION obtener_grupos_usuario(INTEGER) IS
        'Retorna JSONB con información completa de grupos vigentes del usuario. Retorna array vacío si no tiene grupos.';
    """,
    """
    CREATE OR REPLACE FUNCTION verificar_permiso_y_auditar(
        p_usuario_id INTEGER,
        p_capacidad_codigo VARCHAR(200),
        p_ip_address VARCHAR(50) DEFAULT NULL,
        p_user_agent TEXT DEFAULT NULL,
        p_recurso_accedido VARCHAR(200) DEFAULT NULL,
        p_endpoint VARCHAR(500) DEFAULT NULL
    ) RETURNS BOOLEAN AS $$
    DECLARE
        v_tiene_permiso BOOLEAN;
        v_accion VARCHAR(100);
    BEGIN
        v_tiene_permiso := usuario_tiene_permiso(p_usuario_id, p_capacidad_codigo);

        IF v_tiene_permiso THEN
            v_accion := 'acceso_permitido';
        ELSE
            v_accion := 'acceso_denegado';
        END IF;

        INSERT INTO auditoria_permisos (
            usuario_id,
            capacidad_codigo,
            accion,
            resultado,
            recurso_accedido,
            endpoint,
            ip_address,
            user_agent,
            timestamp
        ) VALUES (
            p_usuario_id,
            p_capacidad_codigo,
            v_accion,
            'exito',
            p_recurso_accedido,
            p_endpoint,
            p_ip_address,
            p_user_agent,
            NOW()
        );

        RETURN v_tiene_permiso;
    END;
    $$ LANGUAGE plpgsql
    VOLATILE;

    COMMENT ON FUNCTION verificar_permiso_y_auditar IS
        'Verifica permiso y registra en auditoría en una transacción atómica. Optimizado para casos donde siempre se audita.';
    """,
    """
    CREATE OR REPLACE FUNCTION obtener_menu_usuario(
        p_usuario_id INTEGER
    ) RETURNS JSONB AS $$
    DECLARE
        v_capacidades TEXT[];
        v_menu JSONB;
    BEGIN
        v_capacidades := obtener_capacidades_usuario(p_usuario_id);

        SELECT COALESCE(
            JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'dominio', dominio,
                    'funcion', funcion,
                    'tipo_acceso', tipo_acceso,
                    'icono', icono,
                    'orden', orden,
                    'color_hex', color_hex,
                    'ruta', ruta,
                    'capacidades', capacidades
                ) ORDER BY orden
            ),
            '[]'::JSONB
        )
        INTO v_menu
        FROM (
            SELECT
                f.dominio,
                f.nombre AS funcion,
                gp.tipo_acceso,
                gp.icono,
                gp.orden,
                gp.color_hex,
                gp.ruta,
                ARRAY_AGG(DISTINCT c.codigo) AS capacidades
            FROM grupos_permisos gp
            INNER JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
            INNER JOIN capacidades c ON gc.capacidad_id = c.id
            INNER JOIN funcion_capacidades fc ON c.id = fc.capacidad_id
            INNER JOIN funciones f ON fc.funcion_id = f.id
            WHERE gp.activo = TRUE
              AND c.activa = TRUE
              AND gp.id IN (
                  SELECT grupo_id
                  FROM usuarios_grupos
                  WHERE usuario_id = p_usuario_id
                    AND activo = TRUE
                    AND (fecha_expiracion IS NULL OR fecha_expiracion > NOW())
              )
              AND c.codigo = ANY (v_capacidades)
            GROUP BY f.dominio, f.nombre, gp.tipo_acceso, gp.icono, gp.orden, gp.color_hex, gp.ruta
        ) menu_data;

        RETURN v_menu;
    END;
    $$ LANGUAGE plpgsql
    STABLE
    PARALLEL SAFE;

    COMMENT ON FUNCTION obtener_menu_usuario(INTEGER) IS
        'Genera menú dinámico basado en capacidades del usuario usando vistas optimizadas.';
    """,
]

DROP_FUNCTIONS = [
    "DROP FUNCTION IF EXISTS obtener_menu_usuario(INTEGER);",
    "DROP FUNCTION IF EXISTS verificar_permiso_y_auditar;",
    "DROP FUNCTION IF EXISTS obtener_grupos_usuario(INTEGER);",
    "DROP FUNCTION IF EXISTS obtener_capacidades_usuario(INTEGER);",
    "DROP FUNCTION IF EXISTS usuario_tiene_permiso(INTEGER, VARCHAR);",
]


def create_permission_functions(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        return

    for statement in FUNCTIONS_SQL:
        schema_editor.execute(statement)


def drop_permission_functions(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        return

    for statement in DROP_FUNCTIONS:
        schema_editor.execute(statement)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_create_permission_views"),
    ]

    operations = [
        migrations.RunPython(create_permission_functions, reverse_code=drop_permission_functions),
    ]
