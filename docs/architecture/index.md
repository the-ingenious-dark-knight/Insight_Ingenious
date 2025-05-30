# Architecture Overview

This document provides an overview of the ingenious-slim application architecture.

## System Architecture

ingenious-slim follows a modular architecture designed for flexibility and extensibility. The main components are:

1. **Core Components**: Configuration, logging, and authentication
2. **Agent System**: Base agent classes and agent registry
3. **API Layer**: FastAPI endpoints for interacting with agents
4. **Examples**: Reference implementations and usage examples

## Architecture Diagram

```
+---------------------------+
|     FastAPI Application   |
+---------------------------+
         |        |
         v        v
+----------+  +----------+
|   API    |  |  Agents  |
| Endpoints|  |  Registry|
+----------+  +----------+
      |           |
      v           v
+---------------------------+
|     Agent Implementations |
+---------------------------+
         |
         v
+---------------------------+
|   Azure OpenAI Integration|
+---------------------------+
         |
         v
+---------------------------+
|  Core (Config, Auth, Log) |
+---------------------------+
```

## Main Components

### Core Module

The `core` module provides fundamental services:

- **Configuration**: YAML-based configuration with environment variable support
- **Authentication**: HTTP Basic Authentication for API security
- **Logging**: Structured logging with JSON format option

### Agents Module

The `agents` module handles AI agent functionality:

- **Base Classes**: Abstract base classes for creating agents
- **Registry**: Central registry for managing agent instances
- **Example Agents**: Ready-to-use agent implementations

### API Module

The `api` module provides RESTful endpoints:

- **Health Endpoints**: Application health and status monitoring
- **Agent Endpoints**: Agent management and discovery
- **Chat Endpoints**: Interaction with agents

## Component Details

### Contents

- [Core Components](./core_components.md)
- [Agent System](./agent_system.md)
- [API Layer](./api_layer.md)
- [Integration Points](./integration_points.md)
