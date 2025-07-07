FROM python:3.12-slim

WORKDIR /backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-cyrillic \
    lmodern \
    fonts-liberation \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock /backend/

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

COPY app /backend/app

ENV PYTHONPATH=/backend

CMD ["poetry", "run", "sh", "-c", "cd app/database && alembic upgrade head && cd .. && python3 ./main.py"]
