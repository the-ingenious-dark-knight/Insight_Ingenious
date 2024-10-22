# syntax=docker/dockerfile:1
FROM docker.io/library/ubuntu:jammy

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /ingen_app
#COPY ingenious-1.0.0-py3-none-any.whl /ingen_app/ingenious-1.0.0-py3-none-any.whl
# In bash create a directory and copy the app into it
RUN apt update
RUN apt install python3
RUN apt install python3-pip
# Change to the app directory
WORKDIR /ingen_app
#RUN pip install ingenious-1.0.0-py3-none-any.whl[ChatHistorySummariser]
python3 -m venv ".venv"  

CMD ["cat"]