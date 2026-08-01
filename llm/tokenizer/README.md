# LLM Tokenizer

## Purpose

Token counting, estimation, and optimization utilities for managing context windows and controlling costs.

## Responsibilities

- Token counting (exact and estimated)
- Context window management
- Truncation strategies
- Cost estimation
- Token optimization recommendations

## What Belongs Here

- Tokenizer wrappers
- Counting algorithms
- Truncation logic
- Cost calculators

## What Must NEVER Belong Here

- LLM calls
- Business logic
- Database operations

## Dependencies

- `tiktoken` / provider tokenizers
- `llm.providers` - Model token limits

## Future Phases

- Phase 5: Tokenizer utilities