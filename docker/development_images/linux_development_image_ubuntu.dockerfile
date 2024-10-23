# syntax=docker/dockerfile:1
FROM docker.io/ubuntu:24.04

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt update 
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y python3.12-venv


#RUN mkdir /ingen_app
COPY requirements.txt ./installs/requirements.txt
RUN python3 -m venv .venv
RUN . ./.venv/bin/activate && pip3 install -r ./installs/requirements.txt
# Change to the app directory
#WORKDIR /ingen_app
RUN apt install -y  wget
#RUN wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && apt-get update 
#RUN wget https://github.com/PowerShell/PowerShell/releases/download/v7.4.5/powershell_7.4.5-1.deb_amd64.deb && dpkg -i powershell_7.#4.5-1.deb_amd64.deb && apt-get install -f && rm powershell_7.4.5-1.deb_amd64.deb
RUN apt install zsh git fonts-font-awesome -y 
RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
#RUN . ./.venv/bin/activate && python3 -c "from transformers import AutoTokenizer, AutoModel; \
#           AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
#           AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

CMD ["cat"]