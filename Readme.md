# AI Coding Agent

A terminal-based AI coding agent that connects to OpenAI-compatible APIs to help you write, debug, and manage code through natural language.

## Features

- **Interactive TUI** — Rich-powered terminal interface with real-time streaming, reasoning display, and syntax-highlighted file previews
- **File System Tools** — Read, write, edit, glob, grep, list directories, and execute shell commands — all driven by the AI
- **Context Management** — Automatic message pruning when approaching token limits, keeping conversations under the model's context window
- **Usage Tracking** — Built-in token usage tracking (`/usage` command)
- **Streaming Responses** — Real-time streaming of both reasoning and text responses
- **Error Resilience** — Automatic retry on rate limits, connection errors, and timeouts

## Requirements

- Python 3.10+
- An API key for an OpenAI-compatible API provider

## Setup

```bash
# Clone and enter the project
git clone <repo-url> && cd ai-coding-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure your API credentials
# Edit .env file:
#   API_KEY="your-api-key"
#   BASE_URL="https://api.your-provider.com/v1"
```

## Usage

```bash
python main.py
```

### Commands

| Command | Description |
|---------|-------------|
| `exit` | Exit the agent |
| `/usage` | Show token usage for the session |
| `/messages` | Debug: print all non-system messages |

The agent supports natural language conversations. Ask it to read files, write code, search the codebase, or execute shell commands.


Developed by ❤️ with Jarair Khan
