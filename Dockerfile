FROM python:3.12-slim AS runtime

ARG INSTALL_ML=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt requirements-ml.txt ./
RUN if [ "$INSTALL_ML" = "true" ]; then \
        pip install --no-cache-dir -r requirements-ml.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

RUN addgroup --system app && \
    adduser --system --ingroup app --home /home/app app

COPY --chown=app:app app ./app
COPY --chown=app:app wsgi.py ./wsgi.py

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "wsgi:app"]

FROM runtime AS test

USER root
COPY requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
RUN pytest -q

FROM runtime AS production
