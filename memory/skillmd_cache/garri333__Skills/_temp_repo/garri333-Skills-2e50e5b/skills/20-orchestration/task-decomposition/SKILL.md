---
name: task-decomposition
version: 1.0.0
description: >
  Break complex tasks into manageable atomic subtasks. Create work breakdown structures (WBS),
  generate dependency graphs, identify critical paths, assign effort estimates, plan parallel
  vs sequential execution, define milestones, identify risks per subtask, and specify resource
  requirements.
tags:
  - orchestration
  - task-decomposition
  - work-breakdown
  - wbs
  - dependency-graph
  - critical-path
  - planning
  - estimation
  - milestones
  - risk-management
author: garri333
license: MIT
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# task-decomposition

Break complex tasks into manageable, atomic subtasks. Build work breakdown structures, dependency graphs, and critical paths. Estimate effort, plan execution order, define milestones, and identify risks.

---

## When to Activate

Activate this skill when the user:

- Has a **complex task** that needs to be broken into smaller pieces
- Asks for a **work breakdown structure** (WBS) or task plan
- Needs to understand **dependencies** between tasks
- Wants to identify the **critical path** (longest sequence of dependent tasks)
- Asks for **effort estimates** or timeline planning
- Needs to determine which tasks can run in **parallel**
- Wants to define **milestones** for a project phase
- Asks about **risk identification** for subtasks
- Needs to **assign resources** (agents or team members) to tasks
- Uses keywords: `break down`, `decompose`, `subtask`, `plan`, `WBS`, `dependency`, `critical path`, `estimate`

---

## Step-by-Step Instructions

### 1. Decomposition Principles

```
TASK DECOMPOSITION RULES
══════════════════════════════════════════════════════════════

1. MECE (Mutually Exclusive, Collectively Exhaustive)
   - Every piece of work appears in exactly one subtask
   - All subtasks together cover 100% of the parent task
   - No overlap, no gaps

2. ATOMIC
   - Each subtask does ONE thing
   - Can be assigned to ONE agent/person
   - Has a clear definition of "done"

3. ESTIMABLE
   - Small enough to estimate confidently
   - If you can't estimate it, break it down further
   - Target: 1-4 hours per subtask

4. TESTABLE
   - Each subtask has verifiable outcomes
   - "How will I know this is done?"

5. INDEPENDENT (when possible)
   - Minimize dependencies between subtasks
   - More independence = more parallelism = faster completion
```

---

### 2. Work Breakdown Structure (WBS)

```
WBS TEMPLATE
══════════════════════════════════════════════════════════════

TASK: Build E-Commerce Checkout System

1. CHECKOUT FLOW
   1.1 Cart Summary Page
       1.1.1 Display cart items with quantities
       1.1.2 Calculate subtotal, tax, shipping
       1.1.3 Apply coupon code functionality
       1.1.4 Update quantity / remove item actions

   1.2 Shipping Information
       1.2.1 Address form with validation
       1.2.2 Address autocomplete integration
       1.2.3 Shipping method selection
       1.2.4 Shipping cost calculation API

   1.3 Payment Processing
       1.3.1 Payment form (card, PayPal, etc.)
       1.3.2 Stripe/PayPal integration
       1.3.3 Payment validation & 3D Secure
       1.3.4 Payment error handling

   1.4 Order Confirmation
       1.4.1 Order summary display
       1.4.2 Confirmation email trigger
       1.4.3 Order number generation
       1.4.4 Redirect to order tracking

2. BACKEND API
   2.1 Cart Endpoints
       2.1.1 GET /api/cart
       2.1.2 PATCH /api/cart/items/:id
       2.1.3 POST /api/cart/coupon
   2.2 Checkout Endpoints
       2.2.1 POST /api/checkout/shipping
       2.2.2 POST /api/checkout/payment
       2.2.3 POST /api/checkout/confirm
   2.3 Order Management
       2.3.1 Order model & migration
       2.3.2 Order status state machine
       2.3.3 Email notification service

3. TESTING & DEPLOYMENT
   3.1 Unit tests for business logic
   3.2 Integration tests for checkout flow
   3.3 E2E test for happy path
   3.4 Load testing for payment endpoints
   3.5 Staging deployment & smoke tests
```

---

### 3. Dependency Graph Generation

```
DEPENDENCY GRAPH — CHECKOUT SYSTEM
══════════════════════════════════════════════════════════════

   ┌───────────┐
   │ 2.3.1     │ Order model & migration
   │ (Backend) │
   └─────┬─────┘
         │
   ┌─────▼─────┐     ┌───────────┐
   │ 2.1.1-3   │     │ 1.2.4     │ Shipping cost API
   │ Cart API  │     │ (Backend) │
   └─────┬─────┘     └─────┬─────┘
         │                 │
   ┌─────▼─────┐    ┌─────▼─────┐    ┌───────────┐
   │ 1.1.1-4   │    │ 1.2.1-3   │    │ 1.3.2     │ Payment integration
   │ Cart UI   │    │ Ship Form │    │ (Backend) │
   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
         │                │                │
         └────────┬───────┘          ┌─────▼─────┐
                  │                  │ 1.3.1,3,4 │ Payment UI
                  │                  │           │
              ┌───▼───────────┐      └─────┬─────┘
              │   1.4.1-4     │            │
              │ Confirmation  │◄───────────┘
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │   3.1-5       │
              │   Testing     │
              └───────────────┘

PARALLEL GROUPS:
  Group A (parallel): 2.3.1 Order model
  Group B (parallel): 2.1.x Cart API | 1.2.4 Shipping API | 1.3.2 Payment
  Group C (parallel): 1.1.x Cart UI | 1.2.x Shipping Form | 1.3.x Payment UI
  Group D (sequential): 1.4.x Confirmation (needs all of C)
  Group E (sequential): 3.x Testing (needs all of D)
```

**Programmatic representation:**

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    id: str
    name: str
    description: str
    estimated_hours: float
    dependencies: list[str] = field(default_factory=list)
    agent: str = ""
    status: str = "pending"  # pending | in_progress | done | blocked
    risk: str = "low"        # low | medium | high

tasks = [
    Task("2.3.1", "Order model", "Create Order model and migration", 2,
         dependencies=[], agent="backend"),
    Task("2.1.1", "GET /api/cart", "Cart retrieval endpoint", 1.5,
         dependencies=["2.3.1"], agent="backend"),
    Task("2.1.2", "PATCH cart item", "Update cart item quantity", 1,
         dependencies=["2.3.1"], agent="backend"),
    Task("1.1.1", "Cart item display", "Render cart items with prices", 2,
         dependencies=["2.1.1"], agent="frontend"),
    Task("1.3.2", "Stripe integration", "Payment processing backend", 4,
         dependencies=[], agent="backend", risk="high"),
    # ...
]
```

---

### 4. Critical Path Identification

```
CRITICAL PATH ANALYSIS
══════════════════════════════════════════════════════════════

The CRITICAL PATH is the longest sequence of dependent tasks.
It determines the MINIMUM total project duration.

Method: Find the longest path through the dependency graph
(weighted by estimated hours).

Path A: 2.3.1(2h) → 2.1.x(3h) → 1.1.x(6h) → 1.4.x(4h) → 3.x(6h) = 21h
Path B: 1.3.2(4h) → 1.3.x(5h) → 1.4.x(4h) → 3.x(6h) = 19h
Path C: 1.2.4(2h) → 1.2.x(4h) → 1.4.x(4h) → 3.x(6h) = 16h

CRITICAL PATH: Path A (21 hours)
                ▲
                │
Tasks on this path CANNOT be delayed without delaying
the entire project.

SLACK (Float):
  Path B slack: 21 - 19 = 2h (can be delayed up to 2h)
  Path C slack: 21 - 16 = 5h (can be delayed up to 5h)

OPTIMIZATION:
  → Add resources to critical path tasks
  → Break critical path tasks into smaller parallel pieces
  → Reduce dependencies to remove tasks from critical path
```

---

### 5. Effort Estimation

```
ESTIMATION TECHNIQUES
══════════════════════════════════════════════════════════════

1. T-SHIRT SIZING (quick, relative)
   XS = < 1 hour
   S  = 1-2 hours
   M  = 2-4 hours
   L  = 4-8 hours (half day to full day)
   XL = 8-16 hours (1-2 days) → DECOMPOSE FURTHER

2. THREE-POINT ESTIMATION (more accurate)
   Optimistic (O):  Best case, everything goes right
   Most Likely (M): Normal case, some minor issues
   Pessimistic (P): Worst case, major obstacles

   Estimate = (O + 4M + P) / 6
   Standard Deviation = (P - O) / 6

   Example — "Stripe Integration":
   O = 2h, M = 4h, P = 10h
   Estimate = (2 + 16 + 10) / 6 = 4.7h
   StdDev = (10 - 2) / 6 = 1.3h
   80% confidence: 4.7h ± 1.7h → 3.0h to 6.4h

3. COMPARISON-BASED
   "Similar to the PayPal integration (which took 6h)"
   Adjust for differences: +/- 20%

ESTIMATION RULES:
  □ Never estimate without understanding the task
  □ Include testing time in every estimate
  □ Add 20% buffer for unknowns
  □ If estimate > 8h, decompose further
  □ Track actual vs estimated to improve over time
```

---

### 6. Parallel vs Sequential Planning

```
PARALLEL VS SEQUENTIAL DECISION MATRIX
══════════════════════════════════════════════════════════════

Can run in PARALLEL when:
  ✓ No shared dependencies
  ✓ No shared state (different files/modules)
  ✓ Different agents/resources
  ✓ No communication needed during execution
  ✓ Independent test suites

Must run SEQUENTIALLY when:
  ✗ Output of task A is input of task B
  ✗ Both modify the same files
  ✗ Task B validates task A's output
  ✗ Shared database state
  ✗ API contract must be agreed first

EXECUTION PLAN FORMAT:
══════════════════════════════════════════════════════════════

Phase 1 (Parallel):                        Time: 4h
  ├── [backend]  2.3.1 Order model          2h
  ├── [backend]  1.3.2 Stripe integration   4h  ← longest
  └── [frontend] UI scaffolding             3h

Phase 2 (Parallel, after Phase 1):         Time: 3h
  ├── [backend]  2.1.x Cart API             3h
  ├── [backend]  1.2.4 Shipping API         2h
  └── [frontend] 1.2.x Shipping form        3h

Phase 3 (Parallel, after Phase 2):         Time: 6h
  ├── [frontend] 1.1.x Cart UI             6h  ← longest
  └── [frontend] 1.3.x Payment UI          5h

Phase 4 (Sequential):                     Time: 4h
  └── [frontend] 1.4.x Confirmation        4h

Phase 5 (Sequential):                     Time: 6h
  └── [all]      3.x Testing               6h

TOTAL: 23h elapsed (vs 39h sequential = 41% time savings)
```

---

### 7. Milestone Definition

```
MILESTONES
══════════════════════════════════════════════════════════════

A milestone is NOT a task — it's a checkpoint with verifiable criteria.

MILESTONE FORMAT:
  Name:     <descriptive name>
  After:    <which tasks must be complete>
  Criteria: <how to verify it's been reached>
  Gate:     <what decision is made at this point>

EXAMPLE MILESTONES — CHECKOUT SYSTEM:

M1: "API Foundation Complete"
  After:    2.3.1, 2.1.x, 1.2.4, 1.3.2
  Criteria: All API endpoints respond correctly to Postman/curl tests
  Gate:     Proceed to frontend integration

M2: "UI Integration Complete"
  After:    1.1.x, 1.2.x, 1.3.x, 1.4.x
  Criteria: Full checkout flow works in browser (manual test)
  Gate:     Proceed to automated testing

M3: "Testing Complete"
  After:    3.1-3.4
  Criteria: All tests pass, coverage > 80%, no critical bugs
  Gate:     Approve for staging deployment

M4: "Staging Verified"
  After:    3.5
  Criteria: Smoke tests pass on staging, PO signs off
  Gate:     Approve for production deployment
```

---

### 8. Risk Identification Per Subtask

```
RISK ASSESSMENT TEMPLATE
══════════════════════════════════════════════════════════════

Task: 1.3.2 Stripe Integration
Risk Level: HIGH
Risks:
  1. Stripe API changes between dev and deploy
     Probability: Low | Impact: High
     Mitigation: Pin API version, monitor Stripe changelog

  2. 3D Secure flow complexity
     Probability: High | Impact: Medium
     Mitigation: Use Stripe's prebuilt Payment Element

  3. Webhook configuration errors
     Probability: Medium | Impact: High
     Mitigation: Use Stripe CLI for local webhook testing

  4. PCI compliance requirements
     Probability: Low | Impact: Critical
     Mitigation: Use Stripe Elements (never handle raw card data)

RISK CATEGORIES:
  Technical:    Unknown technology, integration complexity
  Dependency:   Blocked by another task, external service
  Scope:        Requirements unclear or likely to change
  Resource:     Key person unavailable, skill gap
  Security:     Data handling, compliance requirements
  Performance:  Scale concerns, latency requirements
```

---

### 9. Resource Requirements

```
RESOURCE ALLOCATION TABLE
══════════════════════════════════════════════════════════════

Task          │ Agent/Role  │ Skills Required    │ Hours │ Phase
──────────────┼─────────────┼────────────────────┼───────┼──────
2.3.1         │ Backend     │ SQLAlchemy, Alembic│ 2     │ 1
2.1.x         │ Backend     │ FastAPI, REST      │ 3     │ 2
1.3.2         │ Backend     │ Stripe SDK, webhooks│ 4    │ 1
1.2.4         │ Backend     │ Shipping API       │ 2     │ 2
1.1.x         │ Frontend    │ React, Tailwind    │ 6     │ 3
1.2.x         │ Frontend    │ React, forms       │ 3     │ 2
1.3.x         │ Frontend    │ React, Stripe Elem.│ 5     │ 3
1.4.x         │ Frontend    │ React              │ 4     │ 4
3.1-3.4       │ Both        │ pytest, Playwright │ 6     │ 5
3.5           │ DevOps      │ Docker, deploy     │ 2     │ 5

TOTAL:
  Backend:  11h
  Frontend: 18h
  DevOps:   2h
  Bottleneck: Frontend (most hours, on critical path)
```

---

### 10. Decomposition Process

```
STEP-BY-STEP DECOMPOSITION PROCESS
══════════════════════════════════════════════════════════════

INPUT: Complex task description from user

Step 1: UNDERSTAND
  - What is the end goal?
  - What are the acceptance criteria?
  - What constraints exist (time, tech, team)?

Step 2: IDENTIFY MAJOR COMPONENTS
  - What are the 3-5 main areas of work?
  - Backend? Frontend? Infrastructure? Data?

Step 3: BREAK DOWN EACH COMPONENT
  - For each component, list specific deliverables
  - Keep breaking down until each task is 1-4 hours
  - Apply MECE principle

Step 4: MAP DEPENDENCIES
  - For each task: "What must finish before this can start?"
  - Draw the dependency graph
  - Identify parallel groups

Step 5: ESTIMATE & ALLOCATE
  - Assign effort estimates (use three-point if uncertain)
  - Assign agents/resources based on skills
  - Calculate critical path

Step 6: IDENTIFY RISKS & MILESTONES
  - Flag high-risk subtasks
  - Define verification milestones between phases
  - Add risk mitigations

Step 7: PRODUCE THE PLAN
  - Ordered list of phases with tasks
  - Total estimated time (parallel vs sequential)
  - Resource requirements
  - Risk register
```

---

## Best Practices

1. **Decompose recursively** — break big tasks into chunks, then chunks into atoms
2. **Target 1-4 hours per subtask** — smaller is easier to estimate and track
3. **Minimize dependencies** — restructure tasks to maximize parallelism
4. **Validate with MECE** — no overlap, no gaps in coverage
5. **Include testing in every task** — don't make "testing" a separate phase only
6. **Track actuals vs estimates** — calibrate future estimates from past data
7. **Identify the critical path** — focus resources and attention there
8. **Keep milestones actionable** — verifiable criteria, not vague checkpoints
9. **Document assumptions** — every estimate has assumptions, write them down
10. **Re-decompose when scope changes** — update the WBS, don't just add tasks

---

## Related Skills

- `multi-agent-coordinator` — execute the decomposed plan with multiple agents
- `agent-specialization` — match subtasks to the right specialist
- `parallel-execution` — run independent subtasks concurrently
