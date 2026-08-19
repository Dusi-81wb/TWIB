# Workflow Templates

## Purpose

Pre-built, reusable workflow templates for common business patterns. Templates are parameterized workflow graphs that can be instantiated with specific configurations.

## Responsibilities

- Template registry
- Template definitions (YAML/JSON + code)
- Parameter validation
- Template versioning
- Category organization
- Import/export functionality

## What Belongs Here

- Template base class
- Built-in templates (Approval, ETL, Notification, etc.)
- Template schema
- Parameter definitions
- Template metadata

## What Must NEVER Belong Here

- Execution logic (use executor/)
- Node/edge implementations
- Custom workflow storage (use database/)

## Dependencies

- `workflows.graph` - Graph structures
- `workflows.nodes` - Node types
- `workflows.edges` - Edge types
- `database.repositories` - Template persistence

## Future Phases

- Phase 8: Template system