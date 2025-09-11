###########
# BUILD
###########
FROM python:3.12-alpine@sha256:02a73ead8397e904cea6d17e18516f1df3590e05dc8823bd5b1c7f849227d272 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && find /opt/venv/lib/python3.12/site-packages -name "*.pyc" -delete \
    && find /opt/venv/lib/python3.12/site-packages -name "*.dist-info" -type d -exec rm -rf {} +

###########
# RUNTIME
###########
FROM python:3.12-alpine@sha256:02a73ead8397e904cea6d17e18516f1df3590e05dc8823bd5b1c7f849227d272 AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /opt/venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY --chown=nobody:nobody src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
