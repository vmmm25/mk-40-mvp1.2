---
name: multi-agent-coordinator
version: 1.0.0
description: >
  Central coordinator for multi-agent workflows. Handles task delegation to specialized sub-agents,
  result consolidation, conflict resolution, progress monitoring, error handling and retry,
  agent lifecycle management, inter-agent communication protocols, resource allocation, and
  priority queue management.
tags:
  - orchestration
  - multi-agent
  - coordinator
  - task-delegation
  - agent-lifecycle
  - conflict-resolution
  - priority-queue
  - communication-protocol
  - resource-allocation
  - workflow
author: garri333
license: MIT
source: Inspired by n-skills orchestration and Codex Desktop App multi-agent architecture
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# multi-agent-coordinator

Central coordinator that orchestrates multi-agent workflows. Delegate tasks to specialized sub-agents, consolidate results, resolve conflicts, monitor progress, handle errors with retry, manage agent lifecycles, and allocate resources through priority queues.

---

## When to Activate

Activate this skill when the user:

- Has a **complex task requiring multiple specialized agents**
- Wants to set up a **multi-agent workflow** or pipeline
- Needs to **coordinate work** between frontend, backend, and DevOps agents
- Asks about **agent communication** patterns or protocols
- Wants to **delegate subtasks** to different agents and merge results
- Needs **conflict resolution** when agents produce contradictory outputs
- Asks about **error handling** and retry strategies in agent pipelines
- Wants to **monitor progress** across multiple concurrent agents
- Needs **resource allocation** or priority management for agent tasks
- Uses keywords: `coordinate`, `orchestrate`, `multi-agent`, `delegate`, `pipeline`, `workflow`

---

## Step-by-Step Instructions

### 1. Coordinator Architecture

```
MULTI-AGENT COORDINATOR ARCHITECTURE
══════════════════════════════════════════════════════════════

                    ┌──────────────────┐
                    │   COORDINATOR    │
                    │                  │
                    │ • Task Queue     │
                    │ • Agent Registry │
                    │ • Result Store   │
                    │ • Conflict Mgr   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐ ┌────▼────────┐ ┌───▼──────────┐
     │   Frontend    │ │   Backend   │ │    DevOps    │
     │    Agent      │ │    Agent    │ │    Agent     │
     │              │ │             │ │              │
     │ • React/Vue  │ │ • API design│ │ • Docker     │
     │ • CSS/HTML   │ │ • Database  │ │ • CI/CD      │
     │ • Responsive │ │ • Auth/Sec  │ │ • Deploy     │
     └──────────────┘ └─────────────┘ └──────────────┘

COORDINATOR RESPONSIBILITIES:
1. Receive complex task from user
2. Decompose into subtasks (→ task-decomposition skill)
3. Assign subtasks to appropriate agents
4. Monitor execution and progress
5. Handle failures (retry, reassign, escalate)
6. Consolidate and validate results
7. Present unified output to user
```

---

### 2. Task Delegation

```yaml
# Task Delegation Protocol
delegation:
  task_id: "TASK-001"
  parent_task: null
  description: "Build user authentication system"
  subtasks:
    - id: "TASK-001-A"
      agent: "backend"
      description: "Implement JWT authentication API"
      priority: high
      dependencies: []
      inputs:
        - type: "specification"
          content: "REST API with /login, /register, /refresh endpoints"
      expected_outputs:
        - "API endpoint implementations"
        - "Database migration for users table"
        - "Unit tests with >80% coverage"
      timeout: "30m"

    - id: "TASK-001-B"
      agent: "frontend"
      description: "Build login and registration forms"
      priority: high
      dependencies: ["TASK-001-A"]  # Needs API spec first
      inputs:
        - type: "api_spec"
          source: "TASK-001-A"
      expected_outputs:
        - "Login page component"
        - "Registration page component"
        - "Auth context/provider"
      timeout: "25m"

    - id: "TASK-001-C"
      agent: "devops"
      description: "Configure auth secrets and environment"
      priority: medium
      dependencies: []
      inputs:
        - type: "requirement"
          content: "JWT_SECRET, token expiry, CORS origins"
      expected_outputs:
        - "Environment configuration"
        - "Docker compose updates"
        - "CI/CD secret management"
      timeout: "15m"
```

---

### 3. Agent Registry & Capability Matrix

```
AGENT CAPABILITY MATRIX
══════════════════════════════════════════════════════════════

Agent         │ Skills              │ Max Concurrent │ Priority
──────────────┼─────────────────────┼────────────────┼─────────
frontend      │ React, Vue, CSS,    │ 3              │ normal
              │ HTML, accessibility │                │
──────────────┼─────────────────────┼────────────────┼─────────
backend       │ Python, Node.js,    │ 3              │ normal
              │ SQL, REST, GraphQL  │                │
──────────────┼─────────────────────┼────────────────┼─────────
devops        │ Docker, CI/CD,      │ 2              │ normal
              │ Kubernetes, IaC     │                │
──────────────┼─────────────────────┼────────────────┼─────────
security      │ Auth, OWASP, audit, │ 1              │ high
              │ penetration testing │                │
──────────────┼─────────────────────┼────────────────┼─────────
docs          │ Technical writing,  │ 2              │ low
              │ API docs, guides    │                │
──────────────┼─────────────────────┼────────────────┼─────────

ROUTING RULES:
- Match task keywords to agent skills
- Prefer the most specialized agent
- Fall back to a generalist if no specialist available
- Never exceed max concurrent tasks per agent
```

---

### 4. Result Consolidation

```
RESULT CONSOLIDATION PROCESS
══════════════════════════════════════════════════════════════

1. COLLECT
   Wait for all subtasks to complete (or timeout)
   Record: output, duration, errors, warnings

2. VALIDATE
   Check each result against expected_outputs
   Verify no conflicts between agent outputs
   Run integration checks (do the pieces fit together?)

3. MERGE
   Combine code changes into unified changeset
   Resolve file conflicts (same file modified by 2 agents)
   Ensure consistent dependencies (package.json, requirements.txt)

4. VERIFY
   Run full test suite on merged result
   Check for import/reference errors
   Validate API contract between frontend and backend

5. PRESENT
   Summarize what was done and by which agent
   Highlight any issues or decisions that need user input
   Provide the unified deliverable
```

**Consolidation example:**

```python
class ResultConsolidator:
    def consolidate(self, results: list[AgentResult]) -> ConsolidatedResult:
        merged_files = {}
        conflicts = []
        warnings = []

        for result in results:
            for file_path, content in result.files.items():
                if file_path in merged_files:
                    # Conflict — same file modified by two agents
                    conflicts.append(FileConflict(
                        path=file_path,
                        agent_a=merged_files[file_path].agent,
                        agent_b=result.agent,
                        content_a=merged_files[file_path].content,
                        content_b=content,
                    ))
                else:
                    merged_files[file_path] = MergedFile(
                        content=content,
                        agent=result.agent,
                    )

        return ConsolidatedResult(
            files=merged_files,
            conflicts=conflicts,
            warnings=warnings,
            summary=self._generate_summary(results),
        )
```

---

### 5. Conflict Resolution

```
CONFLICT RESOLUTION STRATEGIES
══════════════════════════════════════════════════════════════

AUTOMATIC RESOLUTION:
1. NON-OVERLAPPING CHANGES → Auto-merge (like git merge)
2. ADDITIVE CHANGES → Combine (both add to package.json → merge)
3. PRIORITY-BASED → Higher-priority agent wins
4. DOMAIN AUTHORITY → Security agent wins security decisions,
                      Frontend agent wins UI decisions

REQUIRE HUMAN DECISION:
5. CONTRADICTORY DESIGNS → Present both options to user
6. BREAKING CHANGES → Flag for user review
7. AMBIGUOUS REQUIREMENTS → Ask user to clarify

CONFLICT LOG FORMAT:
┌─────────────────────────────────────────────────────────┐
│ CONFLICT: src/api/auth.py                               │
│ Agent A (backend): Uses bcrypt for password hashing     │
│ Agent B (security): Requires argon2id for hashing       │
│                                                         │
│ RESOLUTION: Accept Agent B (security has domain         │
│ authority over cryptographic decisions)                  │
│                                                         │
│ ACTION: Backend agent to update implementation          │
└─────────────────────────────────────────────────────────┘
```

---

### 6. Progress Monitoring

```
PROGRESS DASHBOARD
══════════════════════════════════════════════════════════════

Task: Build User Authentication System
Started: 2026-02-22 10:00
Elapsed: 12m 34s

Subtask                    Agent      Status      Progress
─────────────────────────────────────────────────────────────
TASK-001-A: JWT API        backend    ▓▓▓▓▓▓▓░░░  70%  Running
TASK-001-B: Login Forms    frontend   ░░░░░░░░░░   0%  Blocked (→A)
TASK-001-C: Auth Config    devops     ▓▓▓▓▓▓▓▓▓▓ 100%  ✓ Done (5m 12s)
TASK-001-D: Security Audit security   ░░░░░░░░░░   0%  Queued

Overall: ████████░░░░░░░░░░░░ 42%

Alerts:
  ⚠ TASK-001-A approaching timeout (18m/30m)
  ℹ TASK-001-C completed ahead of schedule

Estimated completion: 10:28 (~16 minutes remaining)
```

---

### 7. Error Handling & Retry

```python
class AgentErrorHandler:
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 15, 30]  # seconds

    async def execute_with_retry(self, agent, task):
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await agent.execute(task)
                if result.is_valid():
                    return result
                else:
                    raise InvalidResultError(result.errors)
            except AgentTimeoutError:
                if attempt < self.MAX_RETRIES - 1:
                    await self.log(f"Timeout on attempt {attempt+1}, retrying...")
                    task.timeout *= 1.5  # Increase timeout
                    await asyncio.sleep(self.RETRY_DELAYS[attempt])
                else:
                    return await self.escalate(task, "Timeout after all retries")
            except AgentCrashError as e:
                return await self.reassign(task, exclude_agent=agent)
            except InvalidResultError as e:
                if attempt < self.MAX_RETRIES - 1:
                    task.add_context(f"Previous attempt failed: {e}")
                    await asyncio.sleep(self.RETRY_DELAYS[attempt])
                else:
                    return await self.escalate(task, f"Invalid result: {e}")

    async def reassign(self, task, exclude_agent):
        """Find another capable agent when one fails."""
        available = self.registry.find_agents(
            skills=task.required_skills,
            exclude=[exclude_agent],
        )
        if available:
            return await self.execute_with_retry(available[0], task)
        return await self.escalate(task, "No available agents")

    async def escalate(self, task, reason):
        """Return partial results and ask user for guidance."""
        return EscalatedResult(task=task, reason=reason)
```

---

### 8. Communication Protocol Between Agents

```
INTER-AGENT MESSAGE FORMAT
══════════════════════════════════════════════════════════════

{
  "message_id": "msg-001",
  "from": "backend-agent",
  "to": "frontend-agent",
  "type": "api_contract",           // info | request | response | alert
  "timestamp": "2026-02-22T10:15:00Z",
  "payload": {
    "endpoint": "POST /api/auth/login",
    "request_body": {
      "email": "string",
      "password": "string"
    },
    "response_200": {
      "token": "string",
      "user": { "id": "number", "email": "string", "name": "string" }
    },
    "response_401": {
      "error": "string"
    }
  },
  "reply_to": null,
  "requires_ack": true
}

MESSAGE TYPES:
  info          → One-way notification
  request       → Requires a response
  response      → Reply to a request
  alert         → Urgent issue needing attention
  api_contract  → Shared API specification
  handoff       → Transferring task to another agent
```

---

### 9. Resource Allocation & Priority Queue

```
PRIORITY QUEUE MANAGEMENT
══════════════════════════════════════════════════════════════

Priority Levels:
  P0 — CRITICAL:  Security fixes, production incidents
  P1 — HIGH:      User-blocking features, failing CI
  P2 — NORMAL:    Standard feature work
  P3 — LOW:       Documentation, cleanup, nice-to-have

Queue Processing Rules:
  1. Always process higher priority first
  2. Within same priority: FIFO (first in, first out)
  3. P0 tasks can preempt running P2/P3 tasks
  4. P1 tasks can preempt running P3 tasks
  5. Never preempt a task that's >80% complete

Resource Limits:
  Total concurrent agents: 8
  Per-task memory limit: 2GB
  Per-task timeout: configurable (default 30m)
  Queue max depth: 100 tasks
```

---

### 10. Agent Lifecycle Management

```
AGENT LIFECYCLE
══════════════════════════════════════════════════════════════

  IDLE ──→ ASSIGNED ──→ RUNNING ──→ COMPLETED
    ↑          │            │           │
    │          │            ▼           │
    │          └── FAILED──→ RETRY ─────┘
    │                         │
    │                         ▼
    └────────── TERMINATED ←─ ESCALATED

States:
  IDLE:       Agent available, waiting for task
  ASSIGNED:   Task received, loading context
  RUNNING:    Actively working on task
  COMPLETED:  Task done, results submitted
  FAILED:     Task failed, error captured
  RETRY:      Failed task being retried
  ESCALATED:  All retries exhausted, needs human
  TERMINATED: Agent shut down (cleanup complete)

Health Checks:
  - Heartbeat every 30 seconds while RUNNING
  - Kill and restart after 3 missed heartbeats
  - Memory usage monitoring (restart if >90% limit)
```

---

## Best Practices

1. **Decompose first** — break complex tasks into clear subtasks before assigning
2. **Minimize dependencies** — prefer parallel-capable task graphs
3. **Define contracts** — agents should agree on interfaces before building
4. **Fail fast** — detect errors early and retry without wasting time
5. **Log everything** — every delegation, result, and conflict should be traceable
6. **Prefer domain authority** — let specialists make decisions in their domain
7. **Set realistic timeouts** — too short causes false failures, too long wastes time
8. **Consolidate incrementally** — merge results as they arrive, don't wait for all
9. **Keep the user informed** — provide progress updates for long workflows
10. **Design for partial success** — deliver what completed even if some tasks failed

---

## Related Skills

- `task-decomposition` — break complex tasks into assignable subtasks
- `agent-specialization` — configure specialized agents for each domain
- `parallel-execution` — run independent agent tasks simultaneously
- `open-source-maintainer` — coordinate agents for repo maintenance
