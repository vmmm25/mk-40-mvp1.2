---
name: tdd-bdd-patterns
version: 1.0.0
description: >
  Test-Driven Development and Behavior-Driven Development methodologies. Covers the Red-Green-Refactor
  cycle, Given-When-Then scenarios, acceptance criteria translation, unit test first approach,
  integration test strategies, Cucumber/Gherkin syntax, pytest + pytest-bdd, Jest, xUnit,
  test pyramid, outside-in TDD, and property-based testing.
tags:
  - tdd
  - bdd
  - test-driven-development
  - behavior-driven-development
  - red-green-refactor
  - gherkin
  - cucumber
  - pytest
  - jest
  - xunit
  - test-pyramid
  - property-based-testing
author: garri333
license: MIT
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# tdd-bdd-patterns

Test-Driven Development and Behavior-Driven Development methodologies. Write tests first to design better software. Translate business requirements into executable specifications using Given-When-Then scenarios.

---

## When to Activate

Activate this skill when the user:

- Wants to practice **Test-Driven Development** (TDD)
- Asks about the **Red-Green-Refactor** cycle
- Needs to write **BDD scenarios** (Given-When-Then)
- Wants to translate **acceptance criteria** into tests
- Asks about **Cucumber**, **Gherkin**, or **pytest-bdd**
- Needs guidance on the **test pyramid** (unit/integration/E2E balance)
- Asks about **outside-in TDD** (London school) vs **inside-out** (Detroit school)
- Wants to use **property-based testing** (Hypothesis, fast-check)
- Needs to set up a **testing framework** (pytest, Jest, xUnit)
- Uses keywords: `TDD`, `BDD`, `red-green-refactor`, `given-when-then`, `test first`, `test pyramid`

---

## Step-by-Step Instructions

### 1. The Red-Green-Refactor Cycle

```
TDD: RED → GREEN → REFACTOR
══════════════════════════════════════════════════════════════

  ┌─────────────┐
  │     RED     │  Write a failing test for the next small
  │             │  piece of functionality. Run it — it MUST fail.
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │    GREEN    │  Write the MINIMUM code to make the test pass.
  │             │  Don't over-engineer. Just make it green.
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │  REFACTOR   │  Clean up the code. Remove duplication.
  │             │  Improve naming. Keep all tests green.
  └──────┬──────┘
         │
         └──────→ Back to RED for the next behavior

RULES:
1. Write production code ONLY to make a failing test pass
2. Write only ENOUGH of a test to fail (including compile errors)
3. Write only ENOUGH production code to pass the failing test
```

**TDD Example — Building a Stack:**

```python
# ── RED: First test ──────────────────────────────
def test_new_stack_is_empty():
    stack = Stack()
    assert stack.is_empty() is True
# RUN → NameError: name 'Stack' is not defined (RED ✗)

# ── GREEN: Minimal implementation ────────────────
class Stack:
    def is_empty(self):
        return True
# RUN → PASS (GREEN ✓)

# ── RED: Next behavior ──────────────────────────
def test_stack_is_not_empty_after_push():
    stack = Stack()
    stack.push(42)
    assert stack.is_empty() is False
# RUN → AttributeError: 'Stack' object has no attribute 'push' (RED ✗)

# ── GREEN: Make it pass ─────────────────────────
class Stack:
    def __init__(self):
        self._items = []

    def is_empty(self):
        return len(self._items) == 0

    def push(self, item):
        self._items.append(item)
# RUN → PASS (GREEN ✓)

# ── RED: Pop behavior ───────────────────────────
def test_pop_returns_last_pushed_item():
    stack = Stack()
    stack.push(42)
    assert stack.pop() == 42
# RUN → AttributeError (RED ✗)

# ── GREEN ────────────────────────────────────────
def pop(self):
    return self._items.pop()
# RUN → PASS (GREEN ✓)

# ── RED: Edge case ──────────────────────────────
def test_pop_on_empty_stack_raises():
    stack = Stack()
    with pytest.raises(IndexError, match="pop from empty stack"):
        stack.pop()
# RUN → IndexError is raised but message differs (RED ✗)

# ── GREEN ────────────────────────────────────────
def pop(self):
    if self.is_empty():
        raise IndexError("pop from empty stack")
    return self._items.pop()
# RUN → PASS (GREEN ✓)

# ── REFACTOR: Clean up, add __len__, __repr__ ───
```

---

### 2. BDD: Given-When-Then Scenarios

**Gherkin syntax** (used by Cucumber, Behave, pytest-bdd):

```gherkin
# features/shopping_cart.feature

Feature: Shopping Cart
  As a customer
  I want to manage items in my shopping cart
  So that I can purchase the products I need

  Background:
    Given the product catalog contains:
      | name    | price  | stock |
      | Widget  | 9.99   | 100   |
      | Gadget  | 19.99  | 50    |

  Scenario: Add item to cart
    Given I have an empty cart
    When I add 2 "Widget" to the cart
    Then the cart should contain 2 items
    And the cart total should be $19.98

  Scenario: Remove item from cart
    Given I have a cart with 1 "Widget"
    When I remove "Widget" from the cart
    Then the cart should be empty

  Scenario: Apply discount coupon
    Given I have a cart with 1 "Gadget"
    And a valid coupon "SAVE10" for 10% off
    When I apply the coupon "SAVE10"
    Then the cart total should be $17.99

  Scenario Outline: Quantity validation
    Given I have an empty cart
    When I try to add <quantity> "Widget" to the cart
    Then I should see error "<error_message>"

    Examples:
      | quantity | error_message                    |
      | 0        | Quantity must be at least 1      |
      | -1       | Quantity must be at least 1      |
      | 101      | Not enough stock (100 available) |
```

---

### 3. Translating Acceptance Criteria to Tests

```
ACCEPTANCE CRITERIA → TEST TRANSLATION
══════════════════════════════════════════════════════════════

User Story:
  "As a user, I want to reset my password so that I can
   regain access to my account."

Acceptance Criteria:
  1. User can request a reset link by entering their email
  2. A valid reset link is sent within 1 minute
  3. Reset link expires after 24 hours
  4. Password must meet strength requirements
  5. Old password is invalidated after reset

                          ↓

Tests:
  ✓ test_request_reset_with_valid_email_sends_link
  ✓ test_request_reset_with_unknown_email_returns_ok  (security)
  ✓ test_reset_link_contains_valid_token
  ✓ test_reset_link_expires_after_24_hours
  ✓ test_reset_with_expired_link_fails
  ✓ test_reset_requires_minimum_8_characters
  ✓ test_reset_requires_uppercase_and_number
  ✓ test_old_password_invalid_after_reset
  ✓ test_used_reset_link_cannot_be_reused
  ✓ test_multiple_reset_requests_invalidate_previous_links
```

---

### 4. pytest-bdd Implementation

```python
# tests/step_defs/test_shopping_cart.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from myapp.cart import Cart
from myapp.products import ProductCatalog

scenarios('../features/shopping_cart.feature')

@pytest.fixture
def catalog():
    return ProductCatalog()

@pytest.fixture
def cart():
    return Cart()

@given("the product catalog contains:", target_fixture="catalog")
def catalog_with_products(catalog, datatable):
    for row in datatable:
        catalog.add_product(row["name"], float(row["price"]), int(row["stock"]))
    return catalog

@given("I have an empty cart", target_fixture="cart")
def empty_cart():
    return Cart()

@given(parsers.parse('I have a cart with {count:d} "{product}"'), target_fixture="cart")
def cart_with_items(catalog, count, product):
    cart = Cart()
    item = catalog.get_product(product)
    cart.add(item, count)
    return cart

@when(parsers.parse('I add {count:d} "{product}" to the cart'))
def add_to_cart(cart, catalog, count, product):
    item = catalog.get_product(product)
    cart.add(item, count)

@when(parsers.parse('I remove "{product}" from the cart'))
def remove_from_cart(cart, product):
    cart.remove(product)

@then(parsers.parse("the cart should contain {count:d} items"))
def cart_has_items(cart, count):
    assert cart.item_count == count

@then("the cart should be empty")
def cart_is_empty(cart):
    assert cart.is_empty()

@then(parsers.parse("the cart total should be ${total:f}"))
def cart_total(cart, total):
    assert cart.total == pytest.approx(total, abs=0.01)
```

---

### 5. Jest Implementation (JavaScript/TypeScript)

```typescript
// __tests__/cart.test.ts
import { Cart } from '../src/cart';
import { Product } from '../src/product';

describe('Shopping Cart', () => {
  let cart: Cart;
  const widget: Product = { name: 'Widget', price: 9.99, stock: 100 };
  const gadget: Product = { name: 'Gadget', price: 19.99, stock: 50 };

  beforeEach(() => {
    cart = new Cart();
  });

  describe('adding items', () => {
    it('should add an item to the cart', () => {
      cart.add(widget, 2);
      expect(cart.itemCount).toBe(2);
      expect(cart.total).toBeCloseTo(19.98);
    });

    it('should reject zero quantity', () => {
      expect(() => cart.add(widget, 0)).toThrow('Quantity must be at least 1');
    });

    it('should reject quantity exceeding stock', () => {
      expect(() => cart.add(widget, 101)).toThrow('Not enough stock');
    });
  });

  describe('removing items', () => {
    it('should remove an item from the cart', () => {
      cart.add(widget, 1);
      cart.remove('Widget');
      expect(cart.isEmpty()).toBe(true);
    });
  });

  describe('applying coupons', () => {
    it('should apply percentage discount', () => {
      cart.add(gadget, 1);
      cart.applyCoupon({ code: 'SAVE10', discountPercent: 10 });
      expect(cart.total).toBeCloseTo(17.99);
    });
  });
});
```

---

### 6. The Test Pyramid

```
THE TEST PYRAMID
══════════════════════════════════════════════════════════════

                    ╱  ╲
                   ╱ E2E ╲              Few, slow, expensive
                  ╱  Tests ╲            Test full user journeys
                 ╱──────────╲           Playwright, Cypress, Selenium
                ╱ Integration ╲         
               ╱    Tests      ╲        Some, medium speed
              ╱  API, DB, auth  ╲       Test component interactions
             ╱──────────────────╲       
            ╱    Unit Tests      ╲      Many, fast, cheap
           ╱  Pure logic, utils   ╲     Test individual functions
          ╱________________________╲    pytest, Jest, xUnit

RECOMMENDED RATIOS:
  Unit:         70% of tests (fast, isolated, hundreds-thousands)
  Integration:  20% of tests (real DB, real HTTP, tens-hundreds)
  E2E:          10% of tests (browser-based, few dozen max)

EXECUTION TIME BUDGET:
  Unit tests:        < 30 seconds
  Integration tests: < 5 minutes
  E2E tests:         < 15 minutes
  Total CI:          < 20 minutes
```

---

### 7. Outside-In TDD (London School) vs Inside-Out (Detroit School)

```
TWO SCHOOLS OF TDD
══════════════════════════════════════════════════════════════

INSIDE-OUT (Detroit / Classic):
  Start from domain entities → build outward
  ✓ Minimal mocking, tests use real collaborators
  ✓ Good for data-driven designs
  ✗ Can lead to YAGNI violations (building unused internals)

  Workflow: Entity tests → Service tests → Controller tests

OUTSIDE-IN (London / Mockist):
  Start from acceptance test → drill down
  ✓ Driven by user needs
  ✓ Discovers interfaces naturally
  ✗ Can lead to over-mocking

  Workflow: Acceptance test → Controller → Service → Entity
            (mock deeper layers until you implement them)
```

**Outside-In Example:**

```python
# Step 1: Write acceptance test (fails — nothing exists)
def test_user_can_register(client):
    response = client.post("/api/register", json={
        "email": "user@example.com",
        "password": "SecurePass123!",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"

# Step 2: Write controller test (mock service)
def test_register_endpoint(mock_user_service):
    mock_user_service.register.return_value = User(id=1, email="user@example.com")
    response = client.post("/api/register", json={...})
    mock_user_service.register.assert_called_once()

# Step 3: Write service test (mock repository)
def test_register_service(mock_repo):
    service = UserService(repo=mock_repo)
    user = service.register("user@example.com", "SecurePass123!")
    assert user.email == "user@example.com"
    mock_repo.save.assert_called_once()

# Step 4: Implement everything to make acceptance test green
```

---

### 8. Property-Based Testing

Instead of testing specific examples, test **properties** that should hold for **any** input.

```python
# Python — Hypothesis
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_preserves_length(xs):
    """Sorting never changes the number of elements."""
    assert len(sorted(xs)) == len(xs)

@given(st.lists(st.integers(), min_size=1))
def test_sort_produces_ordered_output(xs):
    """Every element is ≤ the next element."""
    result = sorted(xs)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]

@given(st.lists(st.integers()))
def test_sort_is_idempotent(xs):
    """Sorting twice gives the same result as sorting once."""
    assert sorted(sorted(xs)) == sorted(xs)

@given(st.text(), st.text())
def test_string_concat_length(a, b):
    """Concatenation length = sum of individual lengths."""
    assert len(a + b) == len(a) + len(b)
```

```typescript
// JavaScript — fast-check
import fc from 'fast-check';

test('sort preserves length', () => {
  fc.assert(
    fc.property(fc.array(fc.integer()), (arr) => {
      expect([...arr].sort((a, b) => a - b)).toHaveLength(arr.length);
    })
  );
});

test('encode-decode roundtrip', () => {
  fc.assert(
    fc.property(fc.string(), (s) => {
      expect(decode(encode(s))).toBe(s);
    })
  );
});
```

**When to use property-based testing:**
- Serialization/deserialization roundtrips
- Mathematical properties (commutativity, associativity)
- Data structure invariants
- Parser validation
- Any function where you can state a general rule

---

### 9. xUnit Patterns

```
XUNIT TEST STRUCTURE (Four-Phase Test)
══════════════════════════════════════════════════════════════
def test_something():
    # 1. SETUP (Arrange)    — Create objects, prepare data
    user = User(name="Alice", balance=100)

    # 2. EXERCISE (Act)     — Call the method under test
    user.withdraw(30)

    # 3. VERIFY (Assert)    — Check the expected outcome
    assert user.balance == 70

    # 4. TEARDOWN (Cleanup) — Restore state (often in fixture)
    # (handled by fixture/context manager)
```

**Common xUnit patterns:**

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Test Fixture** | Shared setup for multiple tests | Common preconditions |
| **Parameterized Test** | Same test with different data | Many input/output pairs |
| **Expected Exception** | Assert an error is raised | Testing error handling |
| **Test Helper** | Shared assertion/setup function | Reusable test logic |
| **Object Mother** | Factory for test objects | Complex object creation |
| **Builder Pattern** | Fluent API for test data | Readable test setup |

**Builder pattern for tests:**

```python
class UserBuilder:
    def __init__(self):
        self._name = "Default User"
        self._email = "default@example.com"
        self._role = "user"

    def with_name(self, name): self._name = name; return self
    def with_email(self, email): self._email = email; return self
    def as_admin(self): self._role = "admin"; return self
    def build(self): return User(self._name, self._email, self._role)

# Usage in tests
def test_admin_can_delete_users():
    admin = UserBuilder().with_name("Admin").as_admin().build()
    target = UserBuilder().with_name("Target").build()
    admin.delete_user(target)
    assert target.is_deleted
```

---

### 10. Integration Test Strategies

```
INTEGRATION TEST BOUNDARIES
══════════════════════════════════════════════════════════════

What to test in integration tests:
  ✓ Database queries (real DB, use transactions for isolation)
  ✓ HTTP API endpoints (real server, test client)
  ✓ Authentication/authorization flows
  ✓ External service contracts (consumer-driven)
  ✓ Message queue publish/consume
  ✓ File system operations (temp directories)

What NOT to test in integration tests:
  ✗ Business logic (that's for unit tests)
  ✗ UI rendering (that's for E2E tests)
  ✗ Third-party API behavior (use contract tests)
```

```python
# pytest integration test with real database
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    """Each test runs in a transaction that gets rolled back."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_create_and_retrieve_user(db_session):
    repo = UserRepository(db_session)
    repo.create(User(email="test@example.com", name="Test"))
    db_session.flush()

    found = repo.find_by_email("test@example.com")
    assert found is not None
    assert found.name == "Test"
```

---

## Best Practices

1. **Start with the test** — write the assertion first, then work backward
2. **One assertion per concept** — a test should verify one behavior
3. **Name tests as sentences** — `test_user_can_register_with_valid_email`
4. **Red first** — always see the test fail before making it pass
5. **Refactor mercilessly** — the refactor step is not optional
6. **Follow the pyramid** — most tests should be fast unit tests
7. **Use property-based testing** for algorithms and data transformations
8. **BDD for collaboration** — use Gherkin when non-developers need to read tests
9. **Don't test the framework** — test YOUR code, not library/framework behavior
10. **Keep tests fast** — if TDD feels slow, your tests are too slow

---

## Examples

### Complete TDD Session — Password Validator

```python
# TDD Session: Build a password validator step by step

# RED 1: Empty password
def test_empty_password_is_invalid():
    assert validate_password("") == False

# GREEN 1:
def validate_password(password: str) -> bool:
    return len(password) > 0

# RED 2: Too short
def test_password_shorter_than_8_chars_is_invalid():
    assert validate_password("Ab1!xyz") == False  # 7 chars

# GREEN 2:
def validate_password(password: str) -> bool:
    return len(password) >= 8

# RED 3: Needs uppercase
def test_password_without_uppercase_is_invalid():
    assert validate_password("abcdefg1!") == False

# GREEN 3:
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    return True

# RED 4: Needs digit
def test_password_without_digit_is_invalid():
    assert validate_password("Abcdefgh!") == False

# GREEN 4:
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

# RED 5: Valid password passes
def test_valid_password():
    assert validate_password("SecureP4ss!") == True

# GREEN 5: Already passes! ✓

# REFACTOR: Clean up
import re

def validate_password(password: str) -> bool:
    """Validate password meets strength requirements."""
    checks = [
        (len(password) >= 8, "Must be at least 8 characters"),
        (re.search(r'[A-Z]', password), "Must contain an uppercase letter"),
        (re.search(r'\d', password), "Must contain a digit"),
    ]
    return all(check for check, _ in checks)
```

---

## Related Skills

- `testing-anti-patterns` — avoid common mistakes in your TDD practice
- `systematic-debugging` — debug tests that don't work as expected
- `webapp-testing-playwright` — E2E testing as top of the pyramid
- `code-quality-audit` — measure test coverage and quality
