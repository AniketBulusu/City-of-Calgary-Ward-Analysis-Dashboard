FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY datasets ./datasets
COPY entrypoint.sh /entrypoint.sh

# Fix line endings and make executable
RUN apt-get update && \
    apt-get install -y dos2unix && \
    dos2unix /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    apt-get remove -y dos2unix && \
    rm -rf /var/lib/apt/lists/*

ENV DATABASE_URL=postgresql+psycopg2://appuser:app_password@db:5432/calgary_ward_db

EXPOSE 8050

ENTRYPOINT ["/entrypoint.sh"]