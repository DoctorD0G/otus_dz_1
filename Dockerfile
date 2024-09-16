FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry

RUN poetry install --no-dev

COPY . .

ENTRYPOINT ["poetry", "run", "analyze-logs"]

CMD ["./access.log"]
