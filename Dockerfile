###########
# BUILD
###########
FROM python:3.14-alpine@sha256:8373231e1e906ddfb457748bfc032c4c06ada8c759b7b62d9c73ec2a3c56e710 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && find /opt/venv/lib/python3.14/site-packages -name "*.pyc" -delete \
    && find /opt/venv/lib/python3.14/site-packages -name "*.dist-info" -type d -exec rm -rf {} +

###########
# RUNTIME
###########
FROM python:3.14-alpine@sha256:8373231e1e906ddfb457748bfc032c4c06ada8c759b7b62d9c73ec2a3c56e710 AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /opt/venv/lib/python3.14/site-packages /usr/local/lib/python3.13/site-packages

COPY --chown=nobody:nobody src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
