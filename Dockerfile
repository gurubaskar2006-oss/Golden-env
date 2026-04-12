FROM public.ecr.aws/docker/library/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8000
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

RUN useradd -m -u 1000 user
USER user
WORKDIR $HOME/app

COPY --chown=user pyproject.toml README.md openenv.yaml inference.py task_graders.py uv.lock ./
COPY --chown=user golden_hour_dispatch_env ./golden_hour_dispatch_env
COPY --chown=user server ./server
COPY --chown=user tests ./tests

RUN pip install --upgrade pip && pip install .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "uvicorn golden_hour_dispatch_env.server.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
