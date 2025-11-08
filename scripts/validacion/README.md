# Scripts de Validacion - Sistema de Permisos Granular

Scripts para validar que el sistema de permisos granular esta correctamente implementado y funcionando.

## Scripts Disponibles

### 1. validar_funciones.sql

Valida que las funciones y capacidades esten correctamente insertadas en la base de datos.

**Uso:**
```bash
psql -d iact_analytics -f scripts/validacion/validar_funciones.sql
```

**Valida:**
- Funciones insertadas (usuarios, dashboards, configuracion)
- Conteo de capacidades por funcion
- Listado detallado de capacidades

**Resultado esperado:**
- usuarios: 7 capacidades
- dashboards: 4 capacidades
- configuracion: 5 capacidades

---

### 2. validar_grupos.sql

Valida que los grupos de permisos tengan las capacidades correctas asignadas.

**Uso:**
```bash
psql -d iact_analytics -f scripts/validacion/validar_grupos.sql
```

**Valida:**
- Grupos creados
- Capacidades asignadas a cada grupo
- No hay duplicados en asignaciones

**Resultado esperado:**
- administracion_usuarios: 7 capacidades
- visualizacion_basica: 4 capacidades
- configuracion_sistema: 5 capacidades

---

### 3. test_permisos.py

Script Python que prueba la funcion `usuario_tiene_permiso` con datos reales.

**Uso:**
```bash
cd api/callcentersite
python manage.py shell < ../../scripts/validacion/test_permisos.py
```

**Casos de prueba:**
1. Usuario con visualizacion_basica PUEDE ver dashboards ✓
2. Usuario con visualizacion_basica NO PUEDE crear usuarios ✓
3. Usuario con admin_usuarios PUEDE crear usuarios ✓
4. Usuario con admin_usuarios NO PUEDE editar configuracion ✓

**Notas:**
- Crea usuarios de prueba temporales
- Los elimina al terminar
- Retorna exit code 0 si todos los tests pasan

---

### 4. validar_auditoria.sql

Valida que el sistema de auditoria este registrando correctamente todas las acciones.

**Uso:**
```bash
psql -d iact_analytics -f scripts/validacion/validar_auditoria.sql
```

**Valida:**
- Registros de auditoria existen
- Acciones de creacion se auditan
- Acciones de suspension se auditan
- Acciones denegadas se auditan

**Reportes generados:**
- Resumen por resultado (permitido/denegado)
- Top 10 acciones mas auditadas
- Top 10 capacidades mas utilizadas
- Ultimos 20 registros

---

## Orden de Ejecucion Recomendado

Para validar una instalacion nueva, ejecutar en este orden:

```bash
# 1. Aplicar migraciones
cd api/callcentersite
python manage.py migrate users
python manage.py migrate configuration
python manage.py migrate dashboard

# 2. Poblar datos
python manage.py seed_permisos_granular
python manage.py seed_configuraciones_default

# 3. Validar funciones y capacidades
psql -d iact_analytics -f ../../scripts/validacion/validar_funciones.sql

# 4. Validar grupos
psql -d iact_analytics -f ../../scripts/validacion/validar_grupos.sql

# 5. Probar permisos
python manage.py shell < ../../scripts/validacion/test_permisos.py

# 6. Validar auditoria (despues de usar el sistema)
psql -d iact_analytics -f ../../scripts/validacion/validar_auditoria.sql
```

---

## Troubleshooting

### Error: "psql: command not found"

Instalar PostgreSQL client:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql
```

### Error: "FATAL: database does not exist"

Crear la base de datos:
```bash
createdb iact_analytics
```

### Error: "django.core.exceptions.ImproperlyConfigured"

Verificar que Django este configurado correctamente:
```bash
cd api/callcentersite
export DJANGO_SETTINGS_MODULE=callcentersite.settings.development
python manage.py check
```

### Error: "relation does not exist"

Aplicar migraciones:
```bash
python manage.py migrate
```

---

## Resultados Esperados

### Si todo esta correcto:

**validar_funciones.sql:**
```
funcion       | capacidades_encontradas | capacidades_esperadas | estado
--------------+------------------------+----------------------+--------
usuarios      | 7                      | 7                    | OK ✓
dashboards    | 4                      | 4                    | OK ✓
configuracion | 5                      | 5                    | OK ✓
```

**validar_grupos.sql:**
```
grupo_codigo           | total_capacidades | estado
-----------------------+------------------+--------
administracion_usuarios| 7                | OK ✓
visualizacion_basica   | 4                | OK ✓
configuracion_sistema  | 5                | OK ✓
```

**test_permisos.py:**
```
✓ TODOS LOS TESTS PASARON

La funcion usuario_tiene_permiso funciona correctamente.
```

**validar_auditoria.sql:**
- Total de registros > 0
- Registros de creacion > 0
- Registros de suspension >= 0
- Registros denegados >= 0

---

## Integracion con CI/CD

Estos scripts pueden integrarse en pipelines de CI/CD:

```yaml
# .github/workflows/validate.yml
- name: Run SQL validations
  run: |
    psql -d iact_analytics -f scripts/validacion/validar_funciones.sql
    psql -d iact_analytics -f scripts/validacion/validar_grupos.sql

- name: Run Python validations
  run: |
    cd api/callcentersite
    python manage.py shell < ../../scripts/validacion/test_permisos.py
```

---

**Ultima actualizacion:** 2025-11-08
**Version:** 1.0.0
