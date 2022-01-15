FROM python:3.8 as builder
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
RUN pip install --no-cache-dir Werkzeug python-magic google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client

COPY . /app
ENV PYTHONPATH=/app

FROM builder as dev

RUN poetry install --no-root

EXPOSE 80

COPY ./start-dev.sh ./start-dev.sh
RUN chmod +x ./start-dev.sh
CMD ["bash", "./start-dev.sh"]

FROM builder as prod

RUN poetry install --no-root --no-dev
EXPOSE 80

COPY ./start-prod.sh ./start-prod.sh
RUN chmod +x ./start-prod.sh
CMD ["bash", "./start-prod.sh"]