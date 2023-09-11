# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

FROM base AS export-requirements-stage
WORKDIR /tmp

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry export --format requirements.txt \
    --output requirements.txt --without-hashes


FROM base AS run-app-stage
WORKDIR /code

COPY --from=export-requirements-stage /tmp/requirements.txt ./
RUN pip install --upgrade --no-cache-dir --requirement requirements.txt

CMD ["python3", "main.py"]

COPY ./src /code/src
COPY ./main.py ./config.py /code/
