# Template_Single_Agent
# Template_Single_Agent

## Overview

**Template_Single_Agent** is a modular Python project designed for building and running single-agent systems, such as conversational AI or automation agents. The project features a clean architecture, separating agent logic, tools, configuration, routing, and data schemas for maintainability and scalability.

## Features

- Modular agent architecture
- Extensible tool system (calculator, search, etc.)
- Persistent memory for chat history
- Configurable environments
- API routing for agent interaction
- Data models for structured information
- Unit tests for reliability

## Installation

### Prerequisites

- Python 3.12 or higher
- [pip](https://pip.pypa.io/en/stable/installation/)
- (Optional) Virtual environment tool (e.g., `venv` or `conda`)

### Steps

1. **Clone the repository:**
	```bash
	git clone https://github.com/BaoBao112233/Template_Single_Agent.git
	cd Template_Single_Agent
	```

2. **Set up a virtual environment (recommended):**
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```

3. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
	Or, if using `pyproject.toml`:
	```bash
	pip install .
	```

4. **Run the application:**
	```bash
	python main.py
	```

## Project Structure

```
main.py                  # Application entry point
pyproject.toml           # Project configuration and dependencies
memories/                # Chat history storage (JSON)
template/
  agent/
	 agent.py             # Core agent logic
	 histories.py         # Agent memory management
	 prompts.py           # Prompt templates for agent
	 tools/
		calculator.py      # Calculator tool for agent
		search.py          # Search tool for agent
		USE_MANUAL.md      # Tool usage manual
  configs/
	 environments.py      # Environment configuration
  router/
	 v1/
		ai.py              # API router for agent
  schemas/
	 model.py             # Data models
	 tweets.py            # Tweet data schema
test_folder/
  test_agent.py          # Unit tests for agent
README.md                # Project documentation
```

## Usage

1. **Start the agent:**
	- Run `main.py` to launch the agent.
	- The agent will use tools defined in `template/agent/tools/` and store chat history in `memories/`.

2. **Extending the agent:**
	- Add new tools in `template/agent/tools/`.
	- Update prompts in `template/agent/prompts.py`.
	- Modify agent logic in `template/agent/agent.py`.

3. **Configuration:**
	- Adjust environment settings in `template/configs/environments.py`.

4. **API Integration:**
	- Use `template/router/v1/ai.py` to expose agent functionality via API routes.

## Code Analysis

### main.py

- Serves as the entry point, initializing the agent and starting the main loop or server.

### template/agent/agent.py

- Implements the core logic for the agent, including decision-making, tool usage, and interaction with memory and prompts.

### template/agent/histories.py

- Manages chat history, enabling the agent to remember previous interactions and maintain context.

### template/agent/prompts.py

- Contains prompt templates and logic for generating agent responses.

### template/agent/tools/

- Houses modular tools (e.g., calculator, search) that the agent can use to perform tasks.

### template/configs/environments.py

- Defines environment variables and configuration settings for different deployment scenarios.

### template/router/v1/ai.py

- Provides API routing, allowing external systems to interact with the agent via HTTP endpoints.

### template/schemas/

- Defines data models for structured information, such as general models (`model.py`) and tweets (`tweets.py`).

### test_folder/test_agent.py

- Contains unit tests to validate agent behavior and ensure code quality.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Submit a pull request.

## License

Specify your license here (e.g., MIT, Apache 2.0).

## Contact

For questions or support, contact [BaoBao112233](mailto:kevinbao15072002@gmail.com).
