---
id: DOC-ARQ-DEVCONTAINER-HOST-VAGRANT
estado: propuesta
propietario: equipo-plataforma-devops
ultima_actualizacion: 2025-11-19
relacionados: ["DOC-DEVOPS-INDEX", "DOC-INFRA-INDEX", "DOC-ARQ-INFRA"]
---
# Canvas técnico — DevContainer Host con Vagrant

Documento de referencia para estandarizar el host de DevContainers y pipelines CI/CD en una VM gestionada por Vagrant cuando el equipo no puede instalar Docker en sus laptops.

## 1. Identificación
- **Nombre del artefacto:** DevContainer Host con Vagrant
- **Proyecto:** IACT / Plataforma de Desarrollo y CI/CD
- **Versión:** 1.0
- **Responsable:** Equipo de Plataforma / DevOps
- **Estado:** Propuesta técnica inicial

## 2. Propósito del DevContainer Host
- Centralizar la ejecución de DevContainers y pipelines CI/CD en una sola VM.
- Mantener un único lugar donde se instala el runtime de contenedores (Podman rootless o Docker dentro de la VM).
- Servir como fuente de verdad del entorno (SO, toolchains, dependencias del sistema, configuración de usuario y permisos).
- Permitir que el host físico (workstation) opere sin Docker, conectándose por SSH.

## 3. Descripción general
### 3.1 Topología lógica
```
+---------------------------+
| Workstation desarrollador |
| (Windows / macOS / Linux) |
|                           |
| - VS Code                 |
| - Ext. Remote SSH         |
| - Ext. Dev Containers     |
|                           |
| SIN Docker en el host     |
+-------------+-------------+
              |
              | SSH
              v
+---------------------------+
| Vagrant VM (DevContainer Host) |
| SO: Ubuntu Server LTS          |
|                                |
| - Runtime contenedores:        |
|     Podman rootless o          |
|     Docker (solo en la VM)     |
| - Toolchains compartidos       |
| - Runner CI/CD (self-hosted)   |
+---------------------------+
```

### 3.2 Rol operativo
- La VM aloja imágenes e instancias de DevContainer para desarrollo y CI/CD.
- Los repositorios viven en `/srv/projects` dentro de la VM y se montan en los contenedores.
- Los artefactos de runtime se almacenan en `/var/lib/containers` (Podman) o el directorio equivalente de Docker dentro de la VM.

## 4. Especificación de la Vagrant VM como DevContainer Host
### 4.1 Características de la VM
- **Nombre lógico:** `iact-devcontainer-host`
- **Proveedor:** VirtualBox, Libvirt o Hyper-V (según el entorno del desarrollador).
- **Sistema operativo:** Ubuntu 20.04 LTS o 22.04 LTS (alineado con CI/CD).
- **Recursos mínimos:** 4 vCPUs, 8 GB RAM (ajustable), disco dinámico 80–120 GB.

### 4.2 Roles dentro de la VM
- **DevContainer Host:** Ejecuta el runtime de contenedores y aloja imágenes/instancias de DevContainer.
- **CI/CD Execution Node (opcional recomendado):** Runner self-hosted (GitHub Actions o GitLab CI) que reutiliza las mismas imágenes que el DevContainer de desarrollo.

## 5. Componentes dentro de la Vagrant VM
### 5.1 Runtime de contenedores
- **Opción preferida:** Podman rootless para minimizar dependencias privilegiadas.
- **Opción alternativa:** Docker instalado únicamente dentro de la VM.
- **Requisitos:** Compatibilidad OCI y soporte de DevContainer CLI/VS Code.

### 5.2 Toolchain base
- Paquetes: `build-essential`, `git`, `curl`, `wget`, `python3`, `python3-venv` (extensible según el proyecto, p. ej. Node/Go).
- Usuario de trabajo: `dev` o equivalente para sesiones SSH y contenedores rootless.

### 5.3 Almacenamiento
- Directorios clave: `/srv/devcontainers` (imágenes/configs base), `/srv/projects` (repositorios), `/var/lib/containers` (runtime).
- Recomendación: discos virtuales separados si se requiere aislamiento adicional o mayor rendimiento de I/O.

## 6. Flujo de trabajo con Vagrant
### 6.1 Provisión inicial
1. El desarrollador clona el repositorio de infra que incluye `Vagrantfile` y scripts de provisión.
2. Ejecuta `vagrant up iact-devcontainer-host`.
3. Vagrant crea la VM, instala el SO base y aplica los scripts de provisión para:
   - Instalar el runtime de contenedores.
   - Configurar el usuario `dev`.
   - Instalar toolchains base.
4. Resultado: VM lista para usarse como host de DevContainer.

### 6.2 Uso diario (desarrollo)
1. El desarrollador abre VS Code en su host físico.
2. Con Remote SSH se conecta a `dev@iact-devcontainer-host`.
3. Dentro de la VM abre el repo en `/srv/projects/iact` y lanza el DevContainer definido en `devcontainer.json`.
4. Desarrollo, pruebas y depuración ocurren dentro del DevContainer.

### 6.3 Uso en CI/CD
1. Registrar un runner self-hosted dentro de la misma VM (servicio `runner-iact-devcontainer`).
2. El pipeline usa el mismo runtime de contenedores e imágenes base que el DevContainer de desarrollo.
3. Ejecuta pruebas unitarias, de integración, builds y análisis estático con el mismo toolchain.

## 7. Objetivos técnicos
- **Environmental consistency:** VM provisionada con configuración versionada para replicar CI/CD.
- **Operational equivalence:** Mismo runtime de contenedores y misma imagen base para desarrollo y pipelines.
- **Deterministic execution:** Scripts de bootstrap idempotentes reutilizados por dev y CI/CD.
- **Unified toolchain:** Toolchain definido una sola vez en la VM e imagen DevContainer.

## 8. Riesgos específicos con Vagrant
- Desfase de versiones de la VM entre desarrolladores y CI/CD.
- Overhead de recursos en la workstation (RAM/CPU) al ejecutar la VM.
- Complejidad para sincronizar cambios en los scripts de provisión.

## 9. Mitigaciones
- Versionar estrictamente `Vagrantfile` y scripts de provisión (p. ej. `provision.sh`, Ansible).
- Política de actualización clara: cuándo regenerar la VM (`vagrant destroy && vagrant up`).
- Documentar comandos estándar y troubleshooting básico de la VM.

## 10. Checklist mínimo de implementación
- [ ] Definir `Vagrantfile` para `iact-devcontainer-host`.
- [ ] Definir scripts de provisión (runtime contenedores, usuario `dev`, toolchains base).
- [ ] Probar creación de VM en una workstation de desarrollo.
- [ ] Configurar acceso SSH desde VS Code (Remote SSH).
- [ ] Probar DevContainer de desarrollo en la VM.
- [ ] Registrar y probar runner de CI/CD dentro de la VM.
- [ ] Documentar el flujo completo en este archivo.
