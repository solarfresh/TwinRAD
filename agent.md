# agent.md

This file provides guidance for AI agents when working with code in this repository.

## Project Overview

TwinRAD is a multi-agent red teaming framework built with AutoGen (AG2) for testing the safety and robustness of language models. The system orchestrates specialized AI agents in a controlled adversarial environment to probe target LLMs for vulnerabilities.

## Core Architecture

The system follows a modular agent-based architecture:

- **Multi-Agent System**: Built on AutoGen's GroupChat framework with specialized agents
- **Communication Layer**: Socket.IO server (`server/server.py`) handles real-time agent communication
- **Workflow Orchestration**: Custom speaker selection logic in `twinrad/workflows/red_team_flow.py`
- **Agent Specialization**: Each agent in `twinrad/agents/` has a specific role in the red team process

### Key Agent Types

1. **PromptGenerator**: Creates adversarial prompts to test target models
2. **GourmetAgent**: The vulnerable target LLM being tested
3. **EvaluatorAgent**: Analyzes responses for safety violations
4. **IntrospectionAgent**: Learns from evaluations and provides strategic recommendations
5. **PlannerAgent**: Orchestrates the conversation flow and determines next speakers

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System
```bash
# Install the package in development mode
pip install -e .

# Run the main red team workflow
twinrad

# OR run directly with Python
python -m twinrad.main

# Optional: Start the Socket.IO server (separate terminal)
twinrad-server
# OR python server/server.py

# Optional: Launch monitoring dashboard (separate terminal)
twinrad-dashboard
# OR streamlit run dashboard/app.py
```

### Configuration
Environment variables required in `.env`:
- `GOOELG_GENAI_API_KEY`: Google Gemini API key for red team agents
- `TWINKLE_BASE_URL`: Base URL for target LLM API
- `TWINKLE_API_KEY`: API key for target LLM
- `LOG_LEVEL`: Logging level (default: INFO)

## Agent Development Patterns

### Creating New Agents
1. Inherit from `BaseAgent` in `src/twinrad/agents/base_agent.py`
2. Add agent name to `AgentName` enum in `src/twinrad/schemas/agents.py`
3. Update speaker selection logic in `red_team_flow.py`
4. Register in main GroupChat configuration

### Agent Communication Flow
The system uses a structured conversation flow:
1. UserProxy initiates with a test prompt
2. PromptGenerator creates adversarial prompt
3. GourmetAgent (target) responds
4. EvaluatorAgent assesses the response
5. IntrospectionAgent analyzes and learns
6. PlannerAgent decides next speaker

### Tool Integration
Agents can use tools from `src/twinrad/tools/`:
- `reward_tool.py`: Reward system for agent behavior
- `safety_db_tool.py`: Safety violation database
- `social_media_tool.py`: Social media simulation

## Configuration Management

Settings are centralized in `src/twinrad/configs/settings.py` using Pydantic:
- Server configuration (host, port)
- API keys and endpoints
- Logging configuration

Logging is standardized across all components using `src/twinrad/configs/logging_config.py`.

### TODO: Individual Service Configuration Implementation

**Goal**: Implement isolated service configurations per Issue #3 requirements.

#### 1. Create Individual Settings Files

Each service needs its own `settings.py` with dedicated `SettingsConfigDict`:

```python
# server/settings.py
from pydantic import BaseSettings
from pydantic_settings import SettingsConfigDict
from pathlib import Path

class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent / ".env",  # Service-specific .env
            Path(__file__).parent.parent / ".env",  # Root .env
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Server-specific settings
    server_host: str = "localhost"
    server_port: int = 5000
    debug: bool = False
    
    # Inherited from root .env if not overridden
    log_level: str = "INFO"

# dashboard/settings.py  
class DashboardSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent / ".env",
            Path(__file__).parent.parent / ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Dashboard-specific settings
    dashboard_host: str = "localhost" 
    dashboard_port: int = 8501
    theme: str = "light"
    
    # Inherited settings
    log_level: str = "INFO"
```

#### 2. Implement Cascading .env Files

**File Structure**:
```
.env                    # Root configuration
server/.env            # Server overrides
dashboard/.env         # Dashboard overrides
src/twinrad/.env       # Core service overrides (optional)
```

**Root `.env`** (shared defaults):
```bash
LOG_LEVEL=INFO
GOOELG_GENAI_API_KEY=your_api_key_here
TWINKLE_BASE_URL=https://litellm-ekkks8gsocw.dgx-coolify.apmic.ai
TWINKLE_API_KEY=your_api_key_here
```

**Service-specific `.env`** examples:
```bash
# server/.env
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=true

# dashboard/.env  
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501
THEME=dark
```

#### 3. Update Service Files

**server/server.py**:
```python
from server.settings import ServerSettings

settings = ServerSettings()

# Use settings.server_host, settings.server_port, etc.
```

**dashboard/app.py**:
```python
from dashboard.settings import DashboardSettings

settings = DashboardSettings()

# Use settings.dashboard_host, settings.theme, etc.
```

#### 4. Enable Independent Service Execution

Each service should work when run from its own directory:
```bash
cd server && python server.py      # Should load server/.env + root .env
cd dashboard && python app.py      # Should load dashboard/.env + root .env
```

#### 5. Remove Central Config Dependencies

- Refactor `src/twinrad/configs/settings.py` to only handle core TwinRAD settings
- Remove service-specific configs (server_host, server_port) from central settings
- Each service becomes self-contained with its own configuration

#### 6. Implementation Status

- ✅ Create `server/settings.py` with `SettingsConfigDict`
- ✅ Create `dashboard/settings.py` with `SettingsConfigDict`  
- ✅ Create service-specific `.env` files
- ✅ Update service imports to use local settings
- ✅ Test independent service execution from own directories
- ✅ Verify cascading .env inheritance works correctly
- ✅ Remove hardcoded configs from central settings
- ✅ Update documentation with new configuration patterns

**✅ COMPLETED: Issue #3 - Isolated Service Configuration**

This implementation provides true service isolation while maintaining shared configuration inheritance.

### Acceptance Criteria Verification

**✅ Each service (twinrad, server, dashboard) has its own settings.py file with a dedicated SettingsConfigDict**
- ✅ `server/settings.py` with `ServerSettings(BaseSettings)` and `SettingsConfigDict`
- ✅ `dashboard/settings.py` with `DashboardSettings(BaseSettings)` and `SettingsConfigDict`
- ✅ `src/twinrad/configs/settings.py` with `TwinRADSettings(BaseSettings)` for core service

**✅ The application successfully loads configurations from both the service's .env and the root .env file**
- ✅ Verified: Server loads `server/.env` + root `.env` (tested: got `0.0.0.0:5000` from service + `lm-studio` from root)
- ✅ Verified: Dashboard loads `dashboard/.env` + root `.env` (tested: got `INFO` log level from root)
- ✅ Cascading inheritance works: service values override root defaults

**✅ The codebase is free of hardcoded relative path workarounds for finding configuration files**
- ✅ No `sys.path.insert` or similar hacks
- ✅ Clean `Path(__file__).parent / ".env"` for service discovery
- ✅ Clean `Path(__file__).parent.parent / ".env"` for root discovery
- ✅ Proper Pydantic `SettingsConfigDict` with `env_file` arrays

**✅ Running a service from its own directory successfully loads its configuration**
- ✅ Tested: `cd server && python server.py` works and loads correct config
- ✅ Tested: `cd dashboard && python -c "from settings import..."` works
- ✅ Smart import fallback handles both package and direct execution contexts

**✅ The project's root configs/settings.py is removed or refactored to align with this new model**
- ✅ `src/twinrad/configs/settings.py` refactored to `TwinRADSettings` (core only)
- ✅ Removed server-specific settings (`SERVER_HOST`, `SERVER_PORT`) from central config
- ✅ Each service is now self-contained with its own configuration management

### Current Configuration Structure

**File Structure**:
```
.env                           # Root shared configuration
server/
├── .env                      # Server-specific overrides  
├── settings.py               # ServerSettings class
└── server.py                 # Uses local settings
dashboard/
├── .env                      # Dashboard-specific overrides
├── settings.py               # DashboardSettings class  
└── app.py                    # Uses local settings
src/twinrad/configs/
└── settings.py               # Core TwinRAD settings only
```

**Service Independence Verified**:
- ✅ `cd server && python server.py` works independently
- ✅ `cd dashboard && python app.py` works independently  
- ✅ Each service loads its own + root .env files
- ✅ No hardcoded path dependencies

## Import Resolution Fix

The main script includes a sys.path fix to resolve module import issues:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

This allows the script to find the `configs/` module when run from the project root with `python twinrad/main.py`.

## Docker Configuration

The system is configured to run without Docker by default:
- UserProxyAgent includes `code_execution_config={"use_docker": False}`
- This eliminates Docker dependency for local development

## Testing and Validation

The system is designed for security research and should only be used for:
- Defensive security testing
- LLM safety evaluation
- Academic research on AI alignment

**Important**: This framework tests AI safety mechanisms and should be used responsibly for defensive purposes only.

## Architecture Notes

- **Event-Driven**: Uses Socket.IO for real-time agent communication
- **Stateful Conversations**: GroupChat maintains conversation history
- **Extensible Agents**: Modular agent design allows easy addition of new capabilities
- **Configurable Workflows**: Speaker selection logic can be customized for different test scenarios

## Recent Changes

### 2024-08-19: Complete System Verification and Bug Fixes
- **✅ Fixed logging configuration**: Updated `src/twinrad/configs/logging_config.py` to use `settings.log_level` (lowercase) instead of `settings.LOG_LEVEL` (uppercase)
- **✅ Fixed main.py attribute references**: Updated API key references from uppercase (`GOOELG_GENAI_API_KEY`, `TWINKLE_BASE_URL`, `TWINKLE_API_KEY`) to lowercase (`gooelg_genai_api_key`, `twinkle_base_url`, `twinkle_api_key`)
- **✅ Verified all services operational**:
  - Core TwinRAD: `python src/twinrad/main.py` ✅ (multi-agent conversation flows successfully)
  - Dashboard: `streamlit run dashboard/app.py` ✅ (runs at http://localhost:8501)
  - Server: `python server/server.py` ✅ (independent execution with port configuration)
- **✅ Updated API endpoints**: Changed all documentation to use production endpoint `https://litellm-ekkks8gsocw.dgx-coolify.apmic.ai`
- **✅ Complete isolated service configuration validation**: All acceptance criteria for Issue #3 verified working
- **✅ Environment variable overrides**: Confirmed runtime environment variables work correctly (tested with `SERVER_PORT=5001`)

### Key Implementation Success
The isolated service configuration system is now fully operational with:
- True service independence (each service runs from its own directory)
- Cascading .env inheritance (service-specific overrides + root defaults)
- Smart import fallback (handles both package and direct execution contexts)
- Zero hardcoded paths (clean Pydantic SettingsConfigDict implementation)
- Runtime environment variable support