---
name: parallel-execution
version: 1.0.0
description: >
  Run multiple agent tasks simultaneously. Covers parallel task identification, race condition
  prevention, result merging strategies, progress aggregation, error isolation, resource
  contention management, timeout handling, and deadlock prevention.
tags:
  - orchestration
  - parallel-execution
  - concurrency
  - parallelism
  - race-conditions
  - result-merging
  - timeout
  - deadlock
  - resource-contention
  - progress-tracking
author: garri333
license: MIT
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# parallel-execution

Run multiple agent tasks simultaneously for maximum throughput. Identify parallelizable tasks, prevent race conditions, merge results safely, aggregate progress, isolate errors, manage resource contention, handle timeouts, and prevent deadlocks.

---

## When to Activate

Activate this skill when the user:

- Has **independent tasks** that can run at the same time
- Wants to **speed up a workflow** by parallelizing work
- Needs to understand **which tasks can run in parallel** safely
- Has **race conditions** or conflicts from parallel execution
- Needs a strategy for **merging results** from parallel tasks
- Wants to **track progress** across multiple concurrent operations
- Needs **error isolation** (one failure shouldn't crash everything)
- Has **timeout** or **deadlock** concerns with parallel work
- Uses keywords: `parallel`, `concurrent`, `simultaneous`, `speed up`, `race condition`, `merge`, `timeout`, `deadlock`

---

## Step-by-Step Instructions

### 1. Parallel Task Identification

```
PARALLELIZABILITY ASSESSMENT
══════════════════════════════════════════════════════════════

A task is SAFE to parallelize when it has:

1. NO DATA DEPENDENCY on other running tasks
   ✓ Task A reads file X, Task B reads file Y → SAFE
   ✗ Task A writes file X, Task B reads file X → UNSAFE

2. NO SHARED MUTABLE STATE
   ✓ Each task works on different files/tables → SAFE
   ✗ Both tasks modify the same config file → UNSAFE

3. NO ORDERING REQUIREMENT
   ✓ Tests for unrelated modules → SAFE
   ✗ Migration must run before seeding → UNSAFE

4. INDEPENDENT RESOURCES
   ✓ Each task uses its own database connection → SAFE
   ✗ Both tasks need exclusive lock on a table → UNSAFE

QUICK CHECK:
  "If I run ONLY Task B, ignoring Task A entirely,
   will Task B produce the correct result?"
  YES → Tasks are independent, can parallelize
  NO  → There's a dependency, must serialize
```

**Decision matrix:**

```
PARALLELIZATION DECISION MATRIX
══════════════════════════════════════════════════════════════

Task Pair                         │ Parallel? │ Reason
──────────────────────────────────┼───────────┼──────────────
Write frontend + Write backend    │ ✓ YES     │ Different files
Run unit tests + Run lint         │ ✓ YES     │ Read-only
Build Docker + Run tests          │ ✓ YES     │ Independent
Write code + Write tests for it   │ ✗ NO      │ Tests need code
Migrate DB + Seed DB              │ ✗ NO      │ Seed needs schema
Frontend + API it calls           │ ⚠ MAYBE   │ Need API contract first
Refactor module A + Refactor B    │ ⚠ MAYBE   │ If no shared imports
Write docs + Write code           │ ⚠ MAYBE   │ Docs may reference code
```

---

### 2. Race Condition Prevention

```
RACE CONDITION PREVENTION IN MULTI-AGENT SYSTEMS
══════════════════════════════════════════════════════════════

PROBLEM: Two agents modify the same resource simultaneously.

PREVENTION STRATEGIES:

1. FILE LOCKING
   Before modifying a file, agent acquires a lock.
   Other agents wait until the lock is released.

   lock_manager.acquire("package.json")
   try:
       # modify package.json
   finally:
       lock_manager.release("package.json")

2. WORK PARTITIONING
   Divide the workspace so agents never touch the same files.
   Agent A: src/components/**
   Agent B: src/api/**
   Agent C: tests/**

3. SEQUENTIAL MERGE PHASE
   Agents work on separate branches/copies.
   Coordinator merges results sequentially.
   Like git: each agent works on a branch, merge at the end.

4. OPTIMISTIC CONCURRENCY
   Agents work freely, detect conflicts after.
   If conflict detected: retry the conflicting task.

5. COORDINATION MESSAGES
   Agent A tells Agent B: "I'm modifying the User model"
   Agent B avoids User model until A signals completion.
```

**Implementation:**

```python
import asyncio
from asyncio import Lock
from collections import defaultdict

class ResourceLockManager:
    """Prevents race conditions by locking shared resources."""

    def __init__(self):
        self._locks: dict[str, Lock] = defaultdict(Lock)
        self._owners: dict[str, str] = {}

    async def acquire(self, resource: str, agent_id: str, timeout: float = 30.0):
        try:
            await asyncio.wait_for(
                self._locks[resource].acquire(), timeout=timeout
            )
            self._owners[resource] = agent_id
            return True
        except asyncio.TimeoutError:
            raise ResourceContentionError(
                f"Agent {agent_id} timed out waiting for {resource} "
                f"(held by {self._owners.get(resource, 'unknown')})"
            )

    def release(self, resource: str, agent_id: str):
        if self._owners.get(resource) != agent_id:
            raise PermissionError(f"Agent {agent_id} doesn't own lock on {resource}")
        del self._owners[resource]
        self._locks[resource].release()
```

---

### 3. Result Merging Strategies

```
RESULT MERGING STRATEGIES
══════════════════════════════════════════════════════════════

STRATEGY 1: INDEPENDENT FILES (simplest)
  Each agent produces different files → just combine all files.
  Conflict probability: 0%
  Use when: Agents work on completely different areas.

STRATEGY 2: SECTION MERGING
  Both agents modify the same file but different sections.
  Use line-range tracking to merge non-overlapping changes.
  Conflict probability: Low
  Use when: Agents add to different parts of config files.

STRATEGY 3: SEMANTIC MERGING
  Understand the FILE FORMAT to merge intelligently.
  Example: Both agents add dependencies to package.json
  → Merge the "dependencies" objects.
  Conflict probability: Medium
  Use when: Structured files (JSON, YAML, TOML).

STRATEGY 4: THREE-WAY MERGE
  Like git merge: use the common ancestor to resolve.
  Agent A's changes + Agent B's changes vs original.
  Conflict probability: Medium
  Use when: Both agents modify the same code file.

STRATEGY 5: PRIORITY-BASED
  When conflict is irreconcilable, higher-priority agent wins.
  Security > Backend > Frontend > Docs
  Conflict probability: Any
  Use when: Semantic merge fails.
```

**Semantic merge for `package.json`:**

```python
import json

def merge_package_json(original: dict, agent_a: dict, agent_b: dict) -> dict:
    """Merge two agents' modifications to package.json."""
    result = json.loads(json.dumps(original))  # deep copy

    mergeable_keys = ["dependencies", "devDependencies", "scripts"]

    for key in mergeable_keys:
        orig = original.get(key, {})
        a_changes = agent_a.get(key, {})
        b_changes = agent_b.get(key, {})

        # Find what each agent added/changed
        a_new = {k: v for k, v in a_changes.items() if orig.get(k) != v}
        b_new = {k: v for k, v in b_changes.items() if orig.get(k) != v}

        # Check for conflicts (same key, different values)
        conflicts = {
            k for k in a_new if k in b_new and a_new[k] != b_new[k]
        }
        if conflicts:
            raise MergeConflict(f"Conflicting versions for: {conflicts}")

        # Merge
        merged = {**orig, **a_new, **b_new}
        result[key] = merged

    return result
```

---

### 4. Progress Aggregation

```
PROGRESS AGGREGATION DASHBOARD
══════════════════════════════════════════════════════════════

OPTION 1: SIMPLE PERCENTAGE (weighted by estimated effort)

  Task A (est. 4h): ████████░░ 80%  (3.2h / 4h)
  Task B (est. 2h): ██████████ 100% (done)
  Task C (est. 6h): ███░░░░░░░ 30%  (1.8h / 6h)
  ─────────────────────────────────
  Overall: (3.2 + 2 + 1.8) / (4 + 2 + 6) = 58%


OPTION 2: PHASE-BASED

  Phase 1: ████████████████████ COMPLETE ✓
  Phase 2: ████████████░░░░░░░░ IN PROGRESS (60%)
  Phase 3: ░░░░░░░░░░░░░░░░░░░ NOT STARTED
  Phase 4: ░░░░░░░░░░░░░░░░░░░ NOT STARTED
  ─────────────────────────────────
  Overall: Phase 2 of 4 (40% of phases)


OPTION 3: TASK COUNT

  Completed:   8 / 20 tasks (40%)
  In Progress: 3 / 20 tasks
  Blocked:     1 / 20 tasks ⚠
  Not Started: 8 / 20 tasks
```

```python
class ProgressAggregator:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks

    def overall_progress(self) -> float:
        total_weight = sum(t.estimated_hours for t in self.tasks)
        completed_weight = sum(
            t.estimated_hours * t.progress
            for t in self.tasks
        )
        return completed_weight / total_weight if total_weight > 0 else 0

    def summary(self) -> dict:
        return {
            "total": len(self.tasks),
            "completed": sum(1 for t in self.tasks if t.status == "done"),
            "in_progress": sum(1 for t in self.tasks if t.status == "running"),
            "blocked": sum(1 for t in self.tasks if t.status == "blocked"),
            "failed": sum(1 for t in self.tasks if t.status == "failed"),
            "overall_progress": f"{self.overall_progress():.0%}",
            "estimated_remaining": self._estimate_remaining(),
        }

    def _estimate_remaining(self) -> str:
        remaining_hours = sum(
            t.estimated_hours * (1 - t.progress)
            for t in self.tasks
            if t.status in ("pending", "running")
        )
        return f"{remaining_hours:.1f}h"
```

---

### 5. Error Isolation

```
ERROR ISOLATION STRATEGIES
══════════════════════════════════════════════════════════════

PRINCIPLE: One task's failure should NOT cascade to others.

1. INDEPENDENT FAILURE DOMAINS
   Each task runs in its own context (process, container, branch).
   Failure is contained — other tasks continue unaffected.

2. BULKHEAD PATTERN
   Limit the blast radius:
   - Agent A crashes → only Agent A's tasks are affected
   - Agent B and C continue working
   - Coordinator marks A's tasks as failed and decides retry

3. CIRCUIT BREAKER
   If an agent fails N times in a row, stop sending it tasks.
   - Closed:  Normal operation, tasks are sent
   - Open:    Agent failing, tasks are rerouted
   - Half-Open: Test with one task, if it passes → close

4. PARTIAL SUCCESS HANDLING
   If 3 of 4 parallel tasks succeed:
   - Deliver the 3 successful results
   - Report the failure separately
   - Ask: retry failed task? skip it? substitute?
```

```python
class ParallelExecutor:
    async def execute_all(self, tasks: list[Task]) -> ExecutionResult:
        results = await asyncio.gather(
            *[self._execute_isolated(t) for t in tasks],
            return_exceptions=True  # Don't let one failure cancel others
        )

        successes = []
        failures = []

        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                failures.append(TaskFailure(task=task, error=result))
            else:
                successes.append(TaskSuccess(task=task, output=result))

        return ExecutionResult(
            successes=successes,
            failures=failures,
            all_succeeded=len(failures) == 0,
        )

    async def _execute_isolated(self, task: Task):
        """Execute a single task with full isolation."""
        try:
            return await asyncio.wait_for(
                self._run_task(task),
                timeout=task.timeout_seconds,
            )
        except asyncio.TimeoutError:
            raise TaskTimeoutError(f"Task {task.id} timed out after {task.timeout_seconds}s")
        except Exception as e:
            raise TaskExecutionError(f"Task {task.id} failed: {e}") from e
```

---

### 6. Resource Contention Management

```
RESOURCE CONTENTION MANAGEMENT
══════════════════════════════════════════════════════════════

SHARED RESOURCES IN AGENT SYSTEMS:
  - Files in the workspace
  - Database connections
  - API rate limits
  - CPU / memory quotas
  - Network bandwidth
  - External service endpoints

CONTENTION RESOLUTION:

1. RESOURCE POOLING
   Create a pool of N resources, agents check them out/in.
   If pool exhausted → agent waits or is queued.

2. TIME SLICING
   Agent A uses resource for 5 minutes, then Agent B.
   Fair but slow — use only for exclusive resources.

3. SHARDING
   Divide the resource: Agent A gets users A-M, Agent B gets N-Z.
   No contention because no overlap.

4. RATE LIMITING
   External API allows 100 req/s.
   With 4 agents: each gets 25 req/s quota.
   Coordinator tracks total usage across agents.

5. COPY-ON-WRITE
   Each agent gets a copy of the resource (e.g., branch).
   Changes are merged after all agents finish.
   Best for file-system resources.
```

---

### 7. Timeout Handling

```
TIMEOUT STRATEGIES
══════════════════════════════════════════════════════════════

TIMEOUT TYPES:

1. TASK TIMEOUT
   Maximum time for a single task.
   Default: 30 minutes (configurable per task)
   On timeout: Cancel task, report partial results if any.

2. PHASE TIMEOUT
   Maximum time for all parallel tasks in a phase.
   Default: max(task timeouts) × 1.5
   On timeout: Cancel remaining tasks, proceed with completed.

3. OVERALL TIMEOUT
   Maximum time for the entire workflow.
   Default: sum of phase timeouts (sequential estimate)
   On timeout: Report what's done, save state for resumption.

TIMEOUT ACTIONS:
  ┌─────────────┐
  │ Timeout!    │
  └──────┬──────┘
         │
    ┌────▼────┐     YES    ┌────────────┐
    │ Retry?  ├────────────► Retry with  │
    │ count<3 │            │ 1.5x timeout│
    └────┬────┘            └────────────┘
         │ NO
    ┌────▼─────┐    YES    ┌─────────────┐
    │ Partial  ├───────────► Return what  │
    │ results? │           │ we have      │
    └────┬─────┘           └─────────────┘
         │ NO
    ┌────▼─────┐
    │ Escalate │  Ask user what to do
    └──────────┘
```

```python
class TimeoutManager:
    def __init__(self):
        self.default_task_timeout = 30 * 60   # 30 minutes
        self.default_phase_timeout = 45 * 60  # 45 minutes

    async def run_with_timeout(self, coro, timeout: float, task_id: str):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            return TimeoutResult(
                task_id=task_id,
                timeout_seconds=timeout,
                action="retry" if self._should_retry(task_id) else "escalate"
            )

    async def run_phase_with_timeout(self, tasks, phase_timeout: float):
        """Run parallel tasks with a phase-level timeout."""
        done, pending = await asyncio.wait(
            [asyncio.create_task(self._run_task(t)) for t in tasks],
            timeout=phase_timeout,
            return_when=asyncio.ALL_COMPLETED,
        )

        results = [d.result() for d in done]
        timed_out = [self._get_task_id(p) for p in pending]

        for p in pending:
            p.cancel()

        return PhaseResult(
            completed=results,
            timed_out=timed_out,
        )
```

---

### 8. Deadlock Prevention

```
DEADLOCK CONDITIONS (ALL 4 must be present):
══════════════════════════════════════════════════════════════

1. MUTUAL EXCLUSION   — Resource can only be held by one agent
2. HOLD AND WAIT      — Agent holds resources while waiting for more
3. NO PREEMPTION      — Resources can't be forcibly taken
4. CIRCULAR WAIT      — A waits for B, B waits for A

PREVENT ANY ONE CONDITION TO PREVENT DEADLOCK:

Strategy 1: LOCK ORDERING
  All agents acquire locks in the same global order.
  E.g., always lock "package.json" before "tsconfig.json"
  → Prevents circular wait

Strategy 2: TIMEOUT AND RETRY
  If an agent can't get a lock within N seconds, release all
  held locks and retry from scratch.
  → Prevents hold and wait

Strategy 3: TRY-LOCK
  Attempt to acquire lock without blocking.
  If unavailable: release all locks, back off, retry.
  → Prevents hold and wait

Strategy 4: SINGLE LOCK GRANULARITY
  One global lock instead of fine-grained locks.
  Simple but limits parallelism.
  → Prevents circular wait (trivially)

Strategy 5: RESOURCE HIERARCHY
  Assign a number to each resource. Agents can only acquire
  resources with higher numbers than what they already hold.
  → Prevents circular wait

DETECTION:
  Monitor for agents stuck in "waiting" state > timeout.
  Build a wait-for graph: if it has a cycle → deadlock.
  Coordinator can break deadlock by killing one agent's task.
```

---

## Execution Patterns

### Fan-Out / Fan-In

```
FAN-OUT / FAN-IN PATTERN
══════════════════════════════════════════════════════════════

       ┌── Agent A ──┐
       │             │
Input ─┼── Agent B ──┼── Merge → Output
       │             │
       └── Agent C ──┘

1. COORDINATOR receives complex task
2. FAN-OUT: Split into N independent subtasks
3. EXECUTE: All N agents work in parallel
4. FAN-IN: Collect all results
5. MERGE: Combine into unified output
6. VALIDATE: Ensure merged result is consistent
```

### Pipeline with Parallel Stages

```
PIPELINE WITH PARALLEL STAGES
══════════════════════════════════════════════════════════════

Stage 1          Stage 2              Stage 3
(sequential)     (parallel)           (sequential)

┌──────────┐     ┌── Frontend ──┐     ┌──────────┐
│ Design   │     │              │     │ Test     │
│ API Spec ├────►├── Backend  ──├────►│ & Deploy │
│          │     │              │     │          │
└──────────┘     └── DevOps  ──┘     └──────────┘
```

---

## Best Practices

1. **Default to sequential** — only parallelize when you've confirmed independence
2. **Partition work cleanly** — non-overlapping file sets eliminate most conflicts
3. **Use copy-on-write** — let agents work on branches, merge at the end
4. **Set aggressive timeouts** — it's better to retry fast than wait forever
5. **Isolate failures** — use `return_exceptions=True` in asyncio.gather
6. **Track resource ownership** — know which agent holds which lock
7. **Prefer lock ordering over detection** — prevention is simpler than cure
8. **Aggregate progress in real time** — users need visibility into parallel work
9. **Limit parallel degree** — diminishing returns beyond 3-4 concurrent agents
10. **Test parallel execution** — run your workflow 10x to find intermittent failures

---

## Related Skills

- `task-decomposition` — identify which tasks can run in parallel
- `multi-agent-coordinator` — orchestrate parallel agent workflows
- `agent-specialization` — assign parallel tasks to the right specialists
- `systematic-debugging` — debug race conditions and deadlocks
