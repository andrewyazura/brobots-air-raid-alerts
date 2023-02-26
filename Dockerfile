# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

WORKDIR /app

RUN ["pip", "install", "pipenv"]

COPY Pipfile Pipfile.lock ./

RUN ["pipenv", "install", "--system", "--deploy", "--ignore-pipfile"]

CMD ["python", "main.py"]

COPY src src
COPY main.py config.py ./
