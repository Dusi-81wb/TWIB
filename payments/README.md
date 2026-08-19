# Payments

## Purpose

Payment processing integration for subscription billing, usage-based pricing, and invoice management. Integrates with Stripe.

## Responsibilities

- Stripe integration
- Subscription lifecycle
- Usage metering and billing
- Invoice generation
- Webhook handling
- Payment method management
- Dunning management

## What Belongs Here

- Stripe client wrapper
- Billing service
- Webhook handlers
- Price calculation
- Invoice service

## What Must NEVER Belong Here

- Business logic (use services/billing)
- User management
- Workflow execution

## Dependencies

- `stripe` SDK
- `backend.config` - Stripe keys
- `database.repositories` - Subscription persistence

## Future Phases

- Phase 11: Payments implementation