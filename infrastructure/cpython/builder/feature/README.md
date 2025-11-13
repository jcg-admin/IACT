# CPython Prebuilt Feature

**Version**: 1.0.0
**Reference**: SPEC_INFRA_001
**License**: Python Software Foundation License

---

## Description

This Dev Container Feature installs precompiled CPython with Profile-Guided Optimization (PGO) and Link-Time Optimization (LTO).

> **Note:** The canonical feature path is `./infrastructure/cpython/builder/feature`. A backwards compatible symlink is kept at
> `./infrastructure/cpython/installer` for existing configurations.

**Key benefits:**
- **90% faster builds**: Dev Container ready in <2 minutes vs 20+ minutes compiling from source
- **Production-grade**: Same optimizations used in official Python releases
- **Native modules**: All critical modules (ssl, sqlite3, uuid, lzma, bz2, zlib, ctypes) included
- **Zero configuration**: Just 3 lines in devcontainer.json

---

## Usage

### Basic Usage (GitHub Releases - Fase 3+)

Add to your `.devcontainer/devcontainer.json`:

```json
{
  "name": "My Django Project",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-22.04",
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6"
    }
  }
}
```

The feature will automatically download the precompiled artifact from GitHub Releases.

### Advanced Usage (Custom URL)

For testing or using a different distribution source:

```json
{
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6",
      "artifactUrl": "https://custom-host.com/cpython-3.12.6.tgz",
      "checksumUrl": "https://custom-host.com/cpython-3.12.6.tgz.sha256"
    }
  }
}
```

### Local Testing (Fase 2)

For local development and testing with locally built artifacts:

```json
{
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6",
      "artifactUrl": "/workspaces/IACT---project/infraestructura/cpython/artifacts/cpython-3.12.6-ubuntu20.04-build1.tgz",
      "checksumUrl": "/workspaces/IACT---project/infraestructura/cpython/artifacts/cpython-3.12.6-ubuntu20.04-build1.tgz.sha256"
    }
  }
}
```

---

## Options

### version

**Type**: `string`
**Default**: `"3.12.6"`
**Required**: No

CPython version to install. Must match the version available in your artifact source.

**Example**:
```json
{
  "version": "3.11.9"
}
```

### artifactUrl

**Type**: `string`
**Default**: `""` (uses GitHub Releases)
**Required**: No

URL or local path to the precompiled CPython tarball.

**Examples**:
```json
{
  "artifactUrl": "https://github.com/2-Coatl/IACT---project/releases/download/cpython-3.12.6-build1/cpython-3.12.6-ubuntu20.04-build1.tgz"
}
```

```json
{
  "artifactUrl": "/workspaces/project/infraestructura/cpython/artifacts-3.12.6.tgz"
}
```

### checksumUrl

**Type**: `string`
**Default**: `""` (derives from artifactUrl by appending .sha256)
**Required**: No

URL or local path to the SHA256 checksum file.

**Example**:
```json
{
  "checksumUrl": "https://example.com/cpython-3.12.6.tgz.sha256"
}
```

### installPrefix

**Type**: `string`
**Default**: `"/opt/python"`
**Required**: No

Installation directory prefix. The final path will be `{installPrefix}-{version}`.

**Example**:
```json
{
  "installPrefix": "/usr/local/python"
}
```

Result: Python installed at `/usr/local/python-3.12.6/`

### skipValidation

**Type**: `boolean`
**Default**: `false`
**Required**: No

**WARNING**: NOT RECOMMENDED for production use.

Skip SHA256 checksum validation. Only use for testing or when checksum is not available.

**Example**:
```json
{
  "skipValidation": true
}
```

---

## How It Works

### Installation Steps

1. **Idempotency check**: Detects if Python is already installed (via marker file)
2. **URL determination**: Uses GitHub Releases or custom URL
3. **Download**: Downloads artifact and checksum file
4. **Validation**: Verifies SHA256 checksum (unless skipValidation=true)
5. **Extraction**: Extracts tarball to `/opt/python-{version}/`
6. **System configuration**: Creates symlinks in `/usr/local/bin`, configures shared libraries
7. **Validation**: Tests Python version and native modules (ssl, sqlite3, etc.)
8. **Marker creation**: Creates `.installed` marker for future idempotency checks

### File Structure After Installation

```
/opt/python-3.12.6/
  +-- bin/
  |   +-- python3
  |   +-- python3.12
  |   +-- pip3
  |   +-- pip3.12
  +-- lib/
  |   +-- libpython3.12.so
  |   +-- python3.12/
  |       +-- site-packages/
  |       +-- lib-dynload/
  +-- include/
  +-- share/
  +-- .installed    # Marker file

/usr/local/bin/
  +-- python3 -> /opt/python-3.12.6/bin/python3
  +-- pip3 -> /opt/python-3.12.6/bin/pip3

/etc/ld.so.conf.d/
  +-- python3.12.conf
```

---

## Requirements

### Host Requirements

- **OS**: Ubuntu 20.04 LTS (or compatible with glibc >= 2.35)
- **Architecture**: x86_64 (amd64)
- **Tools**: wget or curl, sha256sum, tar, ldconfig

### Dev Container Base Image

Recommended base images:
- `mcr.microsoft.com/devcontainers/base:ubuntu-22.04`
- `mcr.microsoft.com/devcontainers/python:3-22.04` (will replace system Python)

**Not compatible with:**
- Alpine Linux (uses musl instead of glibc)
- Ubuntu 20.04 (glibc 2.31 is too old)
- CentOS/RHEL (different library paths)

---

## Troubleshooting

### Error: "Checksum mismatch"

**Cause**: Artifact file is corrupted or was tampered with.

**Solution**:
1. Verify the artifact was downloaded completely
2. Check if the correct checksum file is being used
3. Re-download both artifact and checksum
4. If building locally, rebuild the artifact

### Error: "Module ssl not available"

**Cause**: Artifact was built without OpenSSL libraries.

**Solution**:
1. Verify the build VM had `libssl-dev` installed
2. Rebuild the artifact with proper dependencies
3. See `infrastructure/cpython/README.md`

### Error: "Version mismatch"

**Cause**: The installed Python version doesn't match the requested version.

**Solution**:
1. Check that the `version` parameter matches the artifact filename
2. Verify the artifact contains the correct Python version
3. Delete `/opt/python-{version}` and rebuild the container

### Error: "Python already installed, skipping"

**Cause**: Feature detected previous installation (idempotency).

**Solution**: This is normal behavior. If you want to reinstall:
1. Delete the marker file: `rm /opt/python-{version}/.installed`
2. Rebuild the Dev Container

### Performance: Build still slow

**Possible causes**:
- Downloading large artifact over slow connection
- Extracting large tarball
- Running post-install hooks

**Solutions**:
- Use a faster internet connection
- Artifacts are cached after first download
- Check if other features are taking time

---

## Examples

### Example 1: Django Project

`.devcontainer/devcontainer.json`:
```json
{
  "name": "Django IACT Project",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-22.04",
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6"
    }
  },
  "postCreateCommand": "pip3 install -r requirements.txt",
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/opt/python-3.12.6/bin/python3"
      }
    }
  }
}
```

### Example 2: Multi-Project with Different Python Versions

Project A (Python 3.12):
```json
{
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6"
    }
  }
}
```

Project B (Python 3.11):
```json
{
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.11.9"
    }
  }
}
```

### Example 3: Local Development Testing

```json
{
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6",
      "artifactUrl": "/workspaces/IACT---project/infraestructura/cpython/artifacts/cpython-3.12.6-ubuntu20.04-build1.tgz"
    }
  }
}
```

---

## Security

### Checksum Validation

**Default**: ENABLED (skipValidation=false)

All artifacts are validated with SHA256 checksums before installation. This ensures:
- Artifact integrity (not corrupted during download)
- Protection against tampering
- Reproducible builds

**Never disable checksum validation in production environments.**

### Artifact Source

- **Phase 2 (current)**: Local filesystem paths
- **Phase 3+**: GitHub Releases (HTTPS with TLS 1.3)
- **Future**: GPG signature verification (ADR_009)

### CVE Monitoring

Python versions are monitored for security vulnerabilities. When a CVE is published:
1. Rebuild with patched CPython version
2. Publish new artifact to GitHub Releases
3. Update `artifacts/ARTIFACTS.md`
4. Notify projects to upgrade

See: `docs/specs/SPEC_INFRA_001_cpython_precompilado.md` section 10.1

---

## Testing

### Manual Testing

1. Build artifact locally:
```bash
make build_cpython VERSION=3.12.6
make validate-cpython ARTIFACT=cpython-3.12.6-ubuntu20.04-build1.tgz
```

2. Create test devcontainer.json:
```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-22.04",
  "features": {
    "./infrastructure/cpython/builder/feature": {
      "version": "3.12.6",
      "artifactUrl": "/workspaces/IACT---project/infraestructura/cpython/artifacts/cpython-3.12.6-ubuntu20.04-build1.tgz"
    }
  }
}
```

3. Build Dev Container in VS Code

4. Verify installation:
```bash
python3 --version
python3 -c "import ssl, sqlite3, uuid, lzma, bz2, zlib, ctypes; print('All modules OK')"
pip3 --version
```

### Automated Testing

Integration tests available:
```bash
pytest tests/integration/test_cpython_feature.py -v
```

---

## Versioning

This feature follows Semantic Versioning (semver):

- **1.0.0**: Initial release (Fase 2)
- **1.1.0**: GitHub Releases support (Fase 3)
- **1.2.0**: GPG signature verification (Fase 4)
- **2.0.0**: Breaking changes (if any)

See: `infrastructure/cpython/builder/feature/devcontainer_feature.json`

---

## References

- **Specification**: docs/specs/SPEC_INFRA_001_cpython_precompilado.md
- **Architecture**: docs/infraestructura/cpython_precompilado/arquitectura.md
- **ADR_008**: Features vs Docker Base Image
- **ADR_009**: Distribution Strategy
- **Dev Containers Spec**: https://containers.dev/
- **CPython License**: https://docs.python.org/3/license.html

---

## Contributing

This feature is part of the IACT project infrastructure.

To contribute:
1. Create feature branch following spec-driven development
2. Ensure all tests pass
3. Follow the no-emoji rule
4. Reference SPEC_INFRA_001 in commits
5. Update this README if adding new options

---

## License

This feature installer is part of IACT project (project-specific license).

The distributed CPython binaries are licensed under the Python Software Foundation License.

See: https://docs.python.org/3/license.html

---

**Maintained by**: Equipo Infraestructura IACT
**Last updated**: 2025-11-06
**Feature version**: 1.0.0
