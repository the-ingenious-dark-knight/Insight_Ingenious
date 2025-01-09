docker stop guardrails-server || true
docker rm guardrails-server || true
docker run -p 8000:8000 -env AZURE_API_KEY AZURE_API_BASE AZURE_API_VERSION --name guardrails-server -it guardrails-server:dev