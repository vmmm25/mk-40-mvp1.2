---
name: goose-security-audit
version: 1.0.0
description: >
  Security audit skill for enterprise compliance. Performs OWASP Top 10 verification, dependency
  vulnerability scanning (CVE database), secret detection, authentication/authorization review,
  input validation audit, and compliance mapping for SOC 2, ISO 27001, and PCI-DSS.
tags:
  - security
  - audit
  - owasp
  - cve
  - compliance
  - soc2
  - iso27001
  - pci-dss
  - vulnerability
  - enterprise
  - goose
author: garri333
license: MIT
source: block/agent-skills
marketplace: https://block.github.io/goose/skills
compatible:
  - goose
  - claude-desktop
  - skill-md-standard
---

# goose-security-audit

Security audit skill for enterprise compliance. Performs comprehensive security assessments covering OWASP Top 10, dependency vulnerabilities, secrets detection, authentication, authorization, and compliance mapping.

---

## When to Activate

Activate this skill when the user:

- Requests a **security audit** or **security review** of code or infrastructure
- Wants to check for **OWASP Top 10** vulnerabilities
- Needs **dependency vulnerability scanning** (CVE checking)
- Asks about **secret detection** in code or configuration
- Wants to review **authentication or authorization** implementation
- Needs an **input validation audit**
- Asks about **SQL injection, XSS**, or other injection prevention
- Wants to verify **CORS policy, CSP headers**, or **rate limiting**
- Needs **API security assessment**
- Asks about **compliance** (SOC 2, ISO 27001, PCI-DSS)
- Uses security keywords: `security`, `audit`, `vulnerability`, `CVE`, `OWASP`, `compliance`, `penetration`, `secrets`

---

## Step-by-Step Instructions

### 1. OWASP Top 10 Verification (2021)

Systematically check for each OWASP Top 10 vulnerability:

| # | Category | What to Check |
|---|---|---|
| **A01** | Broken Access Control | Missing auth checks, IDOR, privilege escalation, CORS misconfig |
| **A02** | Cryptographic Failures | Weak algorithms, plaintext secrets, missing TLS, poor key management |
| **A03** | Injection | SQL injection, NoSQL injection, OS command injection, LDAP injection |
| **A04** | Insecure Design | Missing threat modeling, insecure business logic, insufficient validation |
| **A05** | Security Misconfiguration | Default credentials, unnecessary features, verbose errors, missing headers |
| **A06** | Vulnerable Components | Outdated dependencies, known CVEs, unmaintained libraries |
| **A07** | Auth Failures | Weak passwords allowed, missing MFA, session fixation, credential stuffing |
| **A08** | Data Integrity Failures | Insecure deserialization, unsigned updates, CI/CD pipeline compromise |
| **A09** | Logging Failures | Missing audit logs, no alerting on failures, sensitive data in logs |
| **A10** | SSRF | Unvalidated URLs, internal network access, cloud metadata exposure |

```
OWASP TOP 10 AUDIT REPORT:
═══════════════════════════

A01 — Broken Access Control:
  [✓] Authentication required on all protected endpoints
  [✓] Role-based access control implemented
  [⚠️] IDOR potential: /api/users/{id} does not verify ownership
  [✓] CORS restricted to allowed origins
  [✓] Directory listing disabled

A02 — Cryptographic Failures:
  [✓] TLS 1.2+ enforced
  [✓] Passwords hashed with bcrypt (cost factor 12)
  [⚠️] JWT secret stored in environment variable (verify rotation)
  [✓] Sensitive data encrypted at rest (AES-256)
  [✓] No plaintext credentials in codebase

A03 — Injection:
  [✓] Parameterized queries used (no string concatenation)
  [✓] ORM with query builder (no raw SQL in business logic)
  [✓] User input sanitized before template rendering
  [⚠️] One instance of exec() in admin utility script

  ... [continue for all 10 categories]
```

### 2. Dependency Vulnerability Scanning

```
DEPENDENCY VULNERABILITY SCAN:
══════════════════════════════

Scanning: package.json / requirements.txt / go.mod

CRITICAL (must fix immediately):
  🔴 CVE-2026-1234 — lodash 4.17.20
     Severity: Critical (CVSS 9.8)
     Type: Prototype pollution → Remote Code Execution
     Fix: Upgrade to lodash >= 4.17.21
     Affected: src/utils/data-transform.js

  🔴 CVE-2026-5678 — jsonwebtoken 8.5.1
     Severity: Critical (CVSS 9.1)
     Type: Algorithm confusion → Auth bypass
     Fix: Upgrade to jsonwebtoken >= 9.0.0
     Affected: src/middleware/auth.js

HIGH (fix within 1 week):
  🟠 CVE-2025-9012 — express 4.18.1
     Severity: High (CVSS 7.5)
     Type: ReDoS in URL parsing
     Fix: Upgrade to express >= 4.18.3

MEDIUM (fix within 1 month):
  🟡 CVE-2025-3456 — axios 0.27.2
     Severity: Medium (CVSS 5.3)
     Type: SSRF via redirect following
     Fix: Upgrade to axios >= 1.3.0

LOW (fix in next maintenance window):
  🟢 CVE-2025-7890 — debug 4.3.2
     Severity: Low (CVSS 3.1)
     Type: Information disclosure in error messages
     Fix: Upgrade to debug >= 4.3.4

SUMMARY:
  Total dependencies: 142
  Direct: 28 | Transitive: 114
  Vulnerabilities: 2 Critical, 1 High, 1 Medium, 1 Low
  Action Required: Fix 2 Critical CVEs before next deployment
```

### 3. Secret Detection

```
SECRET DETECTION SCAN:
═════════════════════

Scanning for: API keys, passwords, tokens, private keys,
              connection strings, certificates

FINDINGS:

  🔴 CRITICAL — Hardcoded API key detected
     File: src/services/payment.js:42
     Pattern: sk_live_[a-zA-Z0-9]{24}
     Content: const apiKey = "sk_live_EXAMPLE_REDACTED_KEY"
     Action: Rotate key immediately, move to environment variable

  🔴 CRITICAL — Database password in config
     File: config/database.yml:15
     Content: password: "Pr0duct10n_P@ssw0rd!"
     Action: Move to secrets manager (AWS Secrets Manager, Vault)

  🟠 WARNING — Potential AWS credentials
     File: scripts/deploy.sh:8
     Pattern: AKIA[0-9A-Z]{16}
     Action: Verify if real; if so, rotate and use IAM roles

  🟠 WARNING — Private key file tracked in Git
     File: certs/server.key
     Action: Remove from Git, add to .gitignore, re-generate

GIT HISTORY CHECK:
  ⚠️ Found 3 commits with potential secrets in history
  → Recommend using git-filter-repo to scrub history
  → Or BFG Repo-Cleaner for simpler cases

RECOMMENDED .gitignore ADDITIONS:
  *.key
  *.pem
  *.p12
  .env
  .env.*
  config/secrets.*
```

### 4. Authentication & Authorization Review

```
AUTHENTICATION AUDIT:
━━━━━━━━━━━━━━━━━━━━

Password Policy:
  [✓] Minimum length: 12 characters
  [✓] Complexity requirements enforced
  [⚠️] No check against breached password databases (Have I Been Pwned)
  [✓] Bcrypt hashing with cost factor 12
  [✓] No password hints or security questions

Session Management:
  [✓] Session tokens are cryptographically random
  [✓] Session timeout configured (30 minutes idle)
  [✓] Session invalidated on logout
  [⚠️] No concurrent session limit
  [✓] Secure and HttpOnly flags on session cookies
  [✓] SameSite attribute set to Strict

Multi-Factor Authentication:
  [✓] TOTP-based MFA available
  [⚠️] MFA not enforced for admin accounts
  [✓] Backup codes generated securely
  [✓] MFA recovery process requires identity verification

JWT Implementation:
  [✓] Using RS256 (asymmetric) algorithm
  [✓] Token expiration set (15 minutes access, 7 days refresh)
  [✓] Refresh token rotation implemented
  [⚠️] No token blacklist for revocation before expiry
  [✓] Audience and issuer claims validated

AUTHORIZATION AUDIT:
━━━━━━━━━━━━━━━━━━━

Access Control Model: Role-Based (RBAC)
  [✓] Roles defined: admin, manager, user, readonly
  [✓] Permissions mapped to roles
  [✓] Default role is least privileged (readonly)
  [⚠️] No attribute-based access control (ABAC) for fine-grained rules
  [✓] API endpoints enforce role checks
  [✓] Frontend route guards match backend authorization
  [⚠️] Missing ownership verification on resource endpoints
```

### 5. Input Validation Audit

```
INPUT VALIDATION AUDIT:
━━━━━━━━━━━━━━━━━━━━━━

Server-Side Validation:
  [✓] All API inputs validated with schema (Joi/Zod/Pydantic)
  [✓] Type checking enforced
  [✓] Length limits on string fields
  [✓] Range validation on numeric fields
  [✓] Email format validation
  [⚠️] Missing validation on file upload content type
  [✓] Date format validation (ISO 8601)
  [✓] Enum values restricted to allowed set

SQL Injection Prevention:
  [✓] Parameterized queries used throughout
  [✓] No string concatenation in SQL
  [✓] ORM used for standard queries
  [⚠️] 1 raw SQL query in reporting module — verify parameterized

XSS Prevention:
  [✓] Output encoding in templates (auto-escaping enabled)
  [✓] Content-Security-Policy header configured
  [⚠️] CSP allows 'unsafe-inline' for styles — consider removing
  [✓] No innerHTML or dangerouslySetInnerHTML usage
  [✓] React/Vue auto-escaping relied upon correctly

CSRF Prevention:
  [✓] CSRF tokens on all state-changing forms
  [✓] SameSite cookie attribute set
  [✓] Origin/Referer header validation
```

### 6. HTTP Security Headers Review

```
HTTP SECURITY HEADERS:
━━━━━━━━━━━━━━━━━━━━━

Header                          Status    Value
──────────────────────────────  ────────  ─────────────────────────
Content-Security-Policy         [⚠️]      default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
X-Content-Type-Options          [✓]       nosniff
X-Frame-Options                 [✓]       DENY
X-XSS-Protection                [✓]       0 (disabled, CSP preferred)
Strict-Transport-Security       [✓]       max-age=31536000; includeSubDomains; preload
Referrer-Policy                 [✓]       strict-origin-when-cross-origin
Permissions-Policy              [⚠️]      Missing — should restrict camera, mic, geolocation
Cache-Control                   [✓]       no-store on sensitive endpoints
X-Permitted-Cross-Domain        [✓]       none

CORS Configuration:
  Access-Control-Allow-Origin:      https://app.example.com
  Access-Control-Allow-Methods:     GET, POST, PUT, DELETE
  Access-Control-Allow-Headers:     Content-Type, Authorization
  Access-Control-Allow-Credentials: true
  Access-Control-Max-Age:           3600

  [✓] Origin is specific (not wildcard *)
  [✓] Methods are appropriate
  [⚠️] Consider restricting to only needed headers
```

### 7. Rate Limiting Verification

```
RATE LIMITING AUDIT:
━━━━━━━━━━━━━━━━━━━

Endpoint                    Limit           Window    Status
─────────────────────────  ──────────────  ────────  ──────
POST /api/auth/login       5 requests      15 min    [✓]
POST /api/auth/register    3 requests      1 hour    [✓]
POST /api/auth/reset       3 requests      1 hour    [✓]
GET  /api/users            100 requests    1 min     [✓]
POST /api/orders           30 requests     1 min     [✓]
GET  /api/search           20 requests     1 min     [✓]
POST /api/upload           5 requests      10 min    [✓]
* (global)                 1000 requests   1 min     [✓]

Authentication Brute Force Protection:
  [✓] Account lockout after 5 failed attempts
  [✓] Progressive delay (exponential backoff)
  [✓] IP-based rate limiting
  [⚠️] No CAPTCHA challenge after 3 failures
  [✓] Failed attempt logging for monitoring
```

### 8. API Security Assessment

```
API SECURITY ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━

Authentication:
  [✓] Bearer token required on protected endpoints
  [✓] API key authentication for service-to-service
  [✓] Token validation on every request

Input/Output:
  [✓] Request body size limits enforced (1MB default)
  [✓] Response does not leak internal error details
  [✓] Pagination enforced on list endpoints
  [✓] Field filtering prevents mass assignment
  [⚠️] No response schema validation (could leak unexpected fields)

Transport:
  [✓] TLS 1.2+ required
  [✓] HSTS enabled with preload
  [✓] Certificate pinning for mobile clients

Versioning & Deprecation:
  [✓] API versioned (v1, v2) in URL path
  [✓] Deprecated endpoints return Sunset header
  [✓] Change log maintained
```

### 9. Compliance Mapping

```
COMPLIANCE MAPPING:
═══════════════════

SOC 2 — Trust Service Criteria:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CC6.1 — Logical Access Security:
    [✓] Role-based access control implemented
    [✓] Least privilege principle applied
    [⚠️] Access reviews not automated

  CC6.2 — Credentials Management:
    [✓] Passwords hashed with bcrypt
    [✓] MFA available
    [⚠️] Password rotation not enforced

  CC7.1 — System Monitoring:
    [✓] Audit logging enabled
    [✓] Alerting on suspicious activity
    [✓] Log retention policy (90 days)

  CC8.1 — Change Management:
    [✓] All changes via pull request
    [✓] Code review required
    [✓] CI/CD pipeline with security checks

ISO 27001 — Annex A Controls:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  A.9 — Access Control:        [✓] Implemented
  A.10 — Cryptography:         [✓] AES-256, TLS 1.2+
  A.12 — Operations Security:  [✓] Logging, monitoring
  A.14 — System Development:   [✓] Secure SDLC, code review
  A.16 — Incident Management:  [⚠️] Partial — needs formal IRP
  A.18 — Compliance:           [✓] Regular audits scheduled

PCI-DSS (if processing payments):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Req 1 — Network Security:          [✓] Firewall rules defined
  Req 2 — Secure Configurations:     [✓] No default credentials
  Req 3 — Protect Stored Data:       [✓] Encryption at rest
  Req 4 — Encrypt Transmission:      [✓] TLS for all card data
  Req 6 — Secure Development:        [✓] Secure SDLC practices
  Req 7 — Restrict Access:           [✓] Need-to-know basis
  Req 8 — Identify & Authenticate:   [✓] Unique IDs, MFA
  Req 10 — Logging & Monitoring:     [✓] Audit trails
  Req 11 — Test Security:            [⚠️] Penetration testing quarterly
  Req 12 — Security Policies:        [⚠️] Needs formal documentation
```

---

## Best Practices

1. **Defense in depth** — Apply security controls at every layer (network, application, data)
2. **Least privilege** — Grant only the minimum access required for each role
3. **Fail securely** — Errors should default to denying access, never granting
4. **Validate everything** — Never trust user input; validate on the server side
5. **Encrypt sensitive data** — At rest (AES-256) and in transit (TLS 1.2+)
6. **Keep dependencies updated** — Automate CVE scanning in CI/CD pipeline
7. **Never commit secrets** — Use environment variables, secrets managers, or vaults
8. **Log security events** — Authentication attempts, authorization failures, data access
9. **Rotate credentials regularly** — API keys, passwords, certificates, tokens
10. **Conduct regular audits** — Schedule quarterly security reviews and annual penetration tests

---

## Examples

### Example 1: Full Security Audit

**User prompt:**
> "Run a security audit on our Node.js backend application"

**Expected behavior:**

```
SECURITY AUDIT REPORT
═════════════════════

Project: Node.js Backend
Date: 2026-02-22
Auditor: goose-security-audit v1.0.0

EXECUTIVE SUMMARY:
  Overall Risk Level: MEDIUM
  Critical Findings: 2
  High Findings: 3
  Medium Findings: 5
  Low Findings: 4
  Informational: 6

CRITICAL FINDINGS:
  1. Hardcoded payment API key in payment service
     → Risk: Financial data exposure
     → Fix: Move to environment variable, rotate key

  2. SQL injection in legacy reporting endpoint
     → Risk: Database compromise
     → Fix: Convert to parameterized query

HIGH FINDINGS:
  1. Missing rate limiting on authentication endpoints
  2. JWT tokens have no revocation mechanism
  3. CORS allows wildcard origin in staging config

[Full report continues with all categories...]

REMEDIATION PRIORITY:
  Week 1: Fix all Critical findings
  Week 2: Fix all High findings
  Month 1: Fix all Medium findings
  Quarter: Address Low and Informational items
```

### Example 2: Dependency CVE Check

**User prompt:**
> "Check our dependencies for known vulnerabilities"

**Expected behavior:**

```
DEPENDENCY VULNERABILITY REPORT
════════════════════════════════

Scanning: package.json (npm)

Found 3 vulnerabilities in 142 packages:

  🔴 CRITICAL: CVE-2026-1234 in lodash@4.17.20
     Prototype Pollution → Remote Code Execution
     Fix: npm install lodash@4.17.21

  🟠 HIGH: CVE-2025-5678 in express@4.18.1
     ReDoS in URL parsing
     Fix: npm install express@4.18.3

  🟡 MEDIUM: CVE-2025-9012 in axios@0.27.2
     SSRF via redirect following
     Fix: npm install axios@1.6.0

Quick fix command:
  npm audit fix

Or targeted upgrades:
  npm install lodash@4.17.21 express@4.18.3 axios@1.6.0
```

### Example 3: Compliance Gap Analysis

**User prompt:**
> "We need SOC 2 compliance. What gaps do we have?"

**Expected behavior:**

```
SOC 2 COMPLIANCE GAP ANALYSIS
══════════════════════════════

Trust Service Criteria Assessment:

SECURITY (Common Criteria):
  ✅ CC6.1 Logical Access — RBAC implemented
  ✅ CC6.2 Credentials — Bcrypt hashing, MFA available
  ⚠️ CC6.3 Access Removal — No automated deprovisioning
  ✅ CC7.1 Monitoring — Logging and alerting active
  ⚠️ CC7.2 Incident Response — No formal IRP document
  ✅ CC8.1 Change Management — PR-based workflow

AVAILABILITY:
  ✅ A1.1 Capacity Planning — Auto-scaling configured
  ⚠️ A1.2 Recovery — No documented disaster recovery plan
  ✅ A1.3 Backup — Daily backups with 30-day retention

CONFIDENTIALITY:
  ✅ C1.1 Data Classification — PII identified and tagged
  ⚠️ C1.2 Data Disposal — No data retention/deletion policy

GAPS REQUIRING ACTION:
  1. Create formal Incident Response Plan (IRP)
  2. Implement automated user deprovisioning
  3. Document disaster recovery procedures
  4. Create data retention and disposal policy
  5. Schedule quarterly access reviews
  6. Conduct annual penetration test
  7. Create security awareness training program

Estimated effort to close gaps: 4-6 weeks
```
