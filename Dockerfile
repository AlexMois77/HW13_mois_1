
FROM python:3.11-slim


RUN apt-get update && apt-get install -y build-essential libpq-dev


RUN pip install poetry


WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi


COPY . /app


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
