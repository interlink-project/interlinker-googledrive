FROM python:3.9-slim-buster as builder
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update
RUN pip3 install poetry==1.2.0
RUN apt-get install -y libmagic1
RUN poetry config virtualenvs.create false
WORKDIR /app/
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
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