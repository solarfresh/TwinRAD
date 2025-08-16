# ag2-playground

This repository serves as a learning environment and a hands-on playground for the AG2: Open-Source AgentOS for AI Agents framework.

-----

## Project Structure 📂

Our project is organized to be modular, scalable, and easy to navigate. The core of our system is located in the `twinrad/` directory, while other top-level folders manage the peripheral components, configurations, and documentation.

```
.
├── LICENSE                     # Project license file
├── README.md                   # You are here! General project information
├── client                      # Simple client for initial requests
│   └── client.py
├── configs                     # Configuration files for LLMs, etc.
├── dashboard                   # Streamlit application for real-time monitoring
│   └── app.py
├── server                      # Central Socket.IO communication server
│   └── server.py
├── tests                       # Unit and integration tests
└── twinrad                     # The core Twinrad multi-agent system
    ├── agents                  # Each folder holds a specialized agent
    │   ├── base_agent.py        # Shared logic for all agents
    │   ├── introspection_agent.py # The AG2-level learning agent
    │   ├── prompt_generator.py  # Agent for creating attack prompts
    │   ├── gourmet_agent.py     # The vulnerable target LLM
    │   └── ...
    ├── main.py                 # Main entry point to start the system
    ├── tools                   # Tools the agents can call (e.g., databases)
    │   └── ...
    └── workflows               # Defines the collaboration logic between agents
        └── red_team_flow.py     # Orchestrates the red-teaming process
```

### Key Components Explained

  * **`server/`**: This is the heart of our communication. It's a central **Socket.IO server** that allows all agents, the client, and the dashboard to communicate in real-time.
  * **`twinrad/`**: This is where the magic happens. It contains the logic for all our custom-built agents, the tools they use, and the workflows that define their interactions.
      * **`agents/`**: Each Python file here represents a distinct, specialized agent. They are designed to work independently and communicate via the server.
      * **`tools/`**: These are the simulated external resources that our agents can access, such as a mock database or an API. They are crucial for testing tool-use vulnerabilities.
      * **`workflows/`**: This folder contains the high-level orchestration logic. The `red_team_flow.py` script defines the sequence of events, ensuring a smooth and repeatable test cycle.
  * **`dashboard/`**: The `app.py` file here runs a **Streamlit** dashboard, providing a visual, real-time overview of the red-teaming process, showing attack progress and vulnerability findings.