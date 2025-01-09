#!/bin/bash

docker build \
    -f Dockerfile \
    --build-arg="GUARDRAILS_TOKEN=$GUARDRAILS_TOKEN" \
    -t "guardrails-server:latest" .;


# if running into issues on m based Apple Macs try forcing the build platform with --platform linux/amd64

docker run -d -p 8000:8000 \
  -e AZURE_API_KEY \
  -e AZURE_API_BASE \
  -e AZURE_API_VERSION \
  --name guardrails-server \
  -it guardrails-server:latest

docker run -d -p 8000:8000 -e OPENAI_API_KEY=[YOUR OPENAI KEY] gr-backend-images:latest