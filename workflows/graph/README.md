# Workflow Graph

## Purpose

Core graph data structures and algorithms for workflow representation including DAG validation, topological sorting, and subgraph operations.

## Responsibilities

- Graph data model (nodes, edges, metadata)
- DAG validation (cycle detection)
- Topological sorting
- Subgraph extraction
- Graph serialization/deserialization
- Visualization export (Mermaid, GraphViz)

## What Belongs Here

- Graph class implementation
- Node/edge data classes
- Traversal algorithms
- Validation logic
- Serialization codecs

## What Must NEVER Belong Here

- Execution logic (use executor/)
- Node implementations (use nodes/)
- Persistence (use database/)

## Dependencies

- `workflows.nodes` - Node types
- `workflows.edges` - Edge types
- Python standard library (collections, itertools)

## Future Phases

- Phase 8: Graph implementation