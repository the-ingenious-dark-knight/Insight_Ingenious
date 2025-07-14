# Dependency Management Guide

## Overview

This document outlines the dependency management strategy for the Ingenious library, including rationale for dependency choices, update policies, and installation options.

## Installation Options

### Minimal Installation (Default)
```bash
pip install ingenious
```
**Use case**: Basic API functionality with minimal footprint
**Size**: ~15MB (core dependencies only)
**Includes**: FastAPI, dependency injection, structured logging, CLI tools

### Standard Production Installation  
```bash
pip install ingenious[standard]
```
**Use case**: Most common production deployments
**Size**: ~150MB
**Includes**: Core + auth + AI agents + database connectivity

### Full Installation
```bash
pip install ingenious[full]
```
**Use case**: Development and feature-complete deployments
**Size**: ~800MB+
**Includes**: All features including document processing, ML, visualization

## Dependency Groups

### Core Dependencies (Always Installed)

| Package | Version | Rationale |
|---------|---------|-----------|
| `dependency-injector` | 4.48.1 | Provides IoC container for modular architecture |
| `fastapi` | 0.115.9 | Primary web framework, pinned for API stability |
| `jsonpickle` | 4.1.1 | Serialization for complex Python objects |
| `pydantic` | 2.11.5 | Data validation and serialization |
| `structlog` | 25.4.0 | Structured logging for observability |
| `typer` | 0.16.0 | CLI framework for command-line tools |

### Optional Dependencies

#### Core Features (`ingenious[core]`)
- **aiosqlite**: Async SQLite support for local database operations
- **fastapi-cli**: Development server and CLI enhancements
- **jinja2**: Template engine for dynamic content generation
- **python-dotenv**: Environment variable management

#### Authentication (`ingenious[auth]`)
- **bcrypt**: Password hashing for secure authentication
- **passlib**: Password handling utilities
- **python-jose**: JWT token handling for API authentication

#### Azure Cloud (`ingenious[azure]`)
- **azure-core**: Base Azure SDK functionality
- **azure-cosmos**: Cosmos DB integration for document storage
- **azure-identity**: Azure AD authentication
- **azure-keyvault**: Secure credential storage
- **azure-search-documents**: Cognitive Search integration
- **azure-storage-blob**: Blob storage for file management

#### AI & Agents (`ingenious[ai]`)
- **autogen-agentchat**: Multi-agent conversation frameworks
- **autogen-ext[openai]**: OpenAI integration extensions
- **openai**: Official OpenAI API client

#### Database (`ingenious[database]`)
- **pyodbc**: SQL Server and ODBC database connectivity
- **psutil**: System monitoring for database performance

#### Web UI (`ingenious[ui]`)
- **chainlit**: Conversational AI web interface
- **flask**: Web framework for custom endpoints

#### Document Processing (`ingenious[document-processing]`)
- **pymupdf**: PDF text extraction and manipulation
- **azure-ai-documentintelligence**: Advanced document analysis

#### Advanced Document Processing (`ingenious[document-advanced]`)
- **pdfminer.six**: Alternative PDF processing library
- **unstructured[all-docs]**: Comprehensive document parsing

#### Machine Learning (`ingenious[ml]`)
- **chromadb**: Vector database for embeddings
- **sentence-transformers**: Text embedding models

#### Data Preparation (`ingenious[dataprep]`)
- **scrapfly-sdk**: Web scraping capabilities
- **backoff**: Retry logic for external APIs

#### Visualization (`ingenious[visualization]`)
- **matplotlib**: Plotting and chart generation
- **seaborn**: Statistical data visualization

## Version Pinning Strategy

### Exact Pinning (==)
- **Core dependencies**: Pinned to exact versions for stability
- **Critical integrations**: OpenAI, Azure services, FastAPI
- **Security-sensitive**: Authentication and cryptography libraries

### Compatible Pinning (>=)
- **Utility libraries**: Non-breaking updates allowed
- **Development tools**: Latest features beneficial

## Security Policy

### Vulnerability Scanning
- Automated daily scans using `pip-audit`
- Pre-commit hooks prevent vulnerable dependencies
- GitHub Actions workflow for continuous monitoring

### Update Process
1. Automated weekly dependency update PRs
2. Security patches applied within 24 hours
3. Major version updates require manual review
4. Breaking changes documented in CHANGELOG

## Development Dependencies

Development dependencies are managed separately in the `[dependency-groups]` section:

- **Testing**: pytest, pytest-asyncio, pytest-cov, pytest-mock, pytest-timeout
- **Code Quality**: ruff (linting/formatting), vulture (dead code detection)
- **Security**: pip-audit (vulnerability scanning)
- **CI/CD**: pre-commit, twine (package publishing)

## Installation Examples

### Development Setup
```bash
# Install with development dependencies
uv sync --all-extras --dev

# Or with pip
pip install -e ".[full,tests]"
```

### Production Deployments

#### Minimal API Service
```bash
pip install ingenious
```

#### Standard Web Application
```bash
pip install "ingenious[standard,ui]"
```

#### AI Document Processing Service
```bash
pip install "ingenious[standard,document-processing,ml]"
```

#### Full-featured Enterprise Deployment
```bash
pip install "ingenious[full]"
```

## Lock Files

### uv.lock
- Generated by `uv lock`
- Contains exact versions and hashes for all dependencies
- Used for reproducible environments

### requirements.lock
- Generated by `uv export`
- Compatible with standard pip
- Used for Docker builds and legacy systems

## Troubleshooting

### Common Issues

1. **Large Installation Size**
   - Use minimal installation and add specific feature groups
   - Consider containerized deployments for size optimization

2. **Dependency Conflicts**
   - Check compatibility with `uv pip check`
   - Use lock files for consistent environments

3. **Security Vulnerabilities**
   - Run `uv run pip-audit` to scan for issues
   - Update to latest patch versions

### Getting Help

For dependency-related issues:
1. Check this documentation
2. Review GitHub issues for known problems
3. Run dependency analysis tools
4. Contact maintainers for complex conflicts

## Maintenance

This dependency strategy is reviewed quarterly and updated as needed. Major changes are communicated through:
- Release notes
- Breaking change notifications
- Migration guides