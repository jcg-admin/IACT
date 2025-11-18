# =============================================================================
# CALLCENTER DJANGO API - DEVCONTAINER
# =============================================================================
# Base image: Python 3.11 on Debian Bookworm
# Includes: PostgreSQL client, MariaDB client, development tools
# =============================================================================

FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# =============================================================================
# METADATA
# =============================================================================

LABEL maintainer="IACT Team"
LABEL description="Django CallCenter API DevContainer"
LABEL version="1.0.0"

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

# Python configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Locale configuration
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Timezone
ENV TZ=America/Mexico_City

# User configuration
ENV USERNAME=vscode \
    USER_UID=1000 \
    USER_GID=1000

# =============================================================================
# INSTALL SYSTEM DEPENDENCIES
# =============================================================================

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    python3-dev \
    postgresql-client \
    libpq-dev \
    default-mysql-client \
    default-libmysqlclient-dev \
    git \
    git-lfs \
    curl \
    wget \
    vim \
    nano \
    less \
    tree \
    htop \
    jq \
    zip \
    unzip \
    net-tools \
    iputils-ping \
    dnsutils \
    locales \
    tzdata \
    ca-certificates \
    sudo \
    bash-completion \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# CONFIGURE LOCALE
# =============================================================================

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

# =============================================================================
# CONFIGURE TIMEZONE
# =============================================================================

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# =============================================================================
# UPGRADE PIP AND INSTALL GLOBAL PYTHON PACKAGES
# =============================================================================

RUN pip install --upgrade pip setuptools wheel

# Install global Python development tools
RUN pip install --no-cache-dir \
    black \
    flake8 \
    pylint \
    isort \
    pytest \
    pytest-cov \
    pytest-django \
    pytest-mock \
    mypy \
    django-extensions \
    django-debug-toolbar \
    psycopg2-binary \
    mysqlclient \
    ipython \
    ipdb

# =============================================================================
# CREATE WORKSPACE DIRECTORY
# =============================================================================

RUN mkdir -p /workspaces \
    && chown -R ${USERNAME}:${USERNAME} /workspaces

# =============================================================================
# CONFIGURE BASH HISTORY PERSISTENCE
# =============================================================================

# Create directory for bash history
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && mkdir -p /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R ${USERNAME}:${USERNAME} /commandhistory \
    && echo "$SNIPPET" >> "/home/${USERNAME}/.bashrc"

# =============================================================================
# CONFIGURE SUDO FOR VSCODE USER
# =============================================================================

# Allow vscode user to use sudo without password
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# =============================================================================
# CONFIGURE GIT
# =============================================================================

# Set safe directory for git (prevents "dubious ownership" errors)
RUN git config --system --add safe.directory '*'

# =============================================================================
# CREATE DIRECTORIES FOR LOGS AND STATE
# =============================================================================

RUN mkdir -p /workspaces/infrastructure/devcontainer/logs \
    && mkdir -p /workspaces/infrastructure/state \
    && chown -R ${USERNAME}:${USERNAME} /workspaces/infrastructure

# =============================================================================
# HEALTHCHECK
# =============================================================================

# Simple healthcheck to verify Python is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 --version || exit 1

# =============================================================================
# USER
# =============================================================================

# Switch to non-root user
USER ${USERNAME}

# Set working directory
WORKDIR /workspaces

# =============================================================================
# ENTRYPOINT
# =============================================================================

# Use bash as default shell
SHELL ["/bin/bash", "-c"]

# Keep container running (for DevContainer)
CMD ["sleep", "infinity"]