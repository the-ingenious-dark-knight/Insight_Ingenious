# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /ingen_app
COPY requirements.txt ./installs/requirements.txt
# In bash create a directory and copy the app into it
#RUN apt update
#RUN apt install python3.12 -y
#RUN apt install python3-pip -y
RUN pip install -r ./installs/requirements.txt
# Change to the app directory
WORKDIR /ingen_app
#RUN pip install ingenious-1.0.0-py3-none-any.whl[ChatHistorySummariser]
#python3 -m venv ".venv"  

CMD ["cat"]