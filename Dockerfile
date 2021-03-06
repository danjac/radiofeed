FROM python:3.9.5-buster


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random

# dependencies

RUN apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client-11 curl ca-certificates inotify-tools

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# python requirements

RUN pip install poetry

COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock

RUN poetry config virtualenvs.create false

# https://github.com/python-poetry/poetry/issues/3321
RUN mkdir -p /usr/local/lib/python3.9/site-packages

RUN poetry install

RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader wordnet

# frontend requirements

COPY postcss.config.js ./postcss.config.js
COPY tailwind.config.js ./tailwind.config.js
COPY package.json ./package.json
COPY package-lock.json ./package-lock.json

RUN npm cache clean --force
RUN npm ci


# scripts

COPY ./scripts/docker/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./scripts/docker/start-webapp /start-webapp
RUN chmod +x /start-webapp

COPY ./scripts/docker/start-celeryworker /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./scripts/docker/start-celerybeat /start-celerybeat
RUN chmod +x /start-celerybeat

