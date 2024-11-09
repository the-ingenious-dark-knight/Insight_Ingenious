# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port 80
EXPOSE 80

# Set the working directory
WORKDIR /ingen_app

# Add deadsnakes PPA and install Python 3.12
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo \
        unixodbc \
        unixodbc-dev \
        libodbc2 \
        libodbccr2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy files into the container
COPY dist/ingenious-1.0.0-py3-none-any.whl /ingen_app/ingenious-1.0.0-py3-none-any.whl

# Install dependencies
RUN pip install ./ingenious-1.0.0-py3-none-any.whl[ChatHistorySummariser]

# Expose the package content by copying the installed files to /ingen_app/ingenious
#RUN mkdir -p /ingen_app/ingenious && \
#    cp -r $(pip show -f ingenious | grep 'Location:' | awk '{print $2}')/ingenious/* /ingen_app/ingenious/

# Set the command to run the app
CMD ["ingen_cli"]
