# TwinRAD

This repository implements a multi-agent red teaming framework designed to test the safety and robustness of large language models (LLMs). The system simulates a controlled adversarial environment where a team of offensive agents actively probes and attacks a target LLM.

## 📖 Table of Contents

  - [Project Overview](https://www.google.com/search?q=%23project-overview)
  - [Agent Guidelines](https://www.google.com/search?q=%23agent-guidelines)
  - [Development Workflow](https://www.google.com/search?q=%23development-workflow)
  - [Architecture](https://www.google.com/search?q=%23architecture)
  - [Examples](https://www.google.com/search?q=%23examples)
  - [Configuration](https://www.google.com/search?q=%23configuration)
  - [Testing](https://www.google.com/search?q=%23testing)
  - [Troubleshooting](https://www.google.com/search?q=%23troubleshooting)
  - [Contributing](https://www.google.com/search?q=%23contributing)
  - [Security Considerations](https://www.google.com/search?q=%23security-considerations)

## Project Overview

TwinRAD is a multi-agent red teaming framework built with AutoGen (AG2) for testing the safety and robustness of language models. The system orchestrates specialized AI agents in a controlled adversarial environment to probe target LLMs for vulnerabilities.

### Purpose

  - **Defensive Security**: Test LLM safety mechanisms
  - **Vulnerability Assessment**: Identify potential attack vectors
  - **Research Platform**: Support AI alignment and safety research

### Scope

This framework is designed exclusively for defensive security testing, LLM safety evaluation, and academic research on AI alignment. **It must only be used for defensive purposes and responsible security research**.

## Agent Guidelines

### General Principles

1.  **Security First**: Always prioritize defensive security applications
2.  **Code Quality**: Follow Python best practices and PEP 8
3.  **Documentation**: Maintain clear, comprehensive documentation
4.  **Testing**: Ensure robust test coverage for all components
5.  **Configuration**: Use isolated service configurations

### Coding Standards

  - Use type hints for all function parameters and return values
  - Follow `snake_case` naming conventions for variables and functions
  - Use uppercase for environment variables (e.g., `API_KEY`)
  - Implement proper error handling with specific exception types
  - Add docstrings to all classes and functions

## Development Workflow

### Environment Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd TwinRAD

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install in development mode
pip install -e .

# Edit .env with your API keys
```

### Running the System

  - **Main red team workflow**: `twinrad`
  - **Socket.IO server**: `twinrad-server`
  - **Streamlit dashboard**: `twinrad-dashboard`

-----

## Architecture

Our project follows PyPA standards with a modern `src/` layout. The system is modular, scalable, and easy to navigate.

### Core Components

```
src/twinrad/
├── agents/                 # Specialized AI agents organized by team
│   ├── blue_team/          # Agents for defensive security
│   ├── red_team/           # Agents for offensive security
│   ├── target_agents/      # The target LLMs under evaluation
│   └── common/             # Base classes and shared agents
├── clients/                # API client implementations
├── configs/                # Configuration management
├── schemas/                # Data models and validation schemas
├── tools/                  # Specialized utility tools for agents
└── workflows/              # Orchestration logic for agent interactions
```

-----

## Examples

### Creating a New Agent

```python
# src/twinrad/agents/my_new_agent.py
from typing import List, Dict, Any, Optional

from twinrad.agents.base_agent import BaseAgent
from twinrad.schemas.agents import AgentName

# ... (rest of the example code from AGENTS.md)
```

### Custom Tool Integration

```python
# src/twinrad/tools/my_custom_tool.py
from typing import Dict, Any, List
import logging

# ... (rest of the example code from AGENTS.md)
```

-----

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `GOOELG_GENAI_API_KEY` | Google Gemini API key | - | Yes |
| `GOOGLE_SEARCH_ENGINE_API_KEY` | Google Custom Search API key | - | No |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Custom Search Engine ID | - | No |
| `TWINKLE_BASE_URL` | Target LLM API endpoint | - | Yes |
| `TWINKLE_API_KEY` | Target LLM API key | - | Yes |

-----

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/twinrad

# Run specific test file
python -m pytest tests/group_chat/test_group_chat.py
```

### Test Structure

```
tests/
└── unit
│   ├── clients
│   │   ├── handlers
│   │   │   ├── test_gemini_handler.py
│   │   │   ├── test_openai_handler.py
│   │   │   └── test_vllm_handler.py
│   │   └── test_client_manager.py
└── group_chat
    └── test_group_chat.py
-----

## Troubleshooting

### Common Issues

  - **Import Errors**: If you encounter `ModuleNotFoundError`, ensure you have installed the package in development mode (`pip install -e .`).
  - **Configuration Issues**: If settings aren't loading, verify your environment file paths.
  - **Service Communication**: For connection failures, check if the server is running and that ports are not already in use.

-----

## Contributing

1.  **Fork** the repository
2.  **Create** a feature branch
3.  **Implement** changes following the guidelines
4.  **Test** thoroughly with `pytest`
5.  **Document** changes
6.  **Submit** a pull request with a clear description

-----

## Security Considerations

  - Never commit API keys or sensitive data to the repository.
  - Use environment variables for all configuration.
  - Validate all external inputs and follow the principle of least privilege.
  - Document security assumptions and requirements.