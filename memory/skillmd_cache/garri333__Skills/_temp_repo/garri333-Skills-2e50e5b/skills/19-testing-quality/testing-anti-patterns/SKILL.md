---
name: testing-anti-patterns
version: 1.0.0
description: >
  Catalog of common testing mistakes and how to avoid them. Covers flaky test detection and
  prevention, over-mocking, testing implementation instead of behavior, slow test suites,
  missing edge cases, snapshot testing abuse, test coupling, assertion roulette, eager test
  setup, mystery guest, and test parallelization pitfalls.
tags:
  - testing
  - anti-patterns
  - flaky-tests
  - test-quality
  - mocking
  - test-design
  - code-smell
  - best-practices
author: garri333
license: MIT
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# testing-anti-patterns

Identify and eliminate common testing mistakes that make test suites unreliable, slow, fragile, or meaningless. Each anti-pattern includes detection signals, examples of bad and good code, and remediation strategies.

---

## When to Activate

Activate this skill when the user:

- Has **flaky tests** that pass and fail randomly
- Complains that tests are **too slow** or **hard to maintain**
- Asks why tests **break on every refactor** even when behavior doesn't change
- Wants to **review test quality** or audit their test suite
- Has tests that pass but **bugs still reach production**
- Is **over-mocking** and getting false confidence
- Asks about **test design patterns** and best practices
- Wants to **parallelize tests** but they fail when run concurrently
- Uses keywords: `flaky`, `brittle test`, `test smell`, `slow tests`, `mock`, `snapshot`, `test quality`

---

## Anti-Pattern Catalog

### 1. Flaky Tests

**Signal:** Test passes and fails without code changes. CI shows intermittent red.

```
FLAKY TEST ROOT CAUSES
══════════════════════════════════════════════════════════════
1. Time-dependent logic       → Use clock mocking (fake timers)
2. Random/non-deterministic   → Seed random generators
3. Shared mutable state       → Isolate test state
4. Network calls              → Mock external services
5. Race conditions            → Add proper synchronization
6. Order-dependent tests      → Each test must be independent
7. Filesystem assumptions     → Use temp directories
8. Port conflicts             → Use dynamic port allocation
9. Timezone assumptions       → Explicitly set timezone in tests
10. Floating point comparison → Use approximate assertions
```

**Bad — time-dependent:**
```python
def test_token_expiry():
    token = create_token(expires_in=timedelta(seconds=1))
    time.sleep(1.1)  # Flaky! Depends on CPU speed
    assert token.is_expired()
```

**Good — freeze time:**
```python
from freezegun import freeze_time

def test_token_expiry():
    with freeze_time("2026-01-01 12:00:00"):
        token = create_token(expires_in=timedelta(hours=1))

    with freeze_time("2026-01-01 13:00:01"):
        assert token.is_expired()
```

**Detection strategy:**
```bash
# Run the same test 100 times to detect flakiness
pytest tests/test_suspect.py --count=100 -x  # with pytest-repeat
```

---

### 2. Over-Mocking

**Signal:** Tests pass but bugs reach production. Mocks don't reflect real behavior. Refactoring mocks takes longer than refactoring the code.

**Bad — mocking everything:**
```python
def test_create_user():
    mock_db = Mock()
    mock_validator = Mock(return_value=True)
    mock_hasher = Mock(return_value="hashed")
    mock_emailer = Mock()

    service = UserService(mock_db, mock_validator, mock_hasher, mock_emailer)
    service.create_user("test@example.com", "password")

    mock_db.save.assert_called_once()  # Tests implementation, not behavior
    mock_hasher.hash.assert_called_with("password")
    # What if the REAL hasher fails on empty strings?
    # What if the REAL db rejects duplicate emails?
    # This test tells you NOTHING about correctness.
```

**Good — mock only external boundaries:**
```python
def test_create_user(test_db):
    """Use a real database (SQLite in-memory) and real validator.
    Only mock the email service (external dependency)."""
    mock_emailer = Mock()
    service = UserService(test_db, email_service=mock_emailer)

    user = service.create_user("test@example.com", "ValidPass123!")

    assert user.id is not None
    assert user.email == "test@example.com"
    assert test_db.get_user(user.id) is not None  # Actually saved
    mock_emailer.send_welcome.assert_called_once_with("test@example.com")

def test_create_user_duplicate_email(test_db):
    service = UserService(test_db, email_service=Mock())
    service.create_user("test@example.com", "ValidPass123!")

    with pytest.raises(DuplicateEmailError):
        service.create_user("test@example.com", "AnotherPass1!")
```

**Rule of thumb:** Mock at the **architectural boundary**, not at every function call. Mock: HTTP clients, email services, payment gateways, file systems. Don't mock: your own domain logic, value objects, pure functions.

---

### 3. Testing Implementation Instead of Behavior

**Signal:** Tests break when you refactor internal code even though external behavior is unchanged.

**Bad — testing HOW it works:**
```javascript
test('sorts using quicksort', () => {
  const spy = jest.spyOn(SortUtils, 'quickSort');
  sortProducts(products);
  expect(spy).toHaveBeenCalledWith(products, 'price');
  // Who cares if it uses quicksort or mergesort?
});
```

**Good — testing WHAT it does:**
```javascript
test('sorts products by price ascending', () => {
  const products = [
    { name: 'B', price: 20 },
    { name: 'A', price: 10 },
    { name: 'C', price: 30 },
  ];

  const sorted = sortProducts(products, 'price', 'asc');

  expect(sorted.map(p => p.price)).toEqual([10, 20, 30]);
});
```

**Guideline:** Test the **contract** (inputs → outputs), not the **mechanism**.

---

### 4. Slow Test Suites

**Signal:** Tests take more than 5 minutes for a small project. Developers skip running tests locally.

```
SPEED OPTIMIZATION STRATEGIES
══════════════════════════════════════════════════════════════

1. PARALLEL EXECUTION
   pytest -n auto (pytest-xdist)
   jest --maxWorkers=4

2. TEST PYRAMID
   Many unit tests (fast)     ██████████████████████
   Some integration tests     ████████████
   Few E2E tests (slow)       ████

3. IN-MEMORY DATABASES
   Use SQLite :memory: instead of PostgreSQL for unit tests

4. AVOID SLEEP/WAITS
   Replace time.sleep() with event-based synchronization

5. SELECTIVE RUNNING
   Run only affected tests: pytest --lf (last failed)
   Use test impact analysis tools

6. SHARED FIXTURES (carefully)
   session-scoped fixtures for expensive setup (DB schema)
   function-scoped for data isolation

7. LAZY LOADING
   Don't import heavy modules in every test file
   Use fixtures for expensive object creation
```

**Profile your test suite:**
```bash
pytest --durations=20   # Show 20 slowest tests
jest --verbose           # Show individual test times
```

---

### 5. Missing Edge Cases

**Signal:** Tests only cover the happy path. Production bugs are always in edge cases.

```
EDGE CASE CHECKLIST
══════════════════════════════════════════════════════════════

INPUTS:
  □ Empty string, empty list, empty dict
  □ None / null / undefined
  □ Single element collection
  □ Very large input (boundary of int, huge string)
  □ Negative numbers, zero
  □ Special characters: unicode, emoji, newlines, tabs
  □ SQL injection / XSS payloads
  □ Whitespace-only strings
  □ Duplicate values
  □ Maximum and minimum allowed values

BOUNDARIES:
  □ Off-by-one (fence-post errors)
  □ Exactly at the limit (e.g., max_length = 255)
  □ One over the limit
  □ One under the limit

STATE:
  □ First item / last item
  □ Already exists (duplicate)
  □ Concurrent modification
  □ Resource exhaustion (disk full, memory limit)

TIME:
  □ Midnight, end of month, leap year
  □ Timezone changes (DST)
  □ Very old dates, far future dates
  □ Epoch (January 1, 1970)
```

**Bad:**
```python
def test_calculate_discount():
    assert calculate_discount(100, 10) == 90  # Only happy path
```

**Good:**
```python
@pytest.mark.parametrize("price, discount, expected", [
    (100, 10, 90),        # Normal case
    (100, 0, 100),        # Zero discount
    (100, 100, 0),        # Full discount
    (0, 10, 0),           # Zero price
    (0.01, 50, 0.005),    # Tiny amounts
    (999999.99, 1, 989999.9901),  # Large numbers
])
def test_calculate_discount(price, discount, expected):
    assert calculate_discount(price, discount) == pytest.approx(expected)

def test_calculate_discount_negative_price():
    with pytest.raises(ValueError, match="Price must be non-negative"):
        calculate_discount(-10, 5)

def test_calculate_discount_over_100_percent():
    with pytest.raises(ValueError, match="Discount cannot exceed 100%"):
        calculate_discount(100, 150)
```

---

### 6. Snapshot Testing Abuse

**Signal:** Hundreds of snapshot files that nobody reviews. Snapshots updated blindly with `--update`.

```
WHEN SNAPSHOTS ARE APPROPRIATE
══════════════════════════════════════════════════════════════

GOOD USE CASES:
  ✓ Serialized output (JSON API responses)
  ✓ Error messages (exact wording matters)
  ✓ Generated code / SQL queries
  ✓ Visual regression (screenshot comparison)

BAD USE CASES:
  ✗ Entire React component trees (too fragile)
  ✗ Large objects with timestamps/IDs (always different)
  ✗ HTML output that changes with every CSS tweak
  ✗ Anything where you don't actually READ the snapshot on review

RULES:
  1. Snapshots should be SMALL and READABLE
  2. Review snapshot diffs as carefully as code diffs
  3. Never blindly run --update-snapshot
  4. Use inline snapshots when possible
  5. Exclude volatile fields (dates, UUIDs, random values)
```

**Bad — huge unreadable snapshot:**
```javascript
test('renders user profile', () => {
  const { container } = render(<UserProfile user={mockUser} />);
  expect(container).toMatchSnapshot(); // 200-line snapshot nobody reads
});
```

**Good — targeted assertions:**
```javascript
test('renders user profile', () => {
  render(<UserProfile user={mockUser} />);
  expect(screen.getByRole('heading')).toHaveTextContent('Jane Doe');
  expect(screen.getByText('jane@example.com')).toBeInTheDocument();
  expect(screen.getByRole('img', { name: 'Avatar' })).toHaveAttribute(
    'src', 'https://example.com/avatar.jpg'
  );
});
```

---

### 7. Test Coupling

**Signal:** Test B fails when Test A is skipped. Tests must run in a specific order.

**Bad — shared state between tests:**
```python
user = None

def test_create_user():
    global user
    user = create_user("test@example.com")
    assert user.id is not None

def test_update_user():
    user.name = "Updated"  # Depends on test_create_user running first!
    update_user(user)
    assert get_user(user.id).name == "Updated"
```

**Good — independent tests:**
```python
def test_create_user(db):
    user = create_user("test@example.com")
    assert user.id is not None

def test_update_user(db):
    user = create_user("test@example.com")  # Own setup
    user.name = "Updated"
    update_user(user)
    assert get_user(user.id).name == "Updated"
```

**Detection:** Run tests in random order.
```bash
pytest -p random   # pytest-randomly plugin
jest --randomize
```

---

### 8. Assertion Roulette

**Signal:** Test has many assertions with no message. When it fails, you don't know which assertion or why.

**Bad:**
```python
def test_user_registration():
    result = register("user@test.com", "Pass123!", "John")
    assert result.status == 200
    assert result.json()["id"]
    assert result.json()["email"] == "user@test.com"
    assert result.json()["name"] == "John"
    assert result.json()["role"] == "user"
    assert result.json()["active"] == True
    # Failure: "AssertionError" — WHICH ONE?
```

**Good — descriptive assertions or separate tests:**
```python
def test_user_registration():
    result = register("user@test.com", "Pass123!", "John")
    data = result.json()

    assert result.status == 200, f"Expected 200, got {result.status}: {data}"
    assert data["email"] == "user@test.com", f"Email mismatch: {data['email']}"
    assert data["name"] == "John", f"Name mismatch: {data['name']}"

# Or better — test one concept per test:
def test_registration_returns_user_data():
    data = register("user@test.com", "Pass123!", "John").json()
    assert data["email"] == "user@test.com"
    assert data["name"] == "John"

def test_registration_assigns_default_role():
    data = register("user@test.com", "Pass123!", "John").json()
    assert data["role"] == "user"
```

---

### 9. Eager Test Setup

**Signal:** `setUp` / `beforeEach` method is 50+ lines. Most tests don't need most of the setup.

**Bad:**
```python
class TestOrderProcessing(unittest.TestCase):
    def setUp(self):
        self.user = create_user(...)
        self.product1 = create_product(...)
        self.product2 = create_product(...)
        self.product3 = create_product(...)
        self.coupon = create_coupon(...)
        self.shipping = create_shipping_method(...)
        self.tax_rate = create_tax_rate(...)
        self.warehouse = create_warehouse(...)
        # Every test pays for ALL this setup even if it only needs a user

    def test_empty_cart_total(self):
        cart = Cart(user=self.user)
        assert cart.total == 0  # Didn't need products, coupons, shipping, tax...
```

**Good — setup only what's needed:**
```python
@pytest.fixture
def user(db):
    return create_user(email="test@example.com")

@pytest.fixture
def product(db):
    return create_product(name="Widget", price=9.99)

@pytest.fixture
def cart_with_items(user, product):
    cart = Cart(user=user)
    cart.add(product, quantity=2)
    return cart

def test_empty_cart_total(user):
    cart = Cart(user=user)
    assert cart.total == 0

def test_cart_total_with_items(cart_with_items):
    assert cart_with_items.total == 19.98
```

---

### 10. Mystery Guest

**Signal:** Test references external files, databases, or fixtures that aren't visible in the test code. Reader can't understand the test without looking elsewhere.

**Bad:**
```python
def test_import_products():
    result = import_from_csv("test_data/products.csv")  # What's in this file??
    assert len(result) == 5
    assert result[0].name == "Widget"
```

**Good — make data explicit:**
```python
def test_import_products(tmp_path):
    csv_file = tmp_path / "products.csv"
    csv_file.write_text(
        "name,price,category\n"
        "Widget,9.99,Electronics\n"
        "Gadget,19.99,Electronics\n"
    )

    result = import_from_csv(str(csv_file))

    assert len(result) == 2
    assert result[0].name == "Widget"
    assert result[0].price == 9.99
```

---

### 11. Test Parallelization Pitfalls

**Signal:** Tests pass sequentially but fail when run in parallel.

```
PARALLELIZATION FAILURE CAUSES
══════════════════════════════════════════════════════════════

1. SHARED DATABASE STATE
   Fix: Each test gets its own transaction (rolled back after)
        Or use unique table prefixes per worker

2. SHARED FILES
   Fix: Use temp directories per test, not fixed paths

3. PORT CONFLICTS
   Fix: Use dynamic port allocation (port 0)

4. GLOBAL VARIABLES / SINGLETONS
   Fix: Reset state in setUp/tearDown or use dependency injection

5. SHARED EXTERNAL SERVICES
   Fix: Mock external services, or use per-worker instances

6. ENVIRONMENT VARIABLES
   Fix: Use monkeypatch/mock.patch, don't set os.environ globally
```

**Good practice for parallel-safe tests:**
```python
@pytest.fixture
def isolated_db(tmp_path):
    """Each test gets its own SQLite database."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

@pytest.fixture
def unique_port():
    """Get a free port for this test."""
    import socket
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]
```

---

## Quick Reference: Anti-Pattern Detection

| Anti-Pattern | Detection Signal | Fix |
|---|---|---|
| Flaky Tests | Pass/fail randomly | Mock time, isolate state |
| Over-Mocking | Mocks outnumber real objects | Mock only at boundaries |
| Testing Implementation | Tests break on refactor | Test behavior, not mechanism |
| Slow Tests | Suite > 5 min | Parallelize, use in-memory DB |
| Missing Edge Cases | Bugs in production | Use parametrize + checklist |
| Snapshot Abuse | Blindly updating snapshots | Use targeted assertions |
| Test Coupling | Order-dependent failures | Independent setup per test |
| Assertion Roulette | "AssertionError" with no context | Messages or separate tests |
| Eager Setup | 50-line setUp unused by most tests | Composable fixtures |
| Mystery Guest | Can't understand test alone | Inline test data |
| Parallelization Pitfalls | Fails only in parallel | Isolate all shared resources |

---

## Best Practices

1. **Each test should be a complete story** — readable without looking elsewhere
2. **One concept per test** — if a test name has "and" in it, split it
3. **Test the contract, not the implementation** — inputs → outputs
4. **Mock at boundaries, not everywhere** — keep tests realistic
5. **Run tests in random order** regularly to detect coupling
6. **Profile your test suite** — fix the slowest 10% for biggest gains
7. **Review test code as rigorously as production code** — tests are code
8. **Use the testing pyramid** — mostly unit, some integration, few E2E
9. **Treat flaky tests as bugs** — quarantine and fix immediately
10. **Parameterize** to cover edge cases without writing new test functions

---

## Related Skills

- `tdd-bdd-patterns` — write tests that avoid these anti-patterns from the start
- `systematic-debugging` — debug failing tests effectively
- `webapp-testing-playwright` — avoid E2E testing anti-patterns
- `code-quality-audit` — audit test suite quality as part of codebase health
