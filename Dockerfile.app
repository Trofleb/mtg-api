FROM python:3.13-slim

WORKDIR /code

ARG POETRY_VERSION=2.0.1

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --with=app

COPY app/ .
COPY common/ ./common

EXPOSE 8000

ENTRYPOINT [ "streamlit" ]
CMD [ "run", "app.py" ]
