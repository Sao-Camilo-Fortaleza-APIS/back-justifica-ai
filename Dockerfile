FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies, including gnupg for handling apt keys
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    unixodbc \
    unixodbc-dev \
    libssl-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install SQL Server ODBC Driver
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl -sSL https://packages.microsoft.com/config/ubuntu/20.04/prod.list -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Verificar se o driver foi instalado corretamente
RUN odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
RUN mkdir -p /opt/oracle/

# Install Oracle Instant Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient:${LD_LIBRARY_PATH}
ENV ORACLE_HOME=/opt/oracle/instantclient

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
RUN adduser \
    --uid "${UID}" \
    appuser

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt
COPY . .
EXPOSE 4325

# Run the application.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4325", "--access-logfile","-","--log-file","-", "app:app"]