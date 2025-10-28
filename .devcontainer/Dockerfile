FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ARG USER_UID=1000
ARG USER_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    mariadb-client \
    default-libmysqlclient-dev \
    gcc \
    g++ \
    make \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN if ! getent group ${USER_GID} >/dev/null 2>&1; then \
        groupadd -g ${USER_GID} django; \
    fi \
    && if ! id -u ${USER_UID} >/dev/null 2>&1; then \
        useradd -u ${USER_UID} -g ${USER_GID} -m -s /bin/bash django; \
    fi \
    && mkdir -p /workspace \
    && chown -R ${USER_UID}:${USER_GID} /workspace

WORKDIR /workspace
USER ${USER_UID}:${USER_GID}

CMD ["sleep", "infinity"]