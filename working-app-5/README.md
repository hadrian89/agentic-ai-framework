# Agentic AI Framework (LangGraph-based)

## Overview

This repository contains a **YAML-driven Agentic AI Framework** built using
**LangChain + LangGraph**, designed for **retail banking use cases**.

The framework enables rapid creation of domain-specific agents (e.g. Payment Agent,
Statement Agent) using a **fixed execution architecture** and **config-only onboarding**.

Key principles:
- One reusable LangGraph for all agents
- YAML-driven goals, prompts, tools, and policies
- Deterministic execution
- Bank-grade governance and auditability
- LLMs used only where safe (planning & summarisation)

---

## Key Concepts

### Agent
An agent represents a **bounded business domain**, such as:
- Payments
- Statements
- Cards
- Loans

Each agent is defined entirely in YAML.

### Goal
A goal is a **specific journey within an agent**, for example:
- `make_payment`
- `schedule_payment`
- `fetch_statement`

Goals define:
- Required slots
- Tool to execute
- Applicable policies

---

## Architecture (High-Level)

- **LangGraph** orchestrates the journey
- **Planner** runs once per journey
- **Execution loop** collects required information
- **Replanner** handles digressions safely
- **Policy Engine** enforces bank rules
- **Tool Executor** calls bank-owned systems (AEM)
- **Responder** produces user-friendly output

The graph itself never changes between agents.

---

## Folder Structure

```text
agentic-ai-framework/
├── agents/
│   ├── payment_agent.yaml
│   └── statement_agent.yaml
│
├── core/
│   ├── agent_loader.py
│   ├── state.py
│   ├── graph.py
│   ├── runtime.py
│   ├── prompt_loader.py
│   ├── exporter.py
│   └── trace.py
│
├── nodes/
│   ├── start.py
│   ├── planner.py
│   ├── execution.py
│   ├── slot_filler.py
│   ├── digression_detector.py
│   ├── replanner.py
│   ├── policy_executor.py
│   ├── tool_executor.py
│   └── responder.py
│
├── policies/
│   ├── registry.py
│   ├── sufficient_balance.py
│   ├── daily_limit.py
│   └── aml.py
│
├── tools/
│   ├── registry.py
│   ├── aem_payment.py
│   └── aem_statement.py
│
├── prompts/
│   ├── payment/
│   │   ├── planner.txt
│   │   ├── clarification.txt
│   │   ├── summary.txt
│   │   └── digression_classifier.txt
│   └── statement/
│       ├── planner.txt
│       └── summary.txt
│
├── main.py
├── requirements.txt
└── README.md


uvicorn api.main:app --reload

curl -X POST "http://localhost:8000/agent/account_assistant/chat" \
-H "Content-Type: application/json" \
-d '{
  "session_id": "abc123",
  "message": "what is my balance?"
}'