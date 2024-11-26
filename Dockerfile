# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/oracle/

# Install Oracle Instant Client
RUN apt-get update && apt-get install -y libaio1 wget unzip && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    rm instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    mv instantclient_21_15 /opt/oracle/instantclient && \
    echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Set Oracle environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient:${LD_LIBRARY_PATH}
ENV ORACLE_HOME=/opt/oracle/instantclient

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's    caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 4325

# Run the application.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4325", "--access-logfile","-","--log-file","-", "app:app"]