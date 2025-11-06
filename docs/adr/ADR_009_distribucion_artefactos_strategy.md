# ADR_009: Estrategia de Distribución de Artefactos CPython Precompilados

**Estado:** Propuesto
**Fecha:** 2025-11-06
**Decisor:** Equipo Infraestructura
**Relacionado:** SPEC_INFRA_001, ADR_008
**Actualizado:** 2025-11-06

---

## Contexto

Los artefactos de CPython precompilado pesan aproximadamente 50-80 MB cada uno. Necesitamos una estrategia de distribución que cumpla:

1. **Versionado**: Rastrear qué versión usa cada proyecto
2. **Integridad**: Garantizar que los binarios no están alterados
3. **Disponibilidad**: Acceso confiable para todos los desarrolladores
4. **Costo**: Minimizar costos de almacenamiento y ancho de banda
5. **Simplicidad**: Fácil de usar y mantener
6. **Local-first**: Alineado con filosofía IACT cuando sea posible

### Problema

Guardar binarios de 50-80 MB en Git directamente inflaría el repositorio rápidamente:
- 1 versión de Python = 80 MB
- 5 versiones mantenidas = 400 MB
- 10 builds/updates = 4 GB en historial de Git

Esto haría que clones del repositorio sean extremadamente lentos y consumidores de disco.

### Opciones Evaluadas

1. **GitHub Releases** (opción seleccionada)
2. Git LFS (Large File Storage)
3. Storage externo (S3, Google Cloud Storage)
4. Servidor HTTP interno
5. Commit directo en Git (baseline, descartado inmediatamente)

---

## Decisión

**Usaremos GitHub Releases** para almacenar y distribuir artefactos de CPython precompilado.

### Implementación

**Publicación de artefactos:**

```bash
# Después de compilar en Vagrant
cd infrastructure/cpython/artifacts/
gh release create cpython-3.12.6-build1 \
  cpython-3.12.6-ubuntu22.04-build1.tgz \
  cpython-3.12.6-ubuntu22.04-build1.tgz.sha256 \
  --title "CPython 3.12.6 Build 1" \
  --notes "CPython 3.12.6 precompilado para Ubuntu 22.04 con OpenSSL 3.0, SQLite 3.37"
```

**Consumo en Feature:**

```bash
# install.sh en Feature de Dev Container
ARTIFACT_URL="https://github.com/2-Coatl/IACT---project/releases/download/cpython-3.12.6-build1/cpython-3.12.6-ubuntu22.04-build1.tgz"

wget -q "$ARTIFACT_URL" -O /tmp/cpython.tgz
wget -q "$ARTIFACT_URL.sha256" -O /tmp/cpython.tgz.sha256

# Validar integridad
cd /tmp && sha256sum -c cpython.tgz.sha256
```

**Registro de artefactos:**

Mantener `artifacts/ARTIFACTS.md` en Git (archivo pequeño de texto):

```markdown
| Versión | Build | Distro | Fecha | SHA256 | Release URL | Estado |
|---------|-------|--------|-------|--------|-------------|--------|
| 3.12.6  | 1     | ubuntu22.04 | 2025-11-06 | abc123... | https://github.com/.../releases/download/cpython-3.12.6-build1 | Activo |
```

---

## Justificación

### Por qué GitHub Releases (Opción 1)

**Ventajas:**

1. **Gratis**: GitHub Free incluye releases ilimitados (límite 2 GB por archivo, suficiente)

2. **Versionado nativo**: Releases están asociados a tags de Git, trazabilidad perfecta

3. **No infla repositorio**: Los binarios NO están en historial de Git

4. **Descarga HTTPS pública**: Cualquiera con acceso al repo puede descargar (no requiere auth especial)

5. **CDN de GitHub**: Descarga rápida desde infraestructura global de GitHub

6. **No requiere Git LFS**: Desarrolladores no necesitan instalar/configurar Git LFS

7. **Fácil de usar**: Un comando `gh release create` publica todo

8. **Auditable**: Cada release tiene fecha, autor, notas, y archivos inmutables

9. **Compatible con CI/CD**: GitHub Actions puede publicar releases automáticamente

10. **Rollback simple**: Versiones anteriores permanecen disponibles indefinidamente

**Desventajas (aceptadas):**

- Requiere internet para descargar (primera vez, luego caché local)
- Requiere `gh` CLI para publicar (instalación simple)
- Si GitHub está caído, no se puede descargar (mitigado con fallback manual)

**Evaluación de límites:**

- Límite por archivo: 2 GB (artefactos son ~80 MB, 25x margen)
- Límite total de releases: Ilimitado para repos públicos/privados en plan Free
- Ancho de banda: Ilimitado para descargas públicas

### Por qué NO Git LFS (Opción 2)

**Ventajas consideradas:**
- Versionado con código (archivos en commits normales)
- Transparente para usuarios (con Git LFS instalado)

**Desventajas (críticas):**

1. **Cuota limitada**: 1 GB almacenamiento + 1 GB ancho de banda/mes gratis
   - Sobrepasar cuota requiere pagar: $5/mes por 50 GB
   - Con 80 MB por artefacto: solo 12 descargas agotan cuota mensual

2. **Requiere instalación**: Todos los desarrolladores deben instalar Git LFS
   - Barrera de entrada adicional
   - Fallas silenciosas si no está instalado (archivos pointer en lugar de binarios)

3. **Complejidad de setup**: Requiere configurar `.gitattributes`, track patterns

4. **Costo escalable**: Cada desarrollador descargando gasta cuota

5. **No funciona bien en CI/CD**: GitHub Actions cuenta contra cuota de ancho de banda

**Cálculo de costos con Git LFS:**
- 10 desarrolladores x 5 proyectos x 80 MB = 4 GB/mes de ancho de banda
- Costo: $5/mes (límite excedido inmediatamente)

**Razón de descarte**: Costo y complejidad innecesarios vs GitHub Releases gratis.

### Por qué NO Storage Externo - S3/GCS (Opción 3)

**Ventajas consideradas:**
- Escalable infinitamente
- Control total de ACLs

**Desventajas (críticas):**

1. **Costo**: S3 cobra por almacenamiento + transferencia
   - ~$0.023/GB/mes almacenamiento (región us-east-1)
   - ~$0.09/GB transferencia de salida
   - 5 artefactos x 80 MB = 400 MB = $0.01/mes (trivial)
   - Pero transferencia: 100 descargas x 80 MB = 8 GB = $0.72/mes

2. **Dependencia externa**: Requiere cuenta AWS/GCP, configuración

3. **Complejidad operacional**: Gestión de buckets, IAM, lifecycle policies

4. **Requiere autenticación**: Descargas necesitan credentials o pre-signed URLs

5. **No local-first**: Contradice filosofía IACT

**Razón de descarte**: Complejidad y costo innecesarios para equipo pequeño.

### Por qué NO Servidor HTTP Interno (Opción 4)

**Ventajas consideradas:**
- Control total
- 100% local si se desea

**Desventajas (críticas):**

1. **Requiere infraestructura**: Servidor HTTP dedicado, dominio, SSL

2. **Mantenimiento**: Alguien debe mantener el servidor, backups, updates

3. **Single point of failure**: Si el servidor cae, nadie puede construir Dev Containers

4. **Sin versionado nativo**: Hay que implementar manualmente

5. **Sin CDN**: Descargas lentas si servidor está lejos geográficamente

**Razón de descarte**: Overhead operacional alto para beneficio marginal.

---

## Consecuencias

### Positivas

1. **Costo cero**: Completamente gratis en GitHub Free
2. **Setup simple**: Un comando publica, otro descarga
3. **Versionado perfecto**: Tags de Git + Releases
4. **No infla repositorio**: Clones rápidos
5. **Caché de Docker**: Builds subsecuentes no re-descargan
6. **Auditabilidad**: Historial completo de releases

### Negativas (Mitigadas)

1. **Requiere internet para primera descarga**
   - Mitigación: Documentar procedimiento de descarga manual previa
   - Alternativa: Copiar artefacto localmente y usar `file://` URL

2. **Dependencia de GitHub**
   - Mitigación: GitHub tiene SLA 99.9%, mejor que servidor propio
   - Plan B: Mantener mirror local opcional (documentado)

3. **Requiere `gh` CLI para publicar**
   - Mitigación: Instalación simple (`brew install gh` o `apt install gh`)
   - Alternativa: Publicar via web UI de GitHub

### Neutrales

- Los artefactos son públicos si el repo es público (aceptable, CPython es open source)
- Historial de releases crece con cada versión (esperado, no es problema)

---

## Implementación Técnica

### Publicación (Manual)

```bash
# En Vagrant después de compilar exitosamente
cd /vagrant/infrastructure/cpython/artifacts/

# Crear release con gh CLI
gh release create cpython-3.12.6-build1 \
  cpython-3.12.6-ubuntu22.04-build1.tgz \
  cpython-3.12.6-ubuntu22.04-build1.tgz.sha256 \
  --title "CPython 3.12.6 Build 1 (Ubuntu 22.04)" \
  --notes "$(cat <<'EOF'
## CPython 3.12.6 Precompilado - Build 1

**Plataforma**: Ubuntu 22.04 LTS
**Fecha de compilación**: 2025-11-06
**Flags de optimización**: --enable-optimizations, --with-lto

### Librerías nativas incluidas:
- OpenSSL 3.0.2
- SQLite 3.37.2
- libuuid 2.37.2
- liblzma 5.2.5
- libbz2 1.0.8

### Instalación:
Ver [documentación](https://github.com/2-Coatl/IACT---project/blob/main/docs/infraestructura/cpython_precompilado/README.md)

### Validación:
SHA256: $(cat cpython-3.12.6-ubuntu22.04-build1.tgz.sha256)
EOF
)"

# Actualizar registro
echo "| 3.12.6 | 1 | ubuntu22.04 | $(date +%Y-%m-%d) | $(cat cpython-3.12.6-ubuntu22.04-build1.tgz.sha256 | cut -d' ' -f1) | https://github.com/2-Coatl/IACT---project/releases/download/cpython-3.12.6-build1 | Activo |" >> ../ARTIFACTS.md
```

### Publicación (Automatizada - Fase 4)

```yaml
# .github/workflows/publish-cpython.yml
name: Publish CPython Artifact

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Versión de CPython (ej: 3.12.6)'
        required: true
      build_number:
        description: 'Número de build (ej: 1)'
        required: true

jobs:
  publish:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Download artifact from Vagrant
        run: |
          # Asumir que artefacto ya está en infrastructure/cpython/artifacts/
          ls -lh infrastructure/cpython/artifacts/

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: cpython-${{ inputs.version }}-build${{ inputs.build_number }}
          files: |
            infrastructure/cpython/artifacts/cpython-${{ inputs.version }}-ubuntu22.04-build${{ inputs.build_number }}.tgz
            infrastructure/cpython/artifacts/cpython-${{ inputs.version }}-ubuntu22.04-build${{ inputs.build_number }}.tgz.sha256
```

### Consumo en Feature

```bash
# .devcontainer/infrastructure/cpython/installer/install.sh

VERSION="${VERSION:-3.12.6}"
BUILD_NUMBER="${BUILD_NUMBER:-1}"
DISTRO="ubuntu22.04"

ARTIFACT_NAME="cpython-${VERSION}-${DISTRO}-build${BUILD_NUMBER}.tgz"
BASE_URL="https://github.com/2-Coatl/IACT---project/releases/download/cpython-${VERSION}-build${BUILD_NUMBER}"

# Descargar artefacto
wget -q "${BASE_URL}/${ARTIFACT_NAME}" -O /tmp/cpython.tgz
wget -q "${BASE_URL}/${ARTIFACT_NAME}.sha256" -O /tmp/cpython.tgz.sha256

# Validar checksum
cd /tmp
if ! sha256sum -c cpython.tgz.sha256; then
    echo "ERROR: Checksum SHA256 inválido. Artefacto corrupto o alterado."
    exit 1
fi

# Extraer e instalar
cd /
tar xzf /tmp/cpython.tgz

# Configurar
ln -sf "/opt/python-${VERSION}/bin/python3" /usr/local/bin/python3
ln -sf "/opt/python-${VERSION}/bin/pip3" /usr/local/bin/pip3
echo "/opt/python-${VERSION}/lib" > /etc/ld.so.conf.d/python.conf
ldconfig
```

---

## Plan de Contingencia

### Escenario 1: GitHub está caído

**Fallback manual:**

1. Descargar artefacto manualmente antes de tiempo:
   ```bash
   mkdir -p infrastructure/cpython/artifacts/
   curl -L https://github.com/.../releases/download/.../cpython-3.12.6-ubuntu22.04-build1.tgz \
     -o infrastructure/cpython/artifacts/cpython-3.12.6-ubuntu22.04-build1.tgz
   ```

2. Modificar Feature para usar path local:
   ```json
   {
     "features": {
       "./infrastructure/cpython/installer": {
         "version": "3.12.6",
         "artifactUrl": "${localWorkspaceFolder}/infrastructure/cpython/artifacts/cpython-3.12.6-ubuntu22.04-build1.tgz"
       }
     }
   }
   ```

### Escenario 2: Límite de rate de GitHub

Si GitHub aplica rate limiting (muy improbable para releases), usar caché local:

```bash
# Feature detecta caché
CACHE_DIR="${HOME}/.cache/iact-cpython"
if [ -f "${CACHE_DIR}/${ARTIFACT_NAME}" ]; then
    cp "${CACHE_DIR}/${ARTIFACT_NAME}" /tmp/cpython.tgz
else
    wget ...
    mkdir -p "${CACHE_DIR}"
    cp /tmp/cpython.tgz "${CACHE_DIR}/${ARTIFACT_NAME}"
fi
```

### Escenario 3: Repositorio se vuelve privado

GitHub Releases de repos privados requieren autenticación:

```bash
# Usar GITHUB_TOKEN en Feature
wget --header="Authorization: token ${GITHUB_TOKEN}" ...
```

Pero para IACT (repo público actual), no es necesario.

---

## Evolución Futura

### Mejoras potenciales (Fase 4+):

1. **Firma GPG de artefactos**:
   ```bash
   gpg --armor --detach-sign cpython-3.12.6-ubuntu22.04-build1.tgz
   gh release upload ... cpython-3.12.6-ubuntu22.04-build1.tgz.asc
   ```

2. **Checksums múltiples** (SHA256 + SHA512):
   Redundancia para mayor seguridad

3. **Mirror en servidor interno** (opcional):
   Para equipos enterprise con restricciones de acceso externo

4. **Webhook de notificación**:
   Notificar equipo cuando nuevo artefacto se publica

---

## Métricas de Éxito

Indicadores para validar decisión:

- Costo de almacenamiento: $0/mes (objetivo cumplido)
- Tiempo de descarga: <30 segundos (medible en logs)
- Disponibilidad: 99.9% (SLA de GitHub)
- Satisfacción de desarrolladores: Encuesta post-adopción

---

## Revisión Programada

**Fecha de revisión**: 2025-05-06 (6 meses)

**Criterios de revisión**:
- Si GitHub cambia políticas de releases
- Si el equipo crece >20 personas (considerar S3)
- Si se requiere distribución offline (considerar servidor interno)
- Si costos de GitHub LFS bajan significativamente

---

## Referencias

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Release Limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas)
- [Git LFS Pricing](https://docs.github.com/en/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage)
- [SPEC_INFRA_001](../specs/SPEC_INFRA_001-cpython_precompilado.md)
- [ADR_008: Features vs Imagen Base](./ADR_008-cpython-features-vs-imagen-base.md)

---

**Decisión tomada por**: Equipo Infraestructura
**Aprobación requerida de**: Tech Lead, DevOps Lead
**Fecha límite de revisión**: 2025-05-06 (6 meses)
