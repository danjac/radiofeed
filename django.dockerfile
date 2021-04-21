FROM python:3.9.2-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random

RUN apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client-11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader wordnet

WORKDIR /app

COPY ./scripts/docker/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./scripts/docker/start-django /start-django
RUN chmod +x /start-django

COPY ./scripts/docker/start-celeryworker /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./scripts/docker/start-celerybeat /start-celerybeat
RUN chmod +x /start-celerybeat

EXPOSE 8000

ENTRYPOINT ["/entrypoint"]
