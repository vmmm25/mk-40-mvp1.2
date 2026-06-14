---
name: goose-workflows
version: 1.0.0
description: >
  Repeatable workflow automation for enterprise environments. Orchestrates deployment pipelines,
  release workflows, migration procedures, and environment promotions with checklist-driven
  execution and validation gates.
tags:
  - workflows
  - automation
  - deployment
  - pipelines
  - infrastructure
  - enterprise
  - migrations
  - rollback
  - ci-cd
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

# goose-workflows

Repeatable workflow automation for enterprise environments. Manages deployment pipelines, release workflows, migration procedures, and environment promotions with validation gates and rollback capabilities.

---

## When to Activate

Activate this skill when the user:

- Requests help setting up or executing a **deployment pipeline** (staging → production)
- Needs to define or run a **release workflow** with multiple stages
- Wants to perform a **database migration** sequence with validation
- Asks about **rollback procedures** for a failed deployment
- Needs **environment promotion** (dev → staging → production)
- Wants to create **infrastructure as code** patterns for repeatable workflows
- Requests **multi-environment configuration** management
- Needs **checklist-driven workflow** execution with approval gates
- Mentions workflow keywords: `deploy`, `release`, `migrate`, `rollback`, `promote`, `pipeline`

---

## Step-by-Step Instructions

### 1. Identify the Workflow Type

Determine which workflow category the user needs:

| Workflow Type | Description | Key Stages |
|---|---|---|
| **Deployment Pipeline** | Push code from source to production | Build → Test → Stage → Approve → Deploy |
| **Release Workflow** | Coordinate a versioned release | Version bump → Changelog → Tag → Publish → Notify |
| **Migration Procedure** | Database or infrastructure migration | Backup → Validate schema → Apply → Verify → Rollback plan |
| **Environment Promotion** | Promote artifacts between environments | Dev → QA → Staging → Production |
| **Rollback Procedure** | Revert a failed change | Detect → Assess → Rollback → Verify → Post-mortem |

### 2. Define the Workflow Stages

For each workflow, define explicit stages with:

```yaml
workflow:
  name: "deployment-pipeline"
  version: "1.0.0"
  trigger: "manual | on-push | scheduled"
  
  stages:
    - name: "build"
      description: "Compile and package the application"
      validation:
        - "All tests pass"
        - "Build artifacts generated"
      timeout: "10m"
      on_failure: "abort"

    - name: "test"
      description: "Run integration and e2e tests"
      validation:
        - "Test coverage >= 80%"
        - "No critical vulnerabilities"
      timeout: "20m"
      on_failure: "abort"

    - name: "stage"
      description: "Deploy to staging environment"
      validation:
        - "Health check passes"
        - "Smoke tests pass"
      timeout: "15m"
      on_failure: "rollback"
      requires_approval: false

    - name: "approve"
      description: "Manual approval gate"
      validation:
        - "Stakeholder sign-off"
      timeout: "24h"
      on_failure: "abort"

    - name: "deploy"
      description: "Deploy to production"
      validation:
        - "Health check passes"
        - "Canary metrics within threshold"
      timeout: "30m"
      on_failure: "rollback"
      rollback_to: "stage"
```

### 3. Implement Validation Gates

Each stage must have validation gates before proceeding:

```
VALIDATION GATE CHECKLIST:
□ Pre-condition checks pass
□ Required approvals obtained
□ Health checks return 200
□ Smoke tests pass
□ Performance metrics within threshold
□ Security scan clean
□ Rollback plan documented
□ Monitoring alerts configured
```

### 4. Configure Environment Promotion

```
ENVIRONMENT CHAIN:
  
  [Development] → [QA/Testing] → [Staging] → [Production]
       ↑                                          |
       └──────── Rollback Path ←──────────────────┘

Per-environment configuration:
  - Environment variables (secrets management)
  - Feature flags
  - Database connection strings
  - API endpoint URLs
  - Resource scaling (replicas, CPU, memory)
  - Logging levels
  - Monitoring thresholds
```

### 5. Database Migration Sequence

```
MIGRATION PROCEDURE:
  1. Create backup of current database
  2. Validate migration scripts (dry run)
  3. Check for breaking schema changes
  4. Apply migration in transaction
  5. Run data integrity verification
  6. Update ORM models / application code
  7. Run integration tests against new schema
  8. Document rollback SQL
  9. Monitor for errors (15-minute window)
  10. Confirm migration success
```

### 6. Execute with Checklist Tracking

Track each step explicitly:

```
WORKFLOW EXECUTION LOG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pipeline: deployment-v2.3.1
Started: 2026-02-22T10:00:00Z
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Stage 1/5: Build ............... PASS (2m 14s)
[✓] Stage 2/5: Test ............... PASS (8m 42s)
[✓] Stage 3/5: Stage Deploy ....... PASS (3m 01s)
[⏳] Stage 4/5: Approval Gate ...... WAITING
[ ] Stage 5/5: Production Deploy ... PENDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7. Generate Rollback Plan

Every deployment must include a rollback plan:

```
ROLLBACK PLAN:
  Trigger conditions:
    - Error rate > 5% (sustained 5 minutes)
    - P50 latency > 500ms
    - Health check failures > 3 consecutive
    - Critical alert from monitoring

  Rollback steps:
    1. Switch traffic to previous deployment (blue/green or canary)
    2. Revert database migration (if applicable)
    3. Restore configuration to previous version
    4. Verify health checks
    5. Notify stakeholders
    6. Create incident report

  Estimated rollback time: < 5 minutes
  Responsible: on-call engineer + release manager
```

---

## Best Practices

1. **Never skip validation gates** — Every stage must pass its checks before promotion
2. **Always have a rollback plan** — Document rollback steps before deploying
3. **Use infrastructure as code** — Define workflows in version-controlled YAML/JSON
4. **Implement canary deployments** — Roll out to a subset before full deployment
5. **Separate configuration from code** — Use environment-specific config files or secret managers
6. **Log everything** — Maintain audit trails of who approved what and when
7. **Set timeouts** — Every stage should have a maximum execution time
8. **Test rollback procedures** — Regularly validate that rollback actually works
9. **Use feature flags** — Decouple deployment from feature release
10. **Automate notifications** — Slack/Teams/email alerts at each stage transition

---

## Examples

### Example 1: Simple Deployment Pipeline

**User prompt:**
> "Help me deploy version 2.3.1 of our backend service to production"

**Expected behavior:**

```
DEPLOYMENT PIPELINE: backend-service v2.3.1
══════════════════════════════════════════

Pre-flight checks:
  [✓] Version 2.3.1 tag exists
  [✓] All CI tests passing on tag
  [✓] No open P0/P1 incidents
  [✓] Change window approved

Step 1: Build & Package
  → Building Docker image: backend-service:2.3.1
  → Pushing to registry: registry.example.com/backend-service:2.3.1
  [✓] Image built and pushed successfully

Step 2: Deploy to Staging
  → Updating staging deployment to 2.3.1
  → Running health checks...
  → Running smoke tests...
  [✓] Staging deployment healthy

Step 3: Approval
  → Awaiting approval from release manager
  → Approval granted by @manager at 10:45 UTC

Step 4: Deploy to Production
  → Starting canary deployment (10% traffic)
  → Monitoring metrics for 5 minutes...
  → Canary healthy, promoting to 50%...
  → Promoting to 100%...
  [✓] Production deployment complete

Step 5: Post-deploy verification
  → Health check: PASS
  → Error rate: 0.02% (within threshold)
  → P50 latency: 45ms (within threshold)
  [✓] Deployment verified successfully

Rollback command (if needed):
  kubectl rollout undo deployment/backend-service -n production
```

### Example 2: Database Migration Workflow

**User prompt:**
> "Run the database migration for adding the new orders table"

**Expected behavior:**

```
DATABASE MIGRATION: add-orders-table
═════════════════════════════════════

Migration files:
  → 001_create_orders_table.sql
  → 002_add_orders_indexes.sql
  → 003_seed_order_statuses.sql

Pre-migration:
  [✓] Database backup created: backup_2026-02-22_100000.sql
  [✓] Dry run completed successfully
  [✓] No breaking changes detected
  [✓] Estimated downtime: 0 (online migration)

Execution:
  [✓] 001_create_orders_table.sql — Applied (1.2s)
  [✓] 002_add_orders_indexes.sql — Applied (3.8s)
  [✓] 003_seed_order_statuses.sql — Applied (0.4s)

Post-migration:
  [✓] Schema validation passed
  [✓] Data integrity check passed
  [✓] Application integration tests passed

Rollback SQL (saved to rollback_001-003.sql):
  DROP INDEX IF EXISTS idx_orders_user_id;
  DROP INDEX IF EXISTS idx_orders_status;
  DROP TABLE IF EXISTS orders;
  DELETE FROM order_statuses;
```

### Example 3: Multi-Environment Promotion

**User prompt:**
> "Promote the current staging build to production"

**Expected behavior:**

```
ENVIRONMENT PROMOTION: staging → production
════════════════════════════════════════════

Artifact: frontend-app:staging-abc123f
Current staging version: 3.1.0-rc.2
Production version: 3.0.4

Promotion checklist:
  [✓] Staging has been stable for 48+ hours
  [✓] QA sign-off received
  [✓] Performance benchmarks within tolerance
  [✓] Security scan: no new vulnerabilities
  [✓] Rollback plan documented

Promoting:
  → Retagging staging-abc123f → 3.1.0
  → Updating production deployment manifest
  → Applying production configuration overlay
  → Rolling update in progress (0/3 pods ready)...
  → Rolling update in progress (1/3 pods ready)...
  → Rolling update in progress (3/3 pods ready)...
  [✓] Promotion complete

Notifications sent:
  → #releases channel: "frontend-app 3.1.0 deployed to production"
  → Release manager: deployment confirmation email
  → Status page: updated to operational
```
