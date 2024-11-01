# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /ingen_app
# Create and set the working directory

COPY ingenious-1.0.0-py3-none-any.whl ./ingen_app/ingenious-1.0.0-py3-none-any.whl
COPY requirements.txt ./installs/requirements.txt

# In bash create a directory and copy the app into it

WORKDIR /ingen_app
RUN pip install ./ingenious-1.0.0-py3-none-any.whl[ChatHistorySummariser]
RUN pip install -r ./installs/requirements.txt
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
           AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
           AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Set the command to run the app
CMD ["ingen_cli", "config.yml", "profile.yml"]
