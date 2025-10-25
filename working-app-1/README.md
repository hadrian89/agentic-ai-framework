# Agentic Starter - Orchestrator + Payments Tool (demo)
Each agent defined with YAML — this lets you register, load, and orchestrate agents dynamically without touching code.
Each agent can specify its model, policies, tools, and prompts.
You can combine YAML agents dynamically (e.g., orchestrator loads only those relevant to a user journey).
Security/policy files (like policies.json) can define approval gates, data handling, etc.
Each YAML can become a node cluster in LangGraph later.

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

```bash
uvicorn tools.payments_service:app --host 0.0.0.0 --port 8001 --reload
```
```bash
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```
```bash

curl -s -X POST "http://127.0.0.1:8000/sessions" -H "Content-Type: application/json" -d '{"agent_id":"payments-agent"}' | jq
```
```bash
# Send message to orchestrator to trigger a payment
curl -s -X POST "http://127.0.0.1:8000/sessions/<SESSION_ID>/message" \
  -H "Content-Type: application/json" \
  -d '{"text":"Please pay 100 GBP to John Doe account 12345678 sort 12-34-56"}' | jq
```

https://app.diagrams.net/#G1SOJ9rx0i2f8Xx4835xWzrxQIU59pL71J#%7B%22pageId%22%3A%22TBJuUtOty8-q1wqX8igo%22%7D