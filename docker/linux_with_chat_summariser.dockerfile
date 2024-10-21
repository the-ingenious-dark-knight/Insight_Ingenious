# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /ingen_app

# Copy pyproject.toml and poetry.lock (if available) into the container
COPY pyproject.toml poetry.lock* /ingen_app/

# Install dependencies using Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

# Copy the rest of the application files
COPY . /ingen_app

# Set the command to run the app
CMD ["ingen_cli", "config.yml", "profile.yml"]
