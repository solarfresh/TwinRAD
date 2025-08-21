# AGENTS.md

This document provides comprehensive guidance for AI agents working with the TwinRAD codebase.

## Table of Contents

- [Project Overview](#project-overview)
- [Agent Guidelines](#agent-guidelines)
- [Development Workflow](#development-workflow)
- [Architecture](#architecture)
- [Examples](#examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Project Overview

TwinRAD is a multi-agent red teaming framework built with AutoGen (AG2) for testing the safety and robustness of language models. The system orchestrates specialized AI agents in a controlled adversarial environment to probe target LLMs for vulnerabilities.

### Purpose
- **Defensive Security**: Test LLM safety mechanisms
- **Vulnerability Assessment**: Identify potential attack vectors
- **Research Platform**: Support AI alignment and safety research

### Scope
This framework is designed exclusively for:
- Defensive security testing
- LLM safety evaluation  
- Academic research on AI alignment

**⚠️ Important**: This framework must only be used for defensive purposes and responsible security research.

## Agent Guidelines

### General Principles

1. **Security First**: Always prioritize defensive security applications
2. **Code Quality**: Follow Python best practices and PEP 8
3. **Documentation**: Maintain clear, comprehensive documentation
4. **Testing**: Ensure robust test coverage for all components
5. **Configuration**: Use isolated service configurations

### Coding Standards

- Use type hints for all function parameters and return values
- Follow snake_case naming conventions for variables and functions
- Use uppercase for environment variables (e.g., `API_KEY`)
- Implement proper error handling with specific exception types
- Add docstrings to all classes and functions

### Security Guidelines

- Never commit API keys or sensitive data to the repository
- Use environment variables for all configuration
- Implement proper input validation for all user inputs
- Follow principle of least privilege for system access
- Validate and sanitize all external data sources

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

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file in the project root:

```bash
# Root shared configuration
LOG_LEVEL=INFO
GOOELG_GENAI_API_KEY=your_google_api_key_here
TWINKLE_BASE_URL=https://litellm-ekkks8gsocw.dgx-coolify.apmic.ai
TWINKLE_API_KEY=your_api_key_here
```

Optional service-specific configurations:

```bash
# server/.env
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=false

# dashboard/.env  
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501
THEME=dark
```

### Running the System

```bash
# Main red team workflow
twinrad

# Alternative execution methods
python -m twinrad.main
python src/twinrad/main.py

# Optional services (separate terminals)
twinrad-server          # Socket.IO server
twinrad-dashboard       # Streamlit dashboard
```

## Architecture

### Core Components

```
src/twinrad/
├── agents/                 # Specialized AI agents
│   ├── base_agent.py      # Base agent class
│   ├── prompt_generator.py # Adversarial prompt creation
│   ├── gourmet_agent.py   # Target LLM being tested
│   ├── evaluator_agent.py # Safety violation analysis
│   ├── introspection_agent.py # Learning and strategy
│   └── planner_agent.py   # Conversation orchestration
├── configs/               # Configuration management
│   ├── settings.py        # Core TwinRAD settings
│   └── logging_config.py  # Logging configuration
├── tools/                 # Agent utilities
│   ├── reward_tool.py     # Reward system
│   ├── safety_db_tool.py  # Safety violation database
│   └── social_media_tool.py # Social media simulation
└── workflows/             # Orchestration logic
    └── red_team_flow.py   # Red team conversation flow
```

### Agent Types

1. **PromptGenerator**: Creates adversarial prompts to test target models
2. **GourmetAgent**: The vulnerable target LLM being tested
3. **EvaluatorAgent**: Analyzes responses for safety violations
4. **IntrospectionAgent**: Learns from evaluations and provides strategic recommendations
5. **PlannerAgent**: Orchestrates the conversation flow and determines next speakers

### Communication Flow

```
UserProxy → PromptGenerator → GourmetAgent → EvaluatorAgent → IntrospectionAgent → PlannerAgent
    ↑                                                                                      ↓
    └──────────────────────── Conversation Loop ─────────────────────────────────────────┘
```

## Examples

### Creating a New Agent

```python
# src/twinrad/agents/my_new_agent.py
from typing import List, Dict, Any, Optional
from autogen import ConversableAgent

from twinrad.agents.base_agent import BaseAgent
from twinrad.schemas.agents import AgentName


class MyNewAgent(BaseAgent):
    """
    Custom agent for specific red team functionality.
    
    This agent demonstrates the pattern for creating new specialized agents
    within the TwinRAD framework.
    """
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the custom agent.
        
        Args:
            llm_config: Configuration for the underlying LLM
            **kwargs: Additional configuration parameters
        """
        super().__init__(
            name="MyNewAgent",
            system_message=self._get_system_message(),
            llm_config=llm_config,
            **kwargs
        )
        self.logger.info("Agent 'MyNewAgent' initialized.")
    
    def _get_system_message(self) -> str:
        """Define the agent's role and behavior."""
        return """
        You are a specialized agent in the TwinRAD red teaming framework.
        Your role is to [specific responsibility].
        
        Guidelines:
        - Follow defensive security principles
        - Provide clear, actionable analysis
        - Maintain conversation context
        """
    
    def process_message(self, message: str, sender: str) -> str:
        """
        Process incoming messages and generate responses.
        
        Args:
            message: The incoming message content
            sender: The name of the sending agent
            
        Returns:
            Generated response string
        """
        # Implement custom logic here
        response = f"Processed message from {sender}: {message}"
        self.logger.info(f"Generated response: {response}")
        return response
```

### Registering a New Agent

```python
# src/twinrad/schemas/agents.py
from enum import Enum

class AgentName(Enum):
    """Enumeration of all available agent names."""
    PROMPT_GENERATOR = "PromptGenerator"
    GOURMET_AGENT = "GourmetAgent"
    EVALUATOR_AGENT = "EvaluatorAgent"
    INTROSPECTION_AGENT = "IntrospectionAgent"
    PLANNER_AGENT = "PlannerAgent"
    MY_NEW_AGENT = "MyNewAgent"  # Add your new agent here
```

```python
# src/twinrad/main.py - Add to GroupChat configuration
from twinrad.agents.my_new_agent import MyNewAgent

# Instantiate your new agent
my_new_agent = MyNewAgent(llm_config=red_team_llm_config)

# Add to GroupChat
group_chat = GroupChat(
    agents=[
        user_proxy,
        evaluator_agent,
        gourmet_agent,
        introspection_agent,
        planner_agent,
        prompt_generator,
        my_new_agent,  # Include your new agent
    ],
    messages=[],
    max_round=20,
    speaker_selection_method=speaker_selection_func
)
```

### Custom Tool Integration

```python
# src/twinrad/tools/my_custom_tool.py
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def my_custom_tool(input_data: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom tool for agent use.
    
    Args:
        input_data: Input string to process
        config: Tool configuration parameters
        
    Returns:
        Tool execution results
    """
    try:
        # Implement your tool logic here
        result = {
            "success": True,
            "data": f"Processed: {input_data}",
            "metadata": {
                "tool": "my_custom_tool",
                "version": "1.0.0"
            }
        }
        logger.info(f"Tool executed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


# Tool registration for agent use
def register_tool():
    """Register tool with the agent framework."""
    return {
        "name": "my_custom_tool",
        "description": "Custom tool for specific functionality",
        "function": my_custom_tool,
        "parameters": {
            "input_data": "String input for processing",
            "config": "Configuration dictionary"
        }
    }
```

### Service Configuration

```python
# server/settings.py - Service-specific configuration
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


def find_project_root(start_path: Path) -> Path:
    """Find project root using .git or pyproject.toml markers."""
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / ".git").is_dir() or (current_path / "pyproject.toml").is_file():
            return current_path
        current_path = current_path.parent
    return start_path.resolve()


def get_env_files() -> list[Path]:
    """Get validated environment files."""
    service_env = Path(__file__).parent / ".env"
    root_env = find_project_root(Path(__file__)) / ".env"
    
    env_files = []
    if service_env.exists():
        env_files.append(service_env)
    if root_env.exists():
        env_files.append(root_env)
    
    return env_files


class ServerSettings(BaseSettings):
    """Socket.IO server configuration."""
    
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Server-specific settings
    server_host: str = "localhost"
    server_port: int = 5000
    debug: bool = False
    
    # Inherited settings
    log_level: str = "INFO"
    gooelg_genai_api_key: str = ""
    twinkle_base_url: str = ""
    twinkle_api_key: str = ""
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `GOOELG_GENAI_API_KEY` | Google Gemini API key | - | Yes |
| `TWINKLE_BASE_URL` | Target LLM API endpoint | - | Yes |
| `TWINKLE_API_KEY` | Target LLM API key | - | Yes |
| `SERVER_HOST` | Server bind address | `localhost` | No |
| `SERVER_PORT` | Server port | `5000` | No |
| `DASHBOARD_HOST` | Dashboard bind address | `localhost` | No |
| `DASHBOARD_PORT` | Dashboard port | `8501` | No |

### Service Independence

Each service (core, server, dashboard) operates independently with:

- **Isolated Configuration**: Own `settings.py` with `SettingsConfigDict`
- **Cascading Environment**: Service `.env` + root `.env` inheritance
- **Independent Execution**: Can run from own directory
- **Robust Path Detection**: Dynamic project root discovery
- **Smart Import Resolution**: Context-aware imports for both package and direct execution

#### Smart Import Pattern

Services use intelligent import resolution to work in both contexts:

```python
# Smart import: Use relative import when running directly, absolute when installed
if __package__ is None:
    # Direct execution (python server.py)
    from settings import ServerSettings
else:
    # Package execution (python -m server.server or installed package)
    from server.settings import ServerSettings
```

This pattern:
- ✅ **Eliminates try/except anti-patterns**: Clean, predictable import logic
- ✅ **Works in all contexts**: Package execution and direct script execution
- ✅ **Maintains code quality**: No temporary workarounds or import hacks
- ✅ **Zero configuration**: Automatically detects execution context

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/twinrad

# Run specific test file
python -m pytest tests/test_agents.py

# Run with verbose output
python -m pytest -v
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration
├── test_agents/             # Agent-specific tests
│   ├── test_base_agent.py
│   ├── test_prompt_generator.py
│   └── test_evaluator_agent.py
├── test_configs/            # Configuration tests
│   ├── test_settings.py
│   └── test_logging.py
└── test_integration/        # Integration tests
    ├── test_workflow.py
    └── test_communication.py
```

### Test Example

```python
# tests/test_agents/test_my_new_agent.py
import pytest
from unittest.mock import Mock, patch

from twinrad.agents.my_new_agent import MyNewAgent


class TestMyNewAgent:
    """Test suite for MyNewAgent."""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = MyNewAgent()
        assert agent.name == "MyNewAgent"
        assert agent.system_message is not None
    
    def test_message_processing(self):
        """Test message processing functionality."""
        agent = MyNewAgent()
        result = agent.process_message("test message", "TestSender")
        assert "TestSender" in result
        assert "test message" in result
    
    @patch('twinrad.agents.my_new_agent.logger')
    def test_logging(self, mock_logger):
        """Test logging functionality."""
        agent = MyNewAgent()
        agent.process_message("test", "sender")
        mock_logger.info.assert_called()
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Install in development mode
pip install -e .

# Verify installation
python -c "import twinrad; print('✅ TwinRAD imported successfully')"

# Problem: Service import errors when running directly
# Solution: Use smart import pattern (automatically handled)
# Services use __package__ detection for context-aware imports
```

#### Configuration Issues
```bash
# Problem: Settings not loading
# Solution: Check environment file paths
python -c "
from server.settings import ServerSettings
settings = ServerSettings()
print(f'Config loaded: {settings.server_host}:{settings.server_port}')
"
```

#### Service Communication
```bash
# Problem: Socket.IO connection failed
# Solution: Verify server is running
python server/server.py &
python -c "
import socketio
sio = socketio.Client()
sio.connect('http://localhost:5000')
print('✅ Server connection successful')
"

# Problem: Port already in use
# Solution: Use different port or kill existing process
SERVER_PORT=5001 python server/server.py
# OR: lsof -ti:5000 | xargs kill -9
```

### Debug Mode

Enable debug logging:

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with debug output
twinrad
```

### Validation Commands

```bash
# Test all services
python -c "
from src.twinrad.configs.settings import TwinRADSettings
from server.settings import ServerSettings
from dashboard.settings import DashboardSettings

print('🧪 Configuration Test')
print('✅ Core:', TwinRADSettings().log_level)
print('✅ Server:', ServerSettings().server_port)
print('✅ Dashboard:', DashboardSettings().dashboard_port)
print('🎉 All services configured correctly')
"
```

## Contributing

### Development Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** changes following these guidelines
4. **Test** thoroughly with pytest
5. **Document** changes in appropriate files
6. **Submit** pull request with clear description

### Code Review Checklist

- [ ] Follows coding standards and conventions
- [ ] Includes comprehensive tests
- [ ] Updates relevant documentation
- [ ] Handles errors gracefully
- [ ] Uses proper logging
- [ ] Follows security best practices
- [ ] Configuration is properly isolated

### Security Considerations

- Never commit sensitive data (API keys, credentials)
- Validate all external inputs
- Use environment variables for configuration
- Follow principle of least privilege
- Document security assumptions and requirements

---

**Last Updated**: 2024-08-21  
**Version**: [0.1.0](https://github.com/ai-twinkle/TwinRAD/releases/tag/0.1.0)  
**Maintainers**: TwinRAD Development Team