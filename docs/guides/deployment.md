# Deployment Guide

This guide covers how to deploy the Insight Ingenious application to various environments.

## Prerequisites

Before deploying, ensure you have:

- Completed application configuration in `config.yaml`
- Set up environment variables for sensitive information
- Tested the application locally

## Development Deployment

For development or testing purposes:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Production Deployment

For production, we recommend using a proper WSGI server like Gunicorn along with a reverse proxy like Nginx.

### Using Gunicorn

1. Install Gunicorn with uv:

```bash
uv add gunicorn
```

2. Create a script to run the application (e.g., `start.sh`):

```bash
#!/bin/bash
export $(cat .env | xargs)
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. Make it executable:

```bash
chmod +x start.sh
```

4. Run the script:

```bash
./start.sh
```

### Docker Deployment

1. Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -e .

# Copy application code
COPY . .

# Run the application
CMD ["uv", "run", "gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

2. Build the Docker image:

```bash
docker build -t insight-ingenious .
```

3. Run the container:

```bash
docker run -p 8000:8000 --env-file .env insight-ingenious
```

### Docker Compose

For more complex deployments, create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
  
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
```

## Cloud Deployment

### Azure App Service

1. Create an App Service Plan and Web App in Azure Portal

2. Configure deployment from a Git repository or Docker container

3. Set environment variables in the Azure Portal:
   - Go to Configuration > Application settings
   - Add all required environment variables

4. Deploy the application

### AWS Elastic Beanstalk

1. Create a `Procfile` in your project:

```
web: uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

2. Create a `requirements.txt` file:

```bash
uv pip freeze > requirements.txt
```

3. Deploy using the AWS Elastic Beanstalk CLI:

```bash
eb init
eb create
```

## Environment Variables

Ensure these environment variables are set in your deployment environment:

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password
```

## SSL/TLS Configuration

For production deployments, always use HTTPS:

1. Obtain an SSL certificate (e.g., Let's Encrypt)
2. Configure your reverse proxy (Nginx, Apache) to handle SSL/TLS
3. Redirect HTTP traffic to HTTPS

Example Nginx configuration with SSL:

```
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Logging

Consider setting up:

1. Centralized logging (e.g., Elasticsearch, Logstash, Kibana)
2. Application monitoring (e.g., Prometheus, Grafana)
3. Error tracking (e.g., Sentry)

## Scaling

For horizontal scaling:

1. Ensure your application is stateless
2. Use a load balancer to distribute traffic
3. Consider containerization and orchestration (e.g., Kubernetes)

## Backup and Disaster Recovery

1. Regularly back up configuration and any persistent data
2. Document the deployment process for quick recovery
3. Consider automated deployment pipelines for consistent deployments
