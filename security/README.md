# Security

## Purpose

Security utilities and cross-cutting security concerns including encryption, secrets management, input sanitization, and compliance helpers.

## Responsibilities

- Encryption/decryption utilities
- Secrets management integration
- Input validation/sanitization
- PII detection/redaction
- Audit logging
- Compliance helpers (GDPR, SOC2)
- Security headers

## What Belongs Here

- Crypto utilities
- Secrets client
- Sanitization functions
- Audit logger
- Compliance checklists

## What Must NEVER Belong Here

- Business logic
- Authentication logic (use auth/)
- Database operations

## Dependencies

- `cryptography` library
- `hashicorp-vault` / AWS Secrets Manager SDK
- `backend.config` - Security settings

## Future Phases

- Phase 1: Security utilities
- Phase 14: Production hardening