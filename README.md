# CURRENT•SEA

**Explainable ambiguity signals for text, available over MCP and REST.**

CURRENT•SEA is a small, deterministic service that helps AI agents and software
detect wording that may need clarification before acting on it.

It is publicly available as an MCP server:

- **MCP Registry:** `io.github.Bowieboii/current-sea`
- **Current Registry version:** `0.0.3`
- **Remote MCP endpoint:** `https://current-sea.fastapicloud.dev/mcp`
- **MCP tool:** `scan_ambiguity`

Submitted text is processed but **not retained**.

## What it detects

CURRENT•SEA currently looks for several common forms of ambiguous wording,
including:

- vague timing — `soon`, `later`, `eventually`
- vague quantities — `some`, `few`, `many`
- uncertain commitments
- potentially unresolved references — `it`, `them`, `that`
- subjective standards — `reasonable`, `effective`, `good`, `best`

Each signal includes:

- the phrase that triggered it
- its location in the text
- the ambiguity category
- an explanation
- a suggested clarification question

## Example

Input:

```text
Please send it to them soon, include a few examples, and make sure it is good.