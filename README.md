# Personal Agent

A personal AI productivity system that turns goals into structured plans, stores them in Notion, and supports continuous review and adaptation.

## Vision

This project is an attempt to build a personal AI operating system for:

- decision-making
- planning
- task generation
- memory and tracking
- workflow adaptation over time

The high-level loop is:

**User → Planner → Executor → Memory → Feedback**

In practice, the first version focuses on a much smaller and more realistic scope:

**Goal → Plan → Notion tasks**

---

## Core Idea

The system takes a user goal such as:

> "Prepare my final thesis presentation in 3 weeks"

and transforms it into:

- a structured project
- actionable tasks
- priorities
- optional deadlines
- storage in Notion for tracking

The long-term goal is to make the system increasingly context-aware and capable of helping with execution, but the first milestone is deliberately simple.

---

## MVP Scope

Version 1 will do only the following:

1. Accept a goal as input
2. Generate a structured plan in JSON
3. Validate the planner output
4. Create the project and tasks in Notion

### Explicitly out of scope for v1

To avoid over-engineering, v1 will **not** include:

- autonomous code execution
- multi-agent coordination
- self-improving loops
- advanced memory retrieval
- weekly reflection reports
- event-driven task chaining

These may be added later once the core pipeline is stable.

---

## Architecture

### 1. Planner

The planner is responsible for:

- breaking goals into tasks
- deciding priorities
- returning structured JSON
- following constraints and output rules

Example responsibility:

- convert “Launch a portfolio website” into a project + ordered tasks

### 2. Executor

In the long term, the executor may:

- run code
- call APIs
- automate workflows
- complete machine-executable steps

For v1, this layer is mostly postponed.

### 3. Memory (Notion)

Notion acts as the system memory.

It stores:

- projects
- tasks
- optional logs

This provides persistence, visibility, and manual control.

### 4. Orchestrator

The orchestrator coordinates the system by:

- receiving the goal
- calling the planner
- validating the returned structure
- writing data into Notion

For v1, this is the main application layer.

---

## Proposed Folder Structure

```text
personal-agent/
  README.md
  app/
    planner/
    notion/
    orchestrator/
  prompts/
  schemas/
  tests/
  config/
