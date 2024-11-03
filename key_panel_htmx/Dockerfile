FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN set -ex \
    && addgroup --gid 50000 python \
    && adduser --shell /bin/false --disabled-password --uid 50000 --gid 50000 --no-create-home python \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN python -m pip --disable-pip-version-check --no-cache-dir install -r requirements.txt \ 
    && rm -rf requirements.txt

COPY ["__main__.py", "/app/__main__.py"]

ENTRYPOINT [ "python", "-m", "app"]
