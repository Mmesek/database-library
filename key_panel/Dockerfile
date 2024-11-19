FROM cgr.dev/chainguard/python:latest-dev AS dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONBUFFERED=1

WORKDIR /app

RUN python -m venv /app/.venv
COPY requirements.txt ./
RUN python -m pip --disable-pip-version-check --no-cache-dir install -r requirements.txt

FROM cgr.dev/chainguard/python:latest

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONBUFFERED=1
WORKDIR /app

COPY --from=dev /app/.venv /app/.venv

COPY ["__main__.py", "/app/__main__.py"]

ENTRYPOINT [ "python", "-m", "app"]
