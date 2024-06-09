FROM python:3.11-slim-bullseye
RUN apt-get update && \
    apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python -

# Put Poetry on the path.
ENV PATH=/root/.local/bin:$PATH

ENV GIT_PYTHON_REFRESH=quiet

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY . .

RUN pip install -e .

ENTRYPOINT []