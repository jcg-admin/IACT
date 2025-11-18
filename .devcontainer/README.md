# DevContainer Setup

This directory contains the configuration for the development container environment.

## Quick Start

### 1. Set up environment variables

Before starting the devcontainer, you need to create a `.env` file with your credentials:

```bash
# Copy the example file
cp .env.example .env
```

Then edit the `.env` file and replace the placeholder passwords:
- `POSTGRES_PASSWORD` - PostgreSQL database password
- `MARIADB_ROOT_PASSWORD` - MariaDB root password
- `DJANGO_SUPERUSER_PASSWORD` - Django admin password

**Important:** Never commit the `.env` file to version control! It's already included in `.gitignore`.

### 2. Open in DevContainer

Open the repository in VS Code and select "Reopen in Container" when prompted, or use the command palette (Ctrl+Shift+P / Cmd+Shift+P) and select "Dev Containers: Reopen in Container".

## Files

- `Dockerfile` - Container image definition
- `devcontainer.json` - VS Code DevContainer configuration
- `docker_compose.yml` - Docker Compose configuration for services
- `.env.example` - Example environment variables (safe to commit)
- `.env` - Your actual credentials (never commit this!)

## Services

The devcontainer includes three services:

1. **app** - Django development environment
2. **db_postgres** - PostgreSQL database (default)
3. **db_mariadb** - MariaDB database (legacy)

## Security

All sensitive credentials are stored in the `.env` file, which is:
- Excluded from version control via `.gitignore`
- Not shared between developers
- Easy to rotate without modifying tracked files

This approach prevents accidentally committing production credentials or exposing sensitive information.
