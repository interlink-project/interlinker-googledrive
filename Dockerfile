FROM python:3.9-slim as os-base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update
RUN apt-get install -y curl libmagic1

FROM os-base as poetry-base
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:$PATH"
RUN poetry config virtualenvs.create false
RUN apt-get remove -y curl

FROM poetry-base as builder
WORKDIR /app/
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
RUN pip install --no-cache-dir Werkzeug python-magic google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client
COPY . /app
ENV PYTHONPATH=/app

FROM builder as dev
RUN poetry install --no-root
COPY ./start-dev.sh ./start-dev.sh
RUN chmod +x ./start-dev.sh
CMD ["bash", "./start-dev.sh"]

FROM builder as prod
RUN poetry install --no-root --no-dev
COPY ./start-prod.sh ./start-prod.sh
RUN chmod +x ./start-prod.sh
CMD ["bash", "./start-prod.sh"]