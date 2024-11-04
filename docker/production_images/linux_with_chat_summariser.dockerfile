# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /ingen_app

# Create a virtual environment
RUN python -m venv /ingen_app/venv

# Copy the built wheel and requirements file into the container
COPY dist/ingenious-*.whl /ingen_app/ingenious-1.0.0-py3-none-any.whl
COPY requirements.txt /ingen_app/installs/requirements.txt

# Activate virtual environment and install dependencies
RUN . /ingen_app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install /ingen_app/ingenious-1.0.0-py3-none-any.whl \
    && pip install -r /ingen_app/installs/requirements.txt

# Pre-download the necessary transformer models
RUN . /ingen_app/venv/bin/activate \
    && python -c "from transformers import AutoTokenizer, AutoModel; \
                  AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
                  AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Update the PATH so that the virtual environment is the default Python
ENV PATH="/ingen_app/venv/bin:$PATH"
