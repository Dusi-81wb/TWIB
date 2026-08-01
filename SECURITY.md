# Security Policy

## Supported Versions

TWIB is currently in active development. Security updates are provided for the latest release only.

| Version | Supported          |
|---------|--------------------|
| Latest  | ✅ Yes             |
| < Latest| ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. Please report vulnerabilities privately.

### Reporting Process

1. **Do NOT** report vulnerabilities publicly (issues, PRs, forums)
2. **Email**: `security@twib.io`
3. **Alternative**: Use GitHub private security advisories:
   - Navigate to the repository
   - Go to **Security** tab
   - Click **Report a vulnerability**

### What to Include

When reporting, please provide:

- **Component**: Affected module/file
- **Vulnerability type**: XSS, SQL injection, RCE, auth bypass, etc.
- **Severity estimate**: Critical, High, Medium, Low
- **Reproduction steps**: Detailed, with environment
- **Impact**: What an attacker could do
- **Suggested fix** (optional)

### Response Timeline

| Phase | Timeframe |
|-------|-----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix for critical issues | Within 7 days |
| Fix for high issues | Within 14 days |
| Fix for medium/low | Within 30 days |
| Public disclosure | After fix + 30 days grace |

### Disclosure Policy

- We disclose after a fix is available and verified
- We provide 30-day grace period for users to update
- Reporter credited (unless anonymity requested)

## Security Best Practices

### For Developers

- **Never commit secrets** - API keys, passwords, tokens
- **Use environment variables** for all configuration
- **Follow the coding guidelines** for security-sensitive code
- **Validate all inputs** - Pydantic schemas, sanitization
- **Use parameterized queries** via ORM/repositories
- **Handle errors gracefully** - no stack traces in responses
- **Rate limit** all endpoints, especially auth

### Dependency Security

- Run `pip-audit` and `safety check` for Python deps
- Run `npm audit` for Node deps
- Update dependencies regularly (Dependabot/Renovate)
- Review dependency licenses

## Security Features

TWIB implements:

- **JWT authentication** with JWKS validation
- **Role-based access control** (RBAC)
- **Input validation** via Pydantic
- **CORS** restrictions
- **Rate limiting**
- **Encryption at rest** (database, storage)
- **Encryption in transit** (TLS/HTTPS)
- **Audit logging** for sensitive operations
- **PII redaction** in logs
- **Secret management** via Vault/Secrets Manager

## Incident Response

### Severity Levels

| Level | Definition | Example |
|-------|------------|---------|
| Critical | Full compromise, data breach, RCE | Unauthenticated RCE |
| High | Significant impact, limited scope | Auth bypass, SQLi |
| Medium | Moderate impact, requires conditions | Stored XSS, DoS |
| Low | Minor impact, low risk | Minor info disclosure |

### Response Process

1. **Detect**: Monitoring, alerts, reports
2. **Triage**: Confirm, assess severity, assign response lead
3. **Contain**: Limit impact (revoke keys, block IPs, disable feature)
4. **Fix**: Develop, test, deploy patch
5. **Communicate**: Notify affected users, coordinate disclosure
6. **Postmortem**: Document root cause, improve defenses

## Secure Development Lifecycle

- **Threat modeling** for new features
- **Code review** checklist includes security
- **SAST** in CI (bandit, Semgrep)
- **DAST** for web application
- **Dependency scanning** in CI
- **Secret scanning** pre-commit (git-secrets, gitleaks)
- **Penetration testing** before major releases

## Contact

For security inquiries:

- **Email**: `security@twib.io`
- **PGP Key**: Available on request via email

Thank you for helping keep TWIB and its users safe.