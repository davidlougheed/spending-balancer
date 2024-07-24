FROM python:3.10-slim-bookworm

RUN apt-get update -y; \
    apt-get upgrade -y; \
    apt-get install -y bash

SHELL [ "/bin/bash", "-c" ]

RUN python -m pip install poetry

# ------

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

ENV SB_DEBUG=false
EXPOSE 8000

CMD [ "/bin/bash", "./run.bash" ]
