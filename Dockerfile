###########
# BUILD
###########
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .

# Install dependencies
# Install into a virtual environment
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && find /opt/venv/lib/python3.12/site-packages -name "*.pyc" -delete \
    && find /opt/venv/lib/python3.12/site-packages -name "*.dist-info" -type d -exec rm -rf {} +

###########
# RUNTIME
###########
FROM python:3.12-alpine AS runtime

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy dependencies
COPY --from=builder /opt/venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy app code with ownership
COPY --chown=nobody:nobody src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
