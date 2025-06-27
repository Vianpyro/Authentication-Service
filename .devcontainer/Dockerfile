FROM alpine:latest

# Install common tools, PostgreSQL and build tools for pgTAP
RUN apk add --no-cache bash git \
    postgresql postgresql-contrib su-exec tini nodejs npm \
    make gcc musl-dev postgresql-dev perl patch \
    build-base perl-dev openssl-dev python3 py3-pip \
    && cpan TAP::Parser::SourceHandler::pgTAP

# Clone pgTAP for Unit Testing
RUN git clone --depth 1 https://github.com/theory/pgtap

# Build and install pgTAP
WORKDIR /pgtap
RUN make && make install

# Cleanup
WORKDIR /
RUN rm -rf /pgtap

# Install sqlfluff for SQL linting
RUN ["/bin/bash", "-c", "pip3 --disable-pip-version-check --no-cache-dir install sqlfluff --break-system-packages"]

# Setup default user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN addgroup -g $USER_GID -S $USERNAME && \
    adduser -u $USER_UID -S -G $USERNAME -s /bin/bash $USERNAME && \
    mkdir -p /var/lib/postgresql/data /run/postgresql && \
    chown -R $USERNAME:$USERNAME /var/lib/postgresql /run/postgresql

# Set environment variables for PostgreSQL
ENV PGDATA=/var/lib/postgresql/data

WORKDIR /workspace

# Switch to the default user
USER $USERNAME

# Set environment variables for pip
ENV PATH="/home/${USERNAME}/.local/bin:$PATH" \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1
