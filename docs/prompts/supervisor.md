# Prompt: Supervisor Agent

## Purpose

Specification for the Supervisor Agent's system prompt. The Supervisor orchestrates agents and coordinates execution — it does not generate workflow content.

## Inputs

- TODO: Goal and pipeline stage
- TODO: Agent results / handoffs
- TODO: Context (AgentContext)

## Outputs

- TODO: Orchestration decisions
- TODO: Next agent selection / ordering
- TODO: Final assembled workflow (aggregation of agent outputs)

## System Prompt

- TODO: Define role (coordinator only), capabilities, and output format

## Constraints

- TODO: Must not perform business reasoning or content generation
- TODO: Agents communicate only through the orchestrator
- TODO: Must respect token budget (Context Manager owned)
- TODO: No external calls; no database access

## Status

Planned — to be implemented in Phase 6 (Agents).
