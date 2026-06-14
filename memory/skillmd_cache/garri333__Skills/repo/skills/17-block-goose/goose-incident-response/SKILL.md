---
name: goose-incident-response
version: 1.0.0
description: >
  Incident response checklist and procedures for enterprise environments. Provides severity
  classification (P0-P4), escalation workflows, communication templates, post-mortem generation,
  Root Cause Analysis (RCA), timeline reconstruction, and integration with alerting platforms.
tags:
  - incident-response
  - on-call
  - post-mortem
  - rca
  - escalation
  - pagerduty
  - opsgenie
  - monitoring
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

# goose-incident-response

Incident response checklist and procedures for enterprise environments. Guides teams through severity classification, escalation, communication, resolution, and post-mortem processes.

---

## When to Activate

Activate this skill when the user:

- Reports or mentions an **active incident** or outage
- Needs to **classify the severity** of a production issue
- Asks about **escalation procedures** or on-call responsibilities
- Wants to create a **post-mortem** or **incident report**
- Needs to perform **Root Cause Analysis (RCA)**
- Requests a **timeline reconstruction** of an incident
- Wants to draft **stakeholder communications** during an incident
- Needs to update a **status page** during an outage
- Mentions alerting tools: `PagerDuty`, `Opsgenie`, `Datadog`, `alerts`
- Uses incident keywords: `incident`, `outage`, `downtime`, `P0`, `P1`, `escalate`, `post-mortem`, `RCA`

---

## Step-by-Step Instructions

### 1. Severity Classification

Classify every incident using the P0–P4 scale:

| Severity | Name | Description | Response Time | Update Cadence | Examples |
|---|---|---|---|---|---|
| **P0** | Critical | Complete service outage, data loss, security breach | Immediate (< 5 min) | Every 15 min | Full production down, data breach, payment processing failure |
| **P1** | High | Major feature degraded, significant user impact | < 15 min | Every 30 min | Auth system down, 50%+ error rate, core API failures |
| **P2** | Medium | Minor feature impacted, workaround available | < 1 hour | Every 2 hours | Non-critical feature broken, elevated latency, partial degradation |
| **P3** | Low | Cosmetic issue, minimal user impact | < 4 hours | Daily | UI glitch, minor logging errors, non-blocking bugs |
| **P4** | Informational | No user impact, improvement opportunity | Next business day | As needed | Technical debt, monitoring gap, documentation update |

### 2. Incident Declaration

When an incident is detected or reported:

```
INCIDENT DECLARATION CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Confirm the issue is real (not a false alarm)
□ Assess user impact and blast radius
□ Assign severity level (P0–P4)
□ Assign Incident Commander (IC)
□ Create incident channel (#inc-YYYY-MM-DD-short-name)
□ Page on-call engineer (if P0/P1)
□ Start incident timeline log
□ Post initial status page update
□ Notify stakeholders per escalation matrix
```

### 3. Escalation Procedures

```
ESCALATION MATRIX:
══════════════════

P0 — Critical:
  T+0m:   On-call engineer paged (PagerDuty/Opsgenie)
  T+5m:   Incident Commander assigned
  T+10m:  Engineering Manager notified
  T+15m:  VP Engineering + CTO notified
  T+30m:  Executive stakeholders briefed
  T+60m:  External communication (status page, social media)

P1 — High:
  T+0m:   On-call engineer paged
  T+15m:  Incident Commander assigned
  T+30m:  Engineering Manager notified
  T+2h:   Director of Engineering notified

P2 — Medium:
  T+0m:   On-call engineer notified (non-urgent)
  T+1h:   Team lead informed
  T+4h:   Escalate to P1 if unresolved

P3/P4 — Low/Informational:
  T+0m:   Ticket created in backlog
  T+24h:  Triaged in next standup
```

### 4. Communication Templates

#### Initial Incident Notification

```
📢 INCIDENT DECLARED — [SEVERITY]

Title: [Brief description of the issue]
Severity: [P0/P1/P2/P3/P4]
Impact: [What users are experiencing]
Started: [Timestamp when issue began]
Status: Investigating

Incident Commander: [Name]
Channel: #inc-[date]-[short-name]

Current Actions:
  - [Action 1 being taken]
  - [Action 2 being taken]

Next Update: [Time of next update]
```

#### Status Update Template

```
🔄 INCIDENT UPDATE — [SEVERITY] — Update #[N]

Title: [Brief description]
Status: [Investigating | Identified | Monitoring | Resolved]
Duration: [Time since incident start]

What we know:
  - [Finding 1]
  - [Finding 2]

What we're doing:
  - [Action 1]
  - [Action 2]

User impact: [Current impact description]
ETA to resolution: [Estimate or "Under investigation"]

Next update: [Time]
```

#### Resolution Notification

```
✅ INCIDENT RESOLVED — [SEVERITY]

Title: [Brief description]
Duration: [Total incident duration]
Impact: [Summary of user impact]
Resolution: [What fixed the issue]

Post-mortem will be published within [48/72] hours.
Post-mortem owner: [Name]

Action items will be tracked in: [Jira/Linear project link]
```

### 5. Timeline Reconstruction

Build a detailed timeline of the incident:

```
INCIDENT TIMELINE: INC-2026-0222
═════════════════════════════════

09:42 UTC — Datadog alert: Error rate spike on /api/orders (> 10%)
09:43 UTC — PagerDuty page sent to on-call engineer @alice
09:45 UTC — @alice acknowledges page, begins investigation
09:47 UTC — Incident declared as P1, channel #inc-0222-orders created
09:48 UTC — IC assigned: @bob
09:52 UTC — Root cause identified: Database connection pool exhausted
09:55 UTC — Status page updated: "Investigating elevated error rates"
10:02 UTC — Fix applied: Connection pool size increased from 20 → 50
10:05 UTC — Error rate returning to normal levels
10:15 UTC — All metrics within normal thresholds
10:20 UTC — Incident downgraded to monitoring phase
10:50 UTC — Incident resolved, monitoring confirmed stable (30 min)
10:52 UTC — Status page updated: "Resolved"
10:55 UTC — Resolution notification sent to stakeholders

Total Duration: 1 hour 8 minutes
Time to Detect (TTD): 1 minute
Time to Respond (TTR): 3 minutes
Time to Mitigate (TTM): 20 minutes
Time to Resolve: 1 hour 8 minutes
```

### 6. Root Cause Analysis (RCA)

Follow the structured RCA methodology:

```
ROOT CAUSE ANALYSIS:
━━━━━━━━━━━━━━━━━━━

1. WHAT happened?
   → [Describe the observable symptoms]

2. WHEN did it happen?
   → [Precise timestamps]

3. WHO was affected?
   → [Users, services, regions]

4. WHY did it happen? (5 Whys)
   → Why 1: Orders API returning 500 errors
   → Why 2: Database queries timing out
   → Why 3: Connection pool exhausted
   → Why 4: Connection leak in new ORM version
   → Why 5: Upgrade was not load-tested with production traffic patterns
   ━━━━━━━━━━━
   ROOT CAUSE: Missing load testing in the ORM upgrade deployment workflow

5. HOW do we prevent recurrence?
   → Action items with owners and deadlines
```

### 7. Post-Mortem Generation

Generate a complete post-mortem document:

```
POST-MORTEM: INC-2026-0222 — Orders API Outage
═══════════════════════════════════════════════

Date: February 22, 2026
Author: [IC Name]
Severity: P1
Duration: 1 hour 8 minutes
User Impact: ~2,400 users experienced order failures

SUMMARY:
  The Orders API experienced elevated error rates (peak 45%)
  due to database connection pool exhaustion following an
  ORM library upgrade deployed the previous day.

TIMELINE:
  [Insert reconstructed timeline]

ROOT CAUSE:
  The ORM upgrade (v3.2 → v4.0) introduced a connection
  handling change that caused connection leaks under high
  concurrency. This was not caught because the upgrade was
  not load-tested with production traffic patterns.

CONTRIBUTING FACTORS:
  - No load testing requirement for dependency upgrades
  - Connection pool monitoring alert threshold too high
  - Missing connection leak detection in staging

WHAT WENT WELL:
  ✓ Alert fired within 1 minute of issue onset
  ✓ On-call responded within 3 minutes
  ✓ Root cause identified quickly (7 minutes)
  ✓ Clear communication throughout

WHAT COULD BE IMPROVED:
  ✗ Load testing should be mandatory for ORM/DB changes
  ✗ Connection pool alerts should fire at 70% (not 95%)
  ✗ Staging should simulate production concurrency levels

ACTION ITEMS:
  | # | Action | Owner | Priority | Due Date |
  |---|--------|-------|----------|----------|
  | 1 | Add load testing to dependency upgrade checklist | @alice | P1 | 2026-03-01 |
  | 2 | Lower connection pool alert threshold to 70% | @bob | P2 | 2026-02-28 |
  | 3 | Add connection leak detection to staging | @carol | P2 | 2026-03-15 |
  | 4 | Document ORM upgrade testing requirements | @alice | P3 | 2026-03-08 |

LESSONS LEARNED:
  Dependency upgrades, especially those affecting database
  connectivity, must be load-tested with production-like
  traffic before deployment.
```

### 8. Integration with Alerting Platforms

#### PagerDuty Integration

```
PagerDuty Actions:
  - Trigger incident: POST /incidents with severity routing
  - Acknowledge: Update incident status
  - Resolve: Close incident with resolution notes
  - Escalate: Trigger escalation policy
  - Add responders: Page additional team members
```

#### Opsgenie Integration

```
Opsgenie Actions:
  - Create alert with priority mapping (P0→P1, P1→P2, etc.)
  - Assign to on-call schedule
  - Add tags for routing and filtering
  - Attach runbook links
  - Close with post-mortem reference
```

#### Datadog Integration

```
Datadog Actions:
  - Query monitors for alert status
  - Pull metrics for timeline reconstruction
  - Create dashboard for incident analysis
  - Generate error rate / latency graphs
  - Correlate deployment events with metric changes
```

---

## Best Practices

1. **Declare incidents early** — It's better to declare and downgrade than to miss an escalation window
2. **Assign an Incident Commander** — One person owns coordination; engineers focus on fixing
3. **Blameless post-mortems** — Focus on systems and processes, never individuals
4. **Communicate frequently** — Silence during incidents erodes trust; send updates even if there's no new information
5. **Track action items** — Every post-mortem must produce actionable items with owners and deadlines
6. **Practice incident response** — Run regular game days and tabletop exercises
7. **Maintain runbooks** — Keep step-by-step guides for common failure modes
8. **Measure incident metrics** — Track TTD, TTR, TTM, and MTBF for continuous improvement
9. **Automate detection** — Invest in monitoring and alerting to reduce TTD
10. **Review past incidents** — Learn from history; review post-mortems quarterly

---

## Examples

### Example 1: Declaring a P1 Incident

**User prompt:**
> "Our API error rate just spiked to 30%, we're getting reports from customers"

**Expected behavior:**

```
🚨 INCIDENT ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━

Symptoms: API error rate at 30%, customer reports of failures
Recommended Severity: P1 (High)
  → Major feature degraded with significant user impact

IMMEDIATE ACTIONS:
  [✓] Severity classified: P1
  [✓] Incident Commander needed — assign now
  [✓] Create channel: #inc-2026-0222-api-errors

Escalation (P1 Protocol):
  → Page on-call engineer immediately
  → Notify Engineering Manager within 15 minutes
  → First stakeholder update within 30 minutes

INVESTIGATION CHECKLIST:
  □ Check recent deployments (last 24h)
  □ Review error logs for common patterns
  □ Check database health (connections, queries)
  □ Check external dependency status
  □ Review infrastructure metrics (CPU, memory, disk)
  □ Check for traffic anomalies

INITIAL STATUS UPDATE (draft):
  📢 INCIDENT DECLARED — P1
  Title: Elevated API error rates (~30%)
  Impact: Customers experiencing intermittent failures
  Status: Investigating
  Next Update: 30 minutes
```

### Example 2: Writing a Post-Mortem

**User prompt:**
> "Write a post-mortem for yesterday's auth service outage that lasted 45 minutes"

**Expected behavior:**

The skill generates a complete post-mortem document following the template in Step 7, asking clarifying questions for missing details:

```
I'll help you write the post-mortem. I need a few details:

1. What was the root cause?
2. How many users were affected?
3. What fixed the issue?
4. Who was the Incident Commander?

Meanwhile, here's the structure I'll follow:
  → Summary
  → Timeline (I'll help reconstruct from logs)
  → Root Cause + 5 Whys analysis
  → Contributing factors
  → What went well / could improve
  → Action items with owners and deadlines
  → Lessons learned
```

### Example 3: Escalation Guidance

**User prompt:**
> "The payment processing service has been down for 20 minutes and we haven't been able to fix it"

**Expected behavior:**

```
⚠️  ESCALATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━

Current Status:
  Service: Payment processing
  Duration: 20 minutes
  Severity: P0 (Critical) — Payment processing is a revenue-critical service

P0 Escalation Protocol (you're at T+20m):
  [✓] T+0m:   On-call engineer engaged (done)
  [⚠️] T+5m:   IC should have been assigned — ASSIGN NOW
  [⚠️] T+10m:  Engineering Manager — NOTIFY NOW
  [⚠️] T+15m:  VP Engineering + CTO — NOTIFY NOW
  [NEXT] T+30m: External communication (status page)

RECOMMENDED IMMEDIATE ACTIONS:
  1. Assign Incident Commander NOW (if not already)
  2. Page Engineering Manager and VP Engineering
  3. Bring in additional responders with payment system expertise
  4. Update status page: "We are aware of issues with payment
     processing and are actively working on a resolution."
  5. Consider rollback if a recent deployment is suspected
  6. Prepare customer communication for support team

CRITICAL: Do not wait longer to escalate. At 20 minutes into
a P0, leadership should already be informed.
```
