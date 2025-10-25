# Agentic Starter - Orchestrator + Payments Tool (demo)
### How it works now

UserInputNode inspects the goal and asks for any missing fields interactively.

PlannerNode checks if all required fields are present. If not → waits for user input.

ExecutionNode only runs when the plan is fully ready.

MonitorNode + ReplannerNode handle success/failure as before.

### Features
Fully interactive: prompts user for missing data in natural language.

Goal evaluation: ensures all required fields are collected before execution.

Dynamic multi-agent orchestration: loads agents from YAML files.

Conditional execution: only executes if goals are satisfied.

Replanning support: retries if execution fails.

## Prereqs
- Python 3.10+ (venv recommended)
- git

## Install and run locally

1. Create venv & install
```bash
python -m venv venv
source venv/bin/activate      # mac/linux
# .\venv\Scripts\activate     # windows
pip install -r requirements.txt

pip install pyyaml
# If you plan to use Ollama, also install the ollama client package per its instructions.
python main.py

```
