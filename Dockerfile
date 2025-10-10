###########
# BUILD
###########
FROM python:3.14-alpine@sha256:829edcc737417f9084a154511bde03a50b7996f3746e4c8a6b30a99a9a10648c AS builder

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
FROM python:3.14-alpine@sha256:829edcc737417f9084a154511bde03a50b7996f3746e4c8a6b30a99a9a10648c AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /opt/venv/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY --chown=nobody:nobody src/ .

USER nobody

ENTRYPOINT ["python", "entrypoint.py"]
