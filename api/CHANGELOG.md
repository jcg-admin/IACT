### FEATURE: Configuración de Enrutamiento Principal y Documentación de Desarrollo

**Archivo Modificado:** `callcentersite/urls.py`

Esta actualización mejora la navegación del proyecto al implementar una redirección desde la URL raíz y añade comentarios para clarificar la configuración condicional de las herramientas de desarrollo.

#### Añadido

-   **Redirección de URL Raíz a Documentación:** Se añadió el *path* raíz (`/`) para redirigir automáticamente a la documentación de Swagger UI (`/api/docs/`).
    -   Para esto, fue necesario importar `RedirectView` de `django.views.generic.base`.
    -   Esta corrección elimina el error 404 de Django al acceder a la URL base del servicio.

#### Cambiado

-   **Documentación del Debug Toolbar:** Se agregó un bloque de comentarios detallado en la sección de URLs del Django Debug Toolbar (`path("__debug__/", ...)`).
    -   El objetivo es clarificar que este código opera solo en modo desarrollo (`if settings.DEBUG:`) y que no necesita ser removido manualmente en ambientes de producción.

#### Confirmación de Estructura

-   **Rutas de Importación de Python:** Se validó que todas las inclusiones de URLs de las aplicaciones (ej: `callcentersite.apps.users.urls`) utilizan la ruta de importación de Python correcta y **omiten el prefijo de carpeta `src`**, adhiriéndose a las mejores prácticas de estructuración de módulos.