# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

WORKDIR /code

RUN ["pip", "install", "pipenv"]

COPY ./Pipfile ./Pipfile.lock /code/

RUN ["pipenv", "install", "--system", "--deploy", "--ignore-pipfile"]

CMD ["python", "main.py"]

COPY ./src /code/src
COPY ./main.py ./config.py /code/
