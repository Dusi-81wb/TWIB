# ADR-0009 Authentication & Authorization (Hybrid)

## Status

Accepted

## Context

The project documents conflict on how authentication should work:

- `TECH_STACK.md` selects Auth0/Clerk for managed identity and explicitly rejects a
  self-implemented custom JWT as "risk, time".
- `architecture.md` (section 31) shows an interchangeable Identity Provider feeding a
  TWIB-owned **Authentication Service** that issues **JWT + Refresh Token**, with a
  clean separation of authentication from authorization (RBAC).
- `roadmap.md` Phase 2 lists both "Auth provider integration (Auth0/Clerk)" and "JWT
  validation middleware" plus "JWKS caching", alongside session management and API
  keys.
- `PROJECT_STATUS.md` locks "JWT", "OAuth2", and "RBAC".

Phase 2 (Authentication) is the next feature phase. The model must be settled before
implementation so the auth provider adapter, session handling, and RBAC are built
coherently.

## Decision

Adopt a **hybrid model**: a managed Identity Provider (IdP) owns credential security,
and TWIB owns session tokens and authorization.

- **Identity Provider (authentication of credentials):** Auth0 is the initial IdP;
  Clerk is an acceptable alternative. The IdP handles login, registration, SSO
  (Google, GitHub, Azure AD), MFA, password reset, and email verification. IdP
  providers are swappable behind an auth-provider adapter (per ADR-0008, e.g.
  `app/infrastructure/auth/`).
- **TWIB session tokens:** after the IdP authenticates a user, TWIB's
  `AuthenticationService` mints its own short-lived **session JWT** signed with the
  application `SECRET_KEY`, plus an **opaque refresh token** stored in Redis. The IdP
  access token is validated once at login (via OIDC discovery + **JWKS caching**) and
  exchanged for TWIB session tokens. This satisfies architecture.md's
  "JWT + Refresh Token" flow while the IdP keeps charge of credential security.
- **Request validation:** all protected routes validate the TWIB session JWT in
  middleware/dependencies. Refresh tokens rotate on use; web sessions persist across
  browser restarts via `httpOnly` + `Secure` cookies.
- **Authorization (RBAC):** TWIB-owned. Users, organizations, and memberships with
  roles (admin/member/viewer) live in PostgreSQL and are resolved per request by a
  Permission Resolver, separate from authentication (architecture.md section 31/32).
- **API keys:** for programmatic access TWIB issues opaque API keys, hashed at rest,
  with scopes and rotation/revocation support.
- **`SECRET_KEY` becomes mandatory in production** (no empty default) because TWIB
  now signs session JWTs.

## Alternatives Considered

- **Pure managed tokens (validate IdP JWTs directly via JWKS, no TWIB session JWT):**
  simplest and least custom crypto. Rejected because architecture.md explicitly
  requires a TWIB-issued JWT + refresh flow, and roadmap requires session management
  and persistent sessions; a TWIB-scoped session token also carries org/tenant context
  cleanly.
- **Custom JWT only (email/password + self-issued tokens, no IdP):** rejected.
  No SSO/MFA/enterprise compliance, and TECH_STACK flags the security risk.
- **Self-hosted Keycloak:** rejected for operational burden (TECH_STACK).

## Consequences

- Two token layers (IdP login token + TWIB session JWT) must be validated; JWKS
  caching and session-key configuration are required.
- Redis is required for refresh tokens and sessions (already part of the stack).
- `SECRET_KEY` enforcement and key-rotation practices become mandatory in production.
- Auth0/Clerk is a dependency for identity; the provider adapter keeps it swappable.
- Phase 2 deliverables now include: auth provider adapter, session JWT issuance and
  validation, refresh-token rotation, RBAC + permission resolver, API keys, auth
  routes and schemas, and user/organization/membership models, repositories, and
  migrations.
- `architecture.md` and `roadmap.md` wording may be aligned to this decision where
  they imply a purely managed-token model.
