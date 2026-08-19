# Architecture Decision Records (ADR)

## Purpose

Capture and preserve significant architectural decisions made during TWIB development.

## Responsibilities

- Record architectural decisions in a lightweight, versioned format
- Provide context and rationale behind each decision
- Enable future contributors to understand *why* the architecture is the way it is
- Provide a review trail for architecture evolution

## What Belongs Here

- One numbered ADR file per architectural decision (`NNNN-title.md`)
- Decisions affecting structure, layers, interfaces, or dependencies
- Superseded ADRs (marked with new status)

## What Must NEVER Belong Here

- Implementation details or code
- Business logic
- Routine, non-architectural changes
- Documentation not tied to a specific decision

## Dependencies

- `docs/architecture.md` — source of truth for the current architecture
- `docs/PROJECT_RULES.md` — mandates ADR updates on architectural changes

## Future Phases

- New ADRs as Phase 1+ introduces foundational decisions
- Supersede/amend ADRs as architecture evolves
