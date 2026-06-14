---
name: systematic-debugging
version: 1.0.0
description: >
  Structured debugging methodology for finding and fixing software defects efficiently.
  Covers the Reproduce → Isolate → Fix → Verify cycle, binary search for bug isolation,
  log analysis, stack trace interpretation, memory leak detection, race condition identification,
  performance profiling, git bisect, breakpoint strategies, and hypothesis-driven debugging.
tags:
  - debugging
  - troubleshooting
  - bug-fixing
  - log-analysis
  - profiling
  - git-bisect
  - memory-leaks
  - race-conditions
  - stack-traces
  - performance
author: garri333
license: MIT
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# systematic-debugging

Structured debugging methodology for diagnosing, isolating, and resolving software defects efficiently. Apply the scientific method to bugs: hypothesize, test, observe, conclude.

---

## When to Activate

Activate this skill when the user:

- Reports a **bug** they cannot find the cause of
- Sees an **error message or stack trace** they don't understand
- Has a **flaky test** or intermittent failure
- Suspects a **memory leak** or resource exhaustion
- Encounters a **race condition** or concurrency bug
- Needs to **profile performance** or find bottlenecks
- Wants to use **git bisect** to find a regression
- Asks for a **debugging strategy** or systematic approach
- Has a production incident and needs to **root-cause** it
- Uses keywords: `debug`, `bug`, `trace`, `error`, `crash`, `regression`, `leak`, `deadlock`, `flaky`

---

## Step-by-Step Instructions

### 1. The Reproduce → Isolate → Fix → Verify Cycle

```
THE DEBUGGING CYCLE
══════════════════════════════════════════════════════════════

  ┌──────────────┐
  │  REPRODUCE   │  Make the bug happen reliably
  │              │  Document exact steps, inputs, environment
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │   ISOLATE    │  Narrow down to the smallest failing case
  │              │  Binary search, divide & conquer
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │     FIX      │  Apply the minimal correct fix
  │              │  Understand WHY it broke, not just WHAT
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │    VERIFY    │  Confirm fix works AND nothing else broke
  │              │  Add regression test
  └──────────────┘
```

**Step 1 — Reproduce:**
- Get the exact error message, screenshot, or log output
- Reproduce in your local environment with same data/config
- Document: OS, runtime version, browser, database state
- If intermittent: run in a loop (`for i in {1..100}; do pytest test_x.py; done`)

**Step 2 — Isolate:**
- Strip away unrelated code, dependencies, and data
- Create a minimal reproduction case (MRE / MCVE)
- Use binary search to narrow the code path (see Section 2)

**Step 3 — Fix:**
- Understand the root cause, not just the symptom
- Apply the smallest correct change
- Check: does this fix create new edge cases?

**Step 4 — Verify:**
- Run the original reproduction steps — bug must be gone
- Run the full test suite — no regressions
- Write a regression test encoding the exact failure condition

---

### 2. Binary Search for Bug Isolation

When the bug is somewhere in a large codebase but you don't know where:

```
BINARY SEARCH DEBUGGING
══════════════════════════════════════════════════════════════

Code path: A → B → C → D → E → F → G → H

Step 1: Add assertion/log at midpoint (D)
        Is state correct at D?

  YES → Bug is in E..H         NO → Bug is in A..D
        Test midpoint F              Test midpoint B

  Continue halving until you find the exact transition
  from "state OK" to "state broken"

Result: O(log n) steps instead of O(n)
```

**Practical application:**

```python
# Add checkpoints to narrow the bug
def process_order(order):
    validated = validate(order)
    assert validated.total > 0, f"Checkpoint 1 FAIL: total={validated.total}"

    enriched = enrich_with_pricing(validated)
    assert enriched.line_items, f"Checkpoint 2 FAIL: no line items"

    discounted = apply_discounts(enriched)
    assert discounted.total <= enriched.total, f"Checkpoint 3 FAIL: discount increased total"

    result = save_to_db(discounted)
    assert result.id, f"Checkpoint 4 FAIL: no ID returned"

    return result
```

---

### 3. Log Analysis Patterns

```
LOG ANALYSIS CHECKLIST
══════════════════════════════════════════════════════════════

1. TIMELINE RECONSTRUCTION
   - Sort by timestamp
   - Correlate events across services (use request IDs)
   - Identify the FIRST error, not the cascade

2. PATTERN RECOGNITION
   - Search for ERROR, WARN, Exception, Traceback
   - Look for repeated patterns (same error every N minutes?)
   - Check for resource exhaustion: "out of memory", "too many open files"
   - Look for timeout patterns

3. DIFF AGAINST WORKING STATE
   - Compare logs from a working period vs broken period
   - What changed? New log lines? Missing log lines?
   - Check deploy timestamps against error onset

4. USEFUL COMMANDS
   grep -i "error\|exception\|fatal" app.log | head -50
   grep -B5 -A10 "NullPointerException" app.log
   awk '/2026-02-22 14:00/,/2026-02-22 14:30/' app.log
   sort app.log | uniq -c | sort -rn | head -20
   jq 'select(.level == "error")' structured.log
```

---

### 4. Stack Trace Interpretation

```
READING A STACK TRACE
══════════════════════════════════════════════════════════════

Traceback (most recent call last):        ← Read BOTTOM-UP
  File "main.py", line 42, in main        ← Entry point (least useful)
    result = process(data)
  File "processor.py", line 87, in process
    transformed = transform(item)
  File "transform.py", line 15, in transform
    return item.value.strip()             ← THE BUG IS HERE
AttributeError: 'NoneType' object has no attribute 'strip'
                                          ↑ Read this FIRST

STRATEGY:
1. Read the EXCEPTION TYPE and MESSAGE first (bottom)
2. Find YOUR code in the trace (skip framework internals)
3. Look at the exact line — what assumption failed?
4. Check: what value was None/null that shouldn't have been?
```

**Common exception patterns:**

| Exception | Likely Cause | Fix Strategy |
|-----------|-------------|--------------|
| `NullPointerException` / `AttributeError: NoneType` | Missing null check | Add guard clause or fix data source |
| `IndexError` / `ArrayIndexOutOfBounds` | Off-by-one or empty collection | Check length before access |
| `KeyError` / `undefined` | Missing dictionary/object key | Use `.get()` with default or validate schema |
| `TimeoutError` | Slow dependency or deadlock | Add timeout, check for blocking calls |
| `ConnectionRefused` | Service down or wrong port | Check service health, verify config |
| `PermissionError` / `AccessDenied` | File/resource permissions | Check file ownership, IAM policies |

---

### 5. Memory Leak Detection

```python
# Python — tracemalloc
import tracemalloc

tracemalloc.start()
# ... run suspected leaking code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory consumers:")
for stat in top_stats[:10]:
    print(stat)
```

```javascript
// Node.js — heap snapshot
const v8 = require('v8');
const fs = require('fs');

// Take heap snapshots at intervals and compare
function takeHeapSnapshot(label) {
  const snapshotStream = v8.writeHeapSnapshot();
  console.log(`Heap snapshot written to ${snapshotStream} [${label}]`);
}

// Compare object counts between snapshots in Chrome DevTools
```

**Memory leak indicators:**

```
MEMORY LEAK SIGNALS
══════════════════════════════════════════════════════════════
✗ Memory usage grows continuously over time (sawtooth = normal GC)
✗ Process gets OOM-killed periodically
✗ Response times degrade over hours/days
✗ Heap dumps show growing collections (maps, lists, caches)

COMMON CAUSES:
- Event listeners added but never removed
- Growing caches without eviction policy
- Closures capturing large objects
- Circular references preventing GC
- Unclosed database connections or file handles
- Global state accumulation
```

---

### 6. Race Condition Identification

```
RACE CONDITION SYMPTOMS
══════════════════════════════════════════════════════════════
✗ Bug only appears under load or concurrent access
✗ Test passes when run alone, fails in parallel
✗ "Works on my machine" — depends on timing
✗ Adding a print/log statement makes the bug disappear
✗ Non-deterministic output for same input

DETECTION STRATEGIES:
1. Run tests in parallel repeatedly
2. Add artificial delays (sleep) at suspected race points
3. Use thread sanitizers: -fsanitize=thread (C/C++), go run -race
4. Check for shared mutable state without synchronization
5. Look for check-then-act patterns (TOCTOU)

COMMON PATTERNS:
- Read-modify-write without locks
- Lazy initialization in multi-threaded context
- Event ordering assumptions
- Double-checked locking (done wrong)
```

```python
# Python — detect race conditions with threading stress test
import threading
import concurrent.futures

counter = 0  # Shared mutable state — DANGER

def increment():
    global counter
    for _ in range(100_000):
        counter += 1  # NOT atomic — race condition

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(increment) for _ in range(4)]
    concurrent.futures.wait(futures)

print(f"Expected: 400000, Got: {counter}")  # Will be less!
```

---

### 7. Performance Profiling

```python
# Python — cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions by cumulative time
```

```bash
# Node.js
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Browser — Lighthouse
npx lighthouse http://localhost:3000 --view
```

```
PERFORMANCE PROFILING CHECKLIST
══════════════════════════════════════════════════════════════
1. MEASURE FIRST — never optimize without profiling data
2. Find the HOTSPOT — 80% of time is in 20% of code
3. Check I/O first — database queries, network calls, file reads
4. Look for N+1 queries — fetching related data in loops
5. Check memory allocation — excessive object creation in loops
6. Verify algorithm complexity — O(n²) hidden in innocent-looking code
7. Profile in PRODUCTION-LIKE conditions (data size, concurrency)
```

---

### 8. Git Bisect for Regression Finding

```bash
# Start bisect
git bisect start

# Mark current (broken) commit as bad
git bisect bad

# Mark a known working commit as good
git bisect good v2.3.0   # or a specific commit hash

# Git checks out midpoint — test and report
# If the bug is present:
git bisect bad
# If the bug is NOT present:
git bisect good

# Repeat until git identifies the first bad commit
# Typically finds it in ~10 steps for 1000 commits

# Automated bisect with a test script
git bisect start HEAD v2.3.0
git bisect run pytest tests/test_specific.py -x

# When done
git bisect reset
```

---

### 9. Breakpoint Strategies

```
BREAKPOINT TYPES AND WHEN TO USE THEM
══════════════════════════════════════════════════════════════

CONDITIONAL BREAKPOINT
  Break only when: user_id == "problem_user"
  Use when: bug only happens for specific data

LOGPOINT (non-breaking)
  Log a message without stopping: "Value of x: {x}"
  Use when: you need to trace flow without interrupting

DATA BREAKPOINT (watchpoint)
  Break when variable changes value
  Use when: "something is modifying this value and I don't know what"

EXCEPTION BREAKPOINT
  Break when any/specific exception is thrown
  Use when: exception is caught and swallowed somewhere

HIT COUNT BREAKPOINT
  Break on the Nth hit (e.g., 100th iteration)
  Use when: bug appears only after many iterations

FUNCTION BREAKPOINT
  Break when a function is entered (by name)
  Use when: you don't have the source file open
```

---

### 10. Hypothesis-Driven Debugging

```
THE SCIENTIFIC METHOD FOR DEBUGGING
══════════════════════════════════════════════════════════════

1. OBSERVE      What exactly is the incorrect behavior?
                What is the expected behavior?

2. HYPOTHESIZE  "I believe the bug is caused by ___
                 because ___"

3. PREDICT      "If my hypothesis is correct, then when I
                 do ___, I should see ___"

4. EXPERIMENT   Run the test. Log the result.

5. CONCLUDE     Hypothesis confirmed → investigate deeper
                Hypothesis rejected → form new hypothesis

DOCUMENT EACH CYCLE:
┌─────────────────────────────────────────────────────┐
│ Hypothesis #3: The cache returns stale data after   │
│ invalidation because TTL is checked before delete.  │
│                                                     │
│ Test: Set TTL to 1s, delete key, read immediately.  │
│ Prediction: Should get stale data.                  │
│ Result: Got None — hypothesis REJECTED.             │
│                                                     │
│ New direction: Problem is not in cache layer.        │
└─────────────────────────────────────────────────────┘
```

---

### 11. Rubber Duck Debugging

When you're stuck, explain the problem aloud (or in writing) step by step:

1. **State the problem clearly** — "The function returns 0 instead of the sum"
2. **Walk through the code line by line** — explain what each line does
3. **State your assumptions** — "I assume `items` is never empty"
4. **Challenge each assumption** — "But what if `items` IS empty?"
5. **The act of explaining often reveals the gap in your reasoning**

This works because:
- It forces you to slow down and be precise
- It exposes unstated assumptions
- It shifts from "reading" mode to "explaining" mode

---

### 12. Debug vs Release Build Differences

```
COMMON DEBUG vs RELEASE DISCREPANCIES
══════════════════════════════════════════════════════════════
Issue                    Debug              Release
─────────────────────────────────────────────────────────────
Optimization            Off (O0)           On (O2/O3)
Assertions              Enabled            Disabled
Variable initialization Zeroed by luck     Uninitialized/random
Timing                  Slow               Fast (hides races)
Memory layout           Padded             Compact
Stack frames            Full               Inlined/removed

IF BUG ONLY APPEARS IN RELEASE:
→ Uninitialized variable
→ Race condition (timing-dependent)
→ Removed assertion was catching it
→ Optimizer eliminated "dead" code that had side effects
→ Different memory layout exposes a buffer overrun
```

---

## Best Practices

1. **Reproduce first** — never try to fix a bug you can't reproduce
2. **One change at a time** — change one thing, test, then change the next
3. **Read the error message** — the answer is often in the first line
4. **Check the recent changes** — `git log --oneline -20` and `git diff`
5. **Question your assumptions** — the bug is usually where you're NOT looking
6. **Use version control** — commit before debugging so you can reset
7. **Take breaks** — fresh eyes find bugs faster than tired eyes
8. **Write it down** — document what you've tried so you don't repeat
9. **Ask for help after 30 minutes of being stuck** — fresh perspective helps
10. **Add a regression test** — every bug fix should include a test

---

## Related Skills

- `testing-anti-patterns` — avoid creating hard-to-debug tests
- `code-quality-audit` — proactively find issues before they become bugs
- `webapp-testing-playwright` — debug E2E test failures
