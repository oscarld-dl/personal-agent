# Personal Agent

## Outlooks

1. Add files such as PDF and PPT documents to a specific task, and update that same task's notes through the API with a command shaped like:

```bash
python -m app.orchestrator.main "Attach the PDF /path/to/file.pdf to the specific task X and update its notes with Y"
```

A personal AI productivity system that turns goals into structured plans, validates them, and stores them in Notion.

## Current Status

The project already supports a first working end-to-end flow:

**Goal input → Planner → JSON plan → Schema validation → Notion mapping → Notion storage**

At the moment, the system can:

- accept a goal from the command line
- generate a structured project plan
- validate the plan against a JSON schema
- map the plan into Notion-compatible properties
- create project entries in Notion
- partially create task entries in Notion, with ongoing schema alignment

---

## Vision

The long-term goal is to build a personal AI operating system for:

- planning
- decision-making
- memory and logging
- task tracking
- workflow adaptation
- daily and weekly work journaling

High-level concept:

**User → Planner → Executor → Memory → Feedback**

The current implementation focuses on the first realistic milestone:

**Goal → Structured plan → Notion**

---

## MVP Goal

The first milestone of the project is:

**Take a user goal and turn it into a structured set of tasks stored in Notion.**

This project is being built incrementally to avoid over-engineering.

---

## What Is Already Implemented

### 1. Planner layer
The planner takes a goal and produces structured JSON.

Current planner modes:
- `mock` planner for deterministic local testing
- `openai` planner for real model-generated plans

Planner selection is controlled through configuration.

---

### 2. Prompt-based planning
The planning behavior is defined in:

```text
prompts/planner_prompt.md
