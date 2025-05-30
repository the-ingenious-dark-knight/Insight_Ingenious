FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Use uv in copy mode for Docker
ENV UV_LINK_MODE=copy

# Set Python to use system Python by default
ENV UV_SYSTEM_PYTHON=1

# Copy configuration files for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose the application port
EXPOSE 8000

# Run the application with uv
CMD ["./start.sh"]
