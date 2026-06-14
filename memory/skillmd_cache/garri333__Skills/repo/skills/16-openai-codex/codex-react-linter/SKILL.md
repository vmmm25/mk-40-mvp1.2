---
name: codex-react-linter
version: 1.0.0
description: React Code Fix & Linter skill with three-step protocol (Prettier formatting, linc linting, manual fix reporting). MCP-enhanced with full repository state awareness, dependency analysis, and previous CI run context. Integrates ESLint, Prettier, and React-specific rules for hooks, functional components, and state management. 242,682 stars on MCP Market.
tags: [openai, codex, react, linter, eslint, prettier, hooks, mcp, code-quality, formatting, ci]
author: garri333
license: MIT
source: openai/skills
---

# Codex React Linter Skill

## Overview

Use this skill whenever the user needs to lint, format, or fix React code following a strict three-step protocol. This skill combines Prettier formatting, ESLint linting via `yarn linc`, and intelligent manual fix reporting — all enhanced by MCP (Model Context Protocol) for full repository state awareness.

**MCP Market stats:** 242,682 stars — one of the most popular code quality skills in the ecosystem.

---

## When to Activate

- User asks to lint or format React code.
- User mentions ESLint, Prettier, or linting errors in a React project.
- User has React hook rule violations (rules of hooks).
- User needs to fix CI lint failures in a React project.
- User asks about React code quality or best practices enforcement.
- User mentions `yarn linc` or the three-step lint protocol.
- User wants to migrate React code to modern patterns (class → functional, etc.).
- User asks about MCP-enhanced linting with repository context.

---

## Three-Step Protocol

The React Linter follows a strict three-step protocol for every code fix operation:

```
┌─────────────────────────────────────────────────────────┐
│              THREE-STEP LINT PROTOCOL                    │
│                                                          │
│  Step 1: yarn prettier    → Auto-format code             │
│              ↓                                           │
│  Step 2: yarn linc        → Lint and auto-fix            │
│              ↓                                           │
│  Step 3: Report           → List remaining manual fixes  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Never skip steps. Never reorder steps. Always run all three.**

---

## Step-by-Step Procedures

### Step 1: Prettier Formatting

```bash
# Run Prettier on changed files
yarn prettier --write src/

# Run Prettier on specific files
yarn prettier --write src/components/Dashboard.tsx src/hooks/useAuth.ts

# Check formatting without writing (CI mode)
yarn prettier --check src/

# Run Prettier with React-specific parser
yarn prettier --write --parser typescript "src/**/*.{ts,tsx}"

# Prettier configuration for React projects (.prettierrc)
```

```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "jsxSingleQuote": false,
  "arrowParens": "always",
  "endOfLine": "lf",
  "jsxBracketSameLine": false
}
```

**What Prettier fixes:**
- Consistent indentation and spacing
- Trailing commas
- Quote style (single vs double)
- Line length wrapping
- JSX formatting and bracket placement
- Semicolon consistency

### Step 2: ESLint Linting with `yarn linc`

```bash
# Run linc (Lint Changed files)
yarn linc

# linc only lints files that have changed compared to the base branch,
# making it fast and focused on your actual modifications

# Run ESLint on all files (full project lint)
yarn lint

# Run ESLint with auto-fix
yarn lint --fix

# Run ESLint on specific files
yarn lint src/components/Dashboard.tsx

# Run with verbose output for debugging
yarn lint --debug
```

**ESLint configuration for React (.eslintrc.json):**

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:jsx-a11y/recommended",
    "prettier"
  ],
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint",
    "jsx-a11y",
    "import"
  ],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "react/jsx-no-target-blank": "error",
    "react/no-array-index-key": "warn",
    "react/no-unstable-nested-components": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "import/order": ["error", {
      "groups": ["builtin", "external", "internal", "parent", "sibling", "index"],
      "newlines-between": "always",
      "alphabetize": { "order": "asc" }
    }],
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  },
  "settings": {
    "react": { "version": "detect" }
  }
}
```

### Step 3: Report Manual Fixes Needed

After Steps 1 and 2, report any remaining issues that require manual intervention:

```bash
# After running prettier and linc, check for remaining issues
yarn lint --no-fix 2>&1 | grep "error" | sort | uniq -c | sort -rn

# Generate a structured report
codex react-lint report

# Output:
# ┌────────────────────────────────────────────────────────────────┐
# │ REACT LINTER REPORT                                           │
# ├────────────────────────────────────────────────────────────────┤
# │ Step 1 (Prettier):  ✓ 12 files formatted                     │
# │ Step 2 (yarn linc): ✓ 8 auto-fixed, 3 remaining              │
# │ Step 3 (Manual):    ⚠ 3 issues require manual fixes           │
# ├────────────────────────────────────────────────────────────────┤
# │                                                                │
# │ Manual Fixes Required:                                        │
# │                                                                │
# │ 1. src/hooks/useData.ts:15                                    │
# │    react-hooks/exhaustive-deps: Missing dependency 'userId'   │
# │    in useEffect. Add it to the dependency array or remove      │
# │    the hook if not needed.                                     │
# │                                                                │
# │ 2. src/components/Table.tsx:42                                 │
# │    react/no-unstable-nested-components: Unstable nested        │
# │    component. Extract 'RowRenderer' to a separate component.  │
# │                                                                │
# │ 3. src/pages/Dashboard.tsx:78                                  │
# │    @typescript-eslint/no-explicit-any: Unexpected 'any'.       │
# │    Replace with proper type for API response.                  │
# └────────────────────────────────────────────────────────────────┘
```

---

## React-Specific Rules

### Rules of Hooks

```typescript
// ✗ BAD: Hook inside condition
function UserProfile({ userId }: { userId: string | null }) {
  if (userId) {
    const [user, setUser] = useState(null); // ✗ Hook in conditional
    useEffect(() => { fetchUser(userId); }, [userId]); // ✗ Hook in conditional
  }
  return <div>Profile</div>;
}

// ✓ GOOD: Hooks at top level, conditional logic inside
function UserProfile({ userId }: { userId: string | null }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (userId) {
      fetchUser(userId).then(setUser);
    }
  }, [userId]);

  if (!userId) return <div>No user selected</div>;
  return <div>{user?.name}</div>;
}
```

```typescript
// ✗ BAD: Hook inside loop
function UserList({ userIds }: { userIds: string[] }) {
  return (
    <>
      {userIds.map((id) => {
        const [data] = useFetch(`/api/users/${id}`); // ✗ Hook in loop
        return <UserCard key={id} data={data} />;
      })}
    </>
  );
}

// ✓ GOOD: Extract to a separate component
function UserCard({ userId }: { userId: string }) {
  const [data] = useFetch(`/api/users/${userId}`); // ✓ Top level
  return <div>{data?.name}</div>;
}

function UserList({ userIds }: { userIds: string[] }) {
  return (
    <>
      {userIds.map((id) => (
        <UserCard key={id} userId={id} />
      ))}
    </>
  );
}
```

### Functional Component Patterns

```typescript
// ✗ BAD: Class component (legacy)
class Welcome extends React.Component<{ name: string }> {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}

// ✓ GOOD: Functional component with TypeScript
interface WelcomeProps {
  name: string;
}

function Welcome({ name }: WelcomeProps) {
  return <h1>Hello, {name}</h1>;
}

// ✓ ALSO GOOD: Arrow function with FC type
const Welcome: React.FC<WelcomeProps> = ({ name }) => {
  return <h1>Hello, {name}</h1>;
};
```

### State Management Best Practices

```typescript
// ✗ BAD: Derived state stored separately
function ProductList({ products }: { products: Product[] }) {
  const [filteredProducts, setFilteredProducts] = useState(products);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setFilteredProducts(  // ✗ Unnecessary state + effect
      products.filter((p) => p.name.includes(searchTerm)),
    );
  }, [products, searchTerm]);

  return <List items={filteredProducts} />;
}

// ✓ GOOD: Derive during render
function ProductList({ products }: { products: Product[] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const filteredProducts = useMemo(  // ✓ Derived value
    () => products.filter((p) => p.name.includes(searchTerm)),
    [products, searchTerm],
  );

  return <List items={filteredProducts} />;
}
```

```typescript
// ✗ BAD: Multiple related state variables
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [email, setEmail] = useState('');
const [errors, setErrors] = useState({});

// ✓ GOOD: useReducer for complex related state
interface FormState {
  firstName: string;
  lastName: string;
  email: string;
  errors: Record<string, string>;
}

type FormAction =
  | { type: 'SET_FIELD'; field: keyof FormState; value: string }
  | { type: 'SET_ERRORS'; errors: Record<string, string> }
  | { type: 'RESET' };

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'SET_ERRORS':
      return { ...state, errors: action.errors };
    case 'RESET':
      return initialState;
  }
}

const [state, dispatch] = useReducer(formReducer, initialState);
```

### useEffect Dependency Management

```typescript
// ✗ BAD: Missing dependencies
useEffect(() => {
  fetchData(userId, orgId); // ✗ orgId missing from deps
}, [userId]);

// ✓ GOOD: All dependencies listed
useEffect(() => {
  fetchData(userId, orgId);
}, [userId, orgId]);

// ✓ GOOD: Stable callback with useCallback
const fetchUserData = useCallback(() => {
  return fetchData(userId, orgId);
}, [userId, orgId]);

useEffect(() => {
  fetchUserData();
}, [fetchUserData]);

// ✓ GOOD: Cleanup for subscriptions
useEffect(() => {
  const subscription = dataSource.subscribe(userId);
  return () => {
    subscription.unsubscribe(); // ✓ Cleanup
  };
}, [userId]);
```

---

## MCP-Enhanced Linting

The React Linter uses MCP (Model Context Protocol) to enhance linting with full repository context:

### Repository State Awareness

```bash
# MCP provides the linter with:
# 1. Full project dependency tree (package.json analysis)
# 2. TypeScript configuration (tsconfig.json)
# 3. Previous CI run results and failure patterns
# 4. Import graph across the entire project
# 5. Component hierarchy and prop flow
# 6. Custom ESLint rules and overrides
# 7. Git history for identifying recurring lint patterns

# Enable MCP-enhanced mode
codex react-lint --mcp

# MCP context includes:
# - Which components import the file being linted
# - Whether a missing dependency in useEffect caused a previous CI failure
# - If a deprecated pattern was already flagged in a previous PR review
# - Team-specific overrides from .eslintrc
```

### Dependency-Aware Fixes

```bash
# MCP analyzes your package.json to provide version-aware fixes
codex react-lint --mcp --analyze-deps

# Example output:
# ⚠ Using react-router v5 patterns but react-router v6.21 is installed
#   → Recommend: Replace <Switch> with <Routes>, <Route component> with <Route element>
#
# ⚠ Using @tanstack/react-query v4 API but v5.18 is installed
#   → Recommend: Replace useQuery({ queryKey, queryFn }) positional args with object syntax
#
# ✓ React 19.1 detected — react-in-jsx-scope rule correctly disabled
```

### Previous CI Run Context

```bash
# MCP considers previous CI failures to prioritize fixes
codex react-lint --mcp --ci-context

# Output:
# Previous CI failures (last 5 runs):
#   ✗ Run #142: react-hooks/exhaustive-deps in src/hooks/useData.ts (3 times)
#   ✗ Run #140: import/order in src/pages/Dashboard.tsx (2 times)
#   ✗ Run #138: @typescript-eslint/no-explicit-any in src/api/client.ts
#
# Prioritized fixes (recurring issues first):
#   1. [HIGH] src/hooks/useData.ts:15 — exhaustive-deps (failed 3x)
#   2. [MED]  src/pages/Dashboard.tsx:3 — import/order (failed 2x)
#   3. [LOW]  src/api/client.ts:42 — no-explicit-any (failed 1x)
```

---

## ESLint and Prettier Integration

### Package Setup

```bash
# Install all required dependencies
yarn add -D eslint prettier \
  eslint-config-prettier \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y \
  eslint-plugin-import \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser

# Add scripts to package.json
```

```json
{
  "scripts": {
    "lint": "eslint 'src/**/*.{ts,tsx}' --max-warnings 0",
    "lint:fix": "eslint 'src/**/*.{ts,tsx}' --fix",
    "linc": "eslint --no-error-on-unmatched-pattern $(git diff --name-only --diff-filter=ACMRTUXB HEAD | grep -E '\\.(ts|tsx)$' | xargs)",
    "prettier": "prettier --write 'src/**/*.{ts,tsx,css,json,md}'",
    "prettier:check": "prettier --check 'src/**/*.{ts,tsx,css,json,md}'",
    "lint:all": "yarn prettier && yarn linc"
  }
}
```

### Pre-commit Hook Integration

```bash
# Install husky and lint-staged
yarn add -D husky lint-staged

# Initialize husky
npx husky init

# Add pre-commit hook
echo "npx lint-staged" > .husky/pre-commit
```

```json
// package.json — lint-staged configuration
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "prettier --write",
      "eslint --fix --max-warnings 0"
    ],
    "*.{css,json,md}": [
      "prettier --write"
    ]
  }
}
```

---

## Best Practices

1. **Always follow the three-step protocol** — Prettier first, then linc, then report. Never skip or reorder.
2. **Run Prettier before ESLint** — Prettier handles formatting; ESLint handles logic. Running ESLint first creates formatting conflicts.
3. **Use `yarn linc` over `yarn lint`** — linc only checks changed files, making it faster and more focused.
4. **Fix hooks exhaustive-deps warnings carefully** — blindly adding dependencies can cause infinite re-renders; understand the impact.
5. **Extract nested components** — unstable nested components cause unnecessary re-renders; extract them as standalone components.
6. **Prefer derived values over state + effects** — use `useMemo` for computed values instead of syncing state with `useEffect`.
7. **Enable MCP mode for complex projects** — repository context helps the linter provide more accurate, project-specific fixes.
8. **Set up pre-commit hooks** — catch lint issues locally before they fail CI.
9. **Use `--max-warnings 0`** — treat warnings as errors in CI to maintain code quality standards.
10. **Review auto-fixes before committing** — ESLint auto-fix is good but not perfect; always review the changes.

---

## Examples

### Example 1: Full Three-Step Protocol Run

```bash
# Step 1: Format with Prettier
$ yarn prettier --write src/components/Dashboard.tsx
# ✓ src/components/Dashboard.tsx (formatted)

# Step 2: Lint with linc
$ yarn linc
# ✓ src/components/Dashboard.tsx
#   ⚠ 2 warnings auto-fixed (import/order, no-unused-vars)
#   ✗ 1 error remaining (react-hooks/exhaustive-deps)

# Step 3: Report manual fixes
# ┌──────────────────────────────────────────────────────────────┐
# │ MANUAL FIX REQUIRED:                                        │
# │                                                              │
# │ src/components/Dashboard.tsx:23:8                            │
# │ react-hooks/exhaustive-deps                                  │
# │ React Hook useEffect has a missing dependency: 'fetchData'.  │
# │ Either include it or remove the dependency array.            │
# │                                                              │
# │ Fix: Wrap fetchData in useCallback or move it inside the     │
# │ useEffect if it doesn't need to be shared.                   │
# └──────────────────────────────────────────────────────────────┘
```

### Example 2: MCP-Enhanced CI Fix

```bash
# CI failed on lint — use MCP context to fix intelligently
codex react-lint --mcp --ci-context --fix

# Codex analyzes:
# 1. The CI error log
# 2. The file's import graph
# 3. Related component props and state
# 4. Previous fix attempts in git history

# Result: Smart fix that accounts for the full component tree
```

### Example 3: Migrate Class Components

```bash
# Detect and migrate all class components to functional
codex react-lint --migrate-classes --dry-run

# Found 8 class components:
#   src/components/Header.tsx (simple — auto-migrate)
#   src/components/Form.tsx (lifecycle methods — manual review)
#   src/components/Modal.tsx (simple — auto-migrate)
#   ...
#
# Auto-migratable: 5/8
# Need manual review: 3/8
#
# Proceed with auto-migration? [Y/n]
```

### Example 4: Project-Wide Quality Report

```bash
codex react-lint --report full

# ┌─────────────────────────────────────────────────┐
# │ REACT CODE QUALITY REPORT                       │
# ├─────────────────────────────────────────────────┤
# │ Files analyzed:           142                   │
# │ Formatting issues (Step 1): 23 (auto-fixed)     │
# │ Lint issues (Step 2):       45 (31 auto-fixed)  │
# │ Manual fixes needed (Step 3): 14                │
# ├─────────────────────────────────────────────────┤
# │ Top issues:                                     │
# │   exhaustive-deps:          6                   │
# │   no-explicit-any:          4                   │
# │   import/order:             3                   │
# │   no-unstable-nested:       1                   │
# ├─────────────────────────────────────────────────┤
# │ Class components remaining: 3                   │
# │ Hook violations:            2                   │
# │ Accessibility warnings:     7                   │
# │ Overall grade:              B+ (87/100)         │
# └─────────────────────────────────────────────────┘
```
