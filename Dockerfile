# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create directory for certificate
RUN mkdir -p /app/certs

# Install system dependencies, including gnupg for handling apt keys
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    unixodbc \
    unixodbc-dev \
    libssl-dev \
    curl \
    gnupg \
    ca-certificates && \
    update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft's GPG key for the ODBC driver
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc

# Install ODBC driver for SQL Server using the correct Debian repository for Bullseye (Debian 11)
RUN echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/microsoft.asc] https://packages.microsoft.com/debian/11/prod stable main" > /etc/apt/sources.list.d/mssql-release.list

# Install msodbcsql17 driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify if the ODBC driver was installed correctly
RUN odbcinst -q -d -n "ODBC Driver 17 for SQL Server"

# Install Oracle Instant Client
RUN mkdir -p /opt/oracle/ && apt-get update && apt-get install -y libaio1 wget unzip && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    rm instantclient-basic-linux.x64-21.15.0.0.0dbru.zip && \
    mv instantclient_21_15 /opt/oracle/instantclient && \
    echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Set Oracle environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient:${LD_LIBRARY_PATH}
ENV ORACLE_HOME=/opt/oracle/instantclient

# Create a non-privileged user that the app will run under
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application
USER appuser

# Copy the source code into the container
COPY . .

# Expose the port that the application listens on
EXPOSE 4325

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4325", "--access-logfile","-","--log-file","-", "--certfile=/app/certs/nginx.crt", "--keyfile=/app/certs/nginx.key", "app:app"]
