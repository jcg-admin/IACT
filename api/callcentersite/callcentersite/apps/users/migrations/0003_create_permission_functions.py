"""
Migración para crear funciones SQL del sistema de permisos.

Crea funciones SQL nativas para:
1. usuario_tiene_permiso() - Verificación rápida de permisos
2. obtener_capacidades_usuario() - Lista de capacidades de un usuario
3. obtener_grupos_usuario() - Lista de grupos de un usuario

Estas funciones SQL nativas son alternativas de alta performance al ORM.

Referencia: docs/backend/requisitos/prioridad_01_estructura_base_datos.md
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_permission_views'),
    ]

    operations = [
        # Función 1: usuario_tiene_permiso
        migrations.RunSQL(
            sql="""
            -- Función para verificar si un usuario tiene una capacidad específica
            -- Retorna TRUE si el usuario tiene el permiso (directamente o via grupos)
            CREATE OR REPLACE FUNCTION usuario_tiene_permiso(
                p_usuario_id INTEGER,
                p_capacidad_codigo VARCHAR(200)
            ) RETURNS BOOLEAN AS $$
            DECLARE
                v_tiene_permiso BOOLEAN;
            BEGIN
                -- Verificar si existe en la vista de capacidades del usuario
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

            -- Comentarios
            COMMENT ON FUNCTION usuario_tiene_permiso(INTEGER, VARCHAR) IS
                'Verifica si un usuario tiene una capacidad específica. Usa vista_capacidades_usuario para performance óptimo.';

            -- Grant a roles necesarios (opcional, ajustar según necesidad)
            -- GRANT EXECUTE ON FUNCTION usuario_tiene_permiso(INTEGER, VARCHAR) TO django_user;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS usuario_tiene_permiso(INTEGER, VARCHAR);",
        ),

        # Función 2: obtener_capacidades_usuario
        migrations.RunSQL(
            sql="""
            -- Función para obtener array de códigos de capacidades de un usuario
            -- Útil para construir menús dinámicos o verificar múltiples permisos
            CREATE OR REPLACE FUNCTION obtener_capacidades_usuario(
                p_usuario_id INTEGER
            ) RETURNS TEXT[] AS $$
            DECLARE
                v_capacidades TEXT[];
            BEGIN
                -- Obtener array de códigos de capacidades
                SELECT ARRAY_AGG(DISTINCT capacidad_codigo ORDER BY capacidad_codigo)
                INTO v_capacidades
                FROM vista_capacidades_usuario
                WHERE usuario_id = p_usuario_id;

                RETURN COALESCE(v_capacidades, ARRAY[]::TEXT[]);
            END;
            $$ LANGUAGE plpgsql
            STABLE
            PARALLEL SAFE;

            -- Comentarios
            COMMENT ON FUNCTION obtener_capacidades_usuario(INTEGER) IS
                'Retorna array de códigos de capacidades que tiene un usuario. Retorna array vacío si no tiene permisos.';
            """,
            reverse_sql="DROP FUNCTION IF EXISTS obtener_capacidades_usuario(INTEGER);",
        ),

        # Función 3: obtener_grupos_usuario
        migrations.RunSQL(
            sql="""
            -- Función para obtener JSON de grupos de un usuario
            -- Retorna información completa de grupos con metadata
            CREATE OR REPLACE FUNCTION obtener_grupos_usuario(
                p_usuario_id INTEGER
            ) RETURNS JSONB AS $$
            DECLARE
                v_grupos JSONB;
            BEGIN
                -- Construir JSON de grupos
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

            -- Comentarios
            COMMENT ON FUNCTION obtener_grupos_usuario(INTEGER) IS
                'Retorna JSONB con información completa de grupos vigentes del usuario. Retorna array vacío si no tiene grupos.';
            """,
            reverse_sql="DROP FUNCTION IF EXISTS obtener_grupos_usuario(INTEGER);",
        ),

        # Función 4: verificar_permiso_y_auditar
        migrations.RunSQL(
            sql="""
            -- Función combinada: verifica permiso Y audita en una sola operación atómica
            -- Optimiza casos donde siempre se audita el acceso
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
                -- Verificar permiso
                v_tiene_permiso := usuario_tiene_permiso(p_usuario_id, p_capacidad_codigo);

                -- Determinar acción
                IF v_tiene_permiso THEN
                    v_accion := 'acceso_permitido';
                ELSE
                    v_accion := 'acceso_denegado';
                END IF;

                -- Insertar auditoría
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
            VOLATILE;  -- VOLATILE porque inserta datos

            -- Comentarios
            COMMENT ON FUNCTION verificar_permiso_y_auditar IS
                'Verifica permiso y registra en auditoría en una transacción atómica. Optimizado para casos donde siempre se audita.';
            """,
            reverse_sql="DROP FUNCTION IF EXISTS verificar_permiso_y_auditar;",
        ),

        # Función 5: obtener_menu_usuario
        migrations.RunSQL(
            sql="""
            -- Función para generar menú dinámico basado en permisos del usuario
            -- Agrupa capacidades por función y dominio
            CREATE OR REPLACE FUNCTION obtener_menu_usuario(
                p_usuario_id INTEGER
            ) RETURNS JSONB AS $$
            DECLARE
                v_menu JSONB;
            BEGIN
                -- Construir menú jerárquico: dominio -> función -> capacidades
                SELECT COALESCE(
                    JSONB_OBJECT_AGG(
                        funcion_dominio,
                        funciones
                    ),
                    '{}'::JSONB
                )
                INTO v_menu
                FROM (
                    SELECT
                        funcion_dominio,
                        JSONB_OBJECT_AGG(
                            funcion_nombre,
                            capacidades
                        ) AS funciones
                    FROM (
                        SELECT
                            funcion_dominio,
                            funcion_nombre,
                            JSONB_AGG(
                                DISTINCT capacidad_codigo ORDER BY capacidad_codigo
                            ) AS capacidades
                        FROM vista_capacidades_usuario
                        WHERE usuario_id = p_usuario_id
                          AND funcion_nombre IS NOT NULL
                        GROUP BY funcion_dominio, funcion_nombre
                    ) AS funciones_por_dominio
                    GROUP BY funcion_dominio
                ) AS menu_por_dominio;

                RETURN v_menu;
            END;
            $$ LANGUAGE plpgsql
            STABLE
            PARALLEL SAFE;

            -- Comentarios
            COMMENT ON FUNCTION obtener_menu_usuario(INTEGER) IS
                'Genera menú dinámico en formato JSONB jerárquico: dominio -> función -> capacidades. Útil para UI.';
            """,
            reverse_sql="DROP FUNCTION IF EXISTS obtener_menu_usuario(INTEGER);",
        ),
    ]
