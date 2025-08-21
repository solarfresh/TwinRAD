# TwinRAD

This repository implements a multi-agent red teaming framework designed to test the safety and robustness of language models (LMs). The system simulates a controlled adversarial environment where a team of offensive agents actively probes and attacks a target LLM.

-----

## Project Structure 📂

Our project follows PyPA standards with a modern `src/` layout. The system is organized to be modular, scalable, and easy to navigate.

```
.
├── LICENSE                     # Apache License 2.0
├── README.md                   # Project overview and setup guide
├── AGENTS.md                   # AI agent development guidance
├── pyproject.toml              # Modern Python packaging configuration
├── MANIFEST.in                 # Package distribution manifest
├── .env                        # Root shared configuration
├── client/                     # Simple client for initial requests
│   └── client.py
├── server/                     # Socket.IO communication server
│   ├── settings.py             # Server-specific configuration
│   ├── .env                    # Server configuration overrides
│   └── server.py               # Socket.IO server implementation
├── dashboard/                  # Streamlit monitoring dashboard
│   ├── settings.py             # Dashboard-specific configuration
│   ├── .env                    # Dashboard configuration overrides
│   └── app.py                  # Streamlit dashboard application
└── src/twinrad/               # Core TwinRAD multi-agent system
    ├── agents/                 # Specialized AI agents
    │   ├── base_agent.py       # Shared agent logic
    │   ├── evaluator_agent.py  # Safety violation analyzer
    │   ├── gourmet_agent.py    # Target LLM being tested
    │   ├── introspection_agent.py # Learning and strategy agent
    │   ├── planner_agent.py    # Conversation orchestrator
    │   └── prompt_generator.py # Adversarial prompt creator
    ├── configs/                # Core configuration
    │   ├── settings.py         # Core TwinRAD settings
    │   └── logging_config.py   # Logging configuration
    ├── main.py                 # Main entry point
    ├── tools/                  # Agent tools and utilities
    │   ├── reward_tool.py      # Reward system
    │   ├── safety_db_tool.py   # Safety violation database
    │   └── social_media_tool.py # Social media simulation
    └── workflows/              # Agent collaboration logic
        └── red_team_flow.py    # Red team orchestration
```

### Key Components Explained

  * **`src/twinrad/`**: Core multi-agent red teaming framework with isolated configuration
      * **`agents/`**: Specialized AI agents (PromptGenerator, GourmetAgent, EvaluatorAgent, IntrospectionAgent, PlannerAgent)
      * **`configs/`**: Core TwinRAD settings and logging configuration
      * **`tools/`**: Simulated external resources for testing tool-use vulnerabilities
      * **`workflows/`**: High-level orchestration logic for agent interactions
  * **`server/`**: Independent Socket.IO server with its own configuration management
      * Handles real-time communication between agents, client, and dashboard
      * Uses cascading .env configuration (server/.env + root .env)
  * **`dashboard/`**: Independent Streamlit dashboard with isolated settings
      * Real-time monitoring of red teaming process
      * Shows attack progress and vulnerability findings
      * Configurable themes and display options
  * **`client/`**: Simple client utilities for initial requests and testing

-----

## 🚀 Getting Started with Twinrad

This guide will help you set up and run the `twinrad` multi-agent system. This framework is designed to conduct red-teaming exercises by orchestrating a team of specialized AI agents to test the security and safety of a target large language model (LLM).

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.13+**
  * **Git**

### 💻 Installation

1.  **Clone the repository**:
    ```sh
    git clone https://github.com/solarfresh/ag2-playground.git
    cd twinrad
    ```
2.  **Create a virtual environment** (recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the package in development mode**:
    ```sh
    pip install -e .
    ```
    
    Or install requirements directly:
    ```sh
    pip install -r requirements.txt
    ```

### 🛠️ Configuration

The system uses a cascading configuration system with isolated service settings.

1.  **Create a root `.env` file**:
    Create a new file named `.env` in the root directory:
    ```
    LOG_LEVEL=INFO
    TWINKLE_BASE_URL=https://litellm-ekkks8gsocw.dgx-coolify.apmic.ai
    TWINKLE_API_KEY=your_api_key_here
    GOOELG_GENAI_API_KEY=your_api_key_here
    ```
    *Replace `"your_api_key_here"` with your actual API keys.*

2.  **Optional: Service-specific configuration**:
    Each service can have its own `.env` file for overrides:
    ```
    # server/.env (optional)
    SERVER_HOST=0.0.0.0
    SERVER_PORT=5000
    
    # dashboard/.env (optional)
    DASHBOARD_HOST=0.0.0.0
    DASHBOARD_PORT=8501
    THEME=dark
    ```

### ▶️ How to Run the System

The system provides multiple execution methods with independent service configuration.

#### **Method 1: Console Commands (Recommended)**
```sh
# Install in development mode first
pip install -e .

# Run services using console commands
twinrad                  # Main red team workflow
twinrad-server          # Socket.IO server
twinrad-dashboard       # Streamlit dashboard
```

#### **Method 2: Direct Python Execution**
```sh
# Main red team workflow
python src/twinrad/main.py

# Optional: Run services independently
python server/server.py          # Socket.IO server
streamlit run dashboard/app.py    # Streamlit dashboard
```

#### **Method 3: Package Module Execution**
```sh
# Set PYTHONPATH (if needed)
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run as module
python -m twinrad.main
```

### 🧠 System in Action

Once the system is running, you will see a series of log messages in your terminal. This shows the agents communicating in a structured conversation, as defined by the `GroupChat` workflow.

  * The **PromptGenerator** starts the process with a predefined attack.
  * The **GourmetAgent** (the target LLM) responds to the prompt.
  * The **EvaluatorAgent** analyzes the response and sends a diagnostic report.
  * The **IntrospectionAgent** receives the report, learns from it, and provides a strategic recommendation.
  * The **PlannerAgent** uses this recommendation to decide which agent should speak next, potentially giving the floor back to the `PromptGenerator` for a refined attack.

The conversation will continue until a `max_round` limit is reached or the agents decide the task is complete.

### 🔧 Service Independence

Each service can run independently with its own configuration:

- **Core TwinRAD**: Loads `src/twinrad/configs/settings.py` + root `.env`
- **Server**: Loads `server/settings.py` with `server/.env` + root `.env` cascading
- **Dashboard**: Loads `dashboard/settings.py` with `dashboard/.env` + root `.env` cascading

Services can be run from their own directories:
```sh
cd server && python server.py        # Independent server execution
cd dashboard && streamlit run app.py # Independent dashboard execution
```

### 🏗️ Architecture Features

- **Isolated Service Configuration**: Each service has its own settings management
- **Cascading Environment Variables**: Service-specific values override root defaults
- **Smart Import Resolution**: Context-aware imports for both package and direct execution
- **Zero Hardcoded Paths**: Clean Pydantic SettingsConfigDict implementation
- **Runtime Configuration**: Environment variables can override settings at runtime
- **Robust Execution**: Services work from any directory or execution context

---

**Current Version**: [0.2.0](https://github.com/ai-twinkle/TwinRAD/releases/tag/0.2.0) - Import Resolution & Code Quality Release