###########
# BUILD
###########
FROM python:3.13-alpine@sha256:070342a0cc1011532c0e69972cce2bbc6cc633eba294bae1d12abea8bd05303b AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && find /opt/venv/lib/python3.13/site-packages -name "*.pyc" -delete \
    && find /opt/venv/lib/python3.13/site-packages -name "*.dist-info" -type d -exec rm -rf {} +

###########
# RUNTIME
###########
FROM python:3.13-alpine@sha256:070342a0cc1011532c0e69972cce2bbc6cc633eba294bae1d12abea8bd05303b AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /opt/venv/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY --chown=nobody:nobody src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
