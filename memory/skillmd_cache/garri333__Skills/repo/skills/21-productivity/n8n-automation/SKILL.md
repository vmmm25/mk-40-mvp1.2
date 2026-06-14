---
name: n8n-automation
version: 1.0.0
description: >
  n8n workflow automation integration. Create, modify, and execute n8n workflows
  programmatically. Supports all core node types (HTTP Request, Code, If, Switch, Merge,
  Set, Function, Webhook), workflow templates for common patterns, API v1 CRUD operations,
  credential management, error handling with retry nodes, community node integration,
  and Docker deployment. Covers self-hosted and cloud deployment strategies.
tags:
  - n8n
  - workflow-automation
  - api-orchestration
  - webhook
  - integration
  - docker
  - scheduling
  - event-driven
  - low-code
  - productivity
author: garri333
license: MIT
source: Inspired by n8n PR Creator (170,914+ stars) and n8n community workflows
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# n8n-automation

n8n workflow automation integration. Create, modify, and execute n8n workflows programmatically. Build data sync pipelines, notification systems, API orchestrations, and event-driven automations using n8n's node-based workflow engine.

---

## When to Activate

Activate this skill when the user:

- Wants to **create an n8n workflow** or automate a multi-step process
- Needs to **connect APIs** or services together in a pipeline
- Asks about **webhook-triggered automations** or event-driven workflows
- Wants to **schedule recurring tasks** (cron jobs, data syncs)
- Needs to **modify an existing n8n workflow** via the API
- Asks about **n8n node types**, configuration, or best practices
- Wants to **deploy n8n** with Docker or compare self-hosted vs. cloud
- Needs **error handling** with retries in an automation pipeline
- Asks about **credential management** in n8n
- Wants to integrate **community nodes** or custom functions
- Uses keywords: `n8n`, `workflow automation`, `webhook`, `api orchestration`, `automate`, `pipeline`, `scheduled task`

---

## Step-by-Step Instructions

### 1. n8n Architecture Overview

```
n8n WORKFLOW AUTOMATION ARCHITECTURE
══════════════════════════════════════════════════════════════

  ┌────────────────────────────────────────────────────────┐
  │                    n8n ENGINE                          │
  │                                                        │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
  │  │ TRIGGER  │───▶│  NODES   │───▶│  OUTPUT  │         │
  │  │          │    │          │    │          │         │
  │  │ • Webhook│    │ • HTTP   │    │ • Email  │         │
  │  │ • Cron   │    │ • Code   │    │ • Slack  │         │
  │  │ • Event  │    │ • If/Sw  │    │ • DB     │         │
  │  │ • Manual │    │ • Merge  │    │ • File   │         │
  │  │ • Poll   │    │ • Set    │    │ • API    │         │
  │  └──────────┘    │ • Fn     │    └──────────┘         │
  │                  └──────────┘                          │
  │                                                        │
  │  ┌──────────────────────────────────────────────┐     │
  │  │           CREDENTIAL STORE                    │     │
  │  │  API Keys │ OAuth2 │ DB Connections │ Tokens │     │
  │  └──────────────────────────────────────────────┘     │
  │                                                        │
  │  ┌──────────────────────────────────────────────┐     │
  │  │           EXECUTION ENGINE                    │     │
  │  │  Queue │ Retry │ Error Handling │ Logging    │     │
  │  └──────────────────────────────────────────────┘     │
  └────────────────────────────────────────────────────────┘

  API v1: http://localhost:5678/api/v1/
  UI:     http://localhost:5678/
```

---

### 2. Core Node Types Reference

```yaml
# n8n Core Node Types
node_types:
  triggers:
    - name: Webhook
      description: "HTTP endpoint that starts a workflow on incoming request"
      config:
        httpMethod: "POST"
        path: "my-webhook"
        responseMode: "onReceived"  # or "lastNode"
        authentication: "headerAuth"  # optional

    - name: Cron
      description: "Schedule-based trigger (cron expression)"
      config:
        cronExpression: "0 9 * * 1-5"  # Weekdays at 9am
        timezone: "Europe/Madrid"

    - name: Polling
      description: "Check external source at intervals"
      config:
        pollInterval: 300  # seconds

  processing:
    - name: HTTP Request
      description: "Make HTTP calls to any API"
      config:
        method: "GET|POST|PUT|PATCH|DELETE"
        url: "https://api.example.com/data"
        authentication: "predefinedCredentialType"
        headers: {}
        body: {}
        options:
          timeout: 30000
          retry:
            maxRetries: 3
            waitBetween: 1000

    - name: Code
      description: "Execute custom JavaScript or Python"
      config:
        language: "javaScript"  # or "python"
        code: |
          // Access input data
          const items = $input.all();
          // Process and return
          return items.map(item => ({
            json: { ...item.json, processed: true }
          }));

    - name: If
      description: "Conditional branching"
      config:
        conditions:
          - leftValue: "={{ $json.status }}"
            operation: "equals"
            rightValue: "active"

    - name: Switch
      description: "Multi-way branching based on value"
      config:
        dataType: "string"
        value: "={{ $json.category }}"
        rules:
          - value: "urgent"
            output: 0
          - value: "normal"
            output: 1
          - value: "low"
            output: 2

    - name: Merge
      description: "Combine data from multiple branches"
      config:
        mode: "append"  # append | mergeByIndex | mergeByKey | multiplex
        mergeByKey:
          key: "id"

    - name: Set
      description: "Set or modify data fields"
      config:
        assignments:
          - name: "fullName"
            value: "={{ $json.firstName }} {{ $json.lastName }}"
            type: "string"

    - name: Function
      description: "Advanced data transformation with full JS"
      config:
        functionCode: |
          const results = [];
          for (const item of items) {
            results.push({
              json: {
                id: item.json.id,
                transformed: item.json.value * 2
              }
            });
          }
          return results;
```

---

### 3. Workflow Templates

#### Template A: Data Sync Pipeline

```json
{
  "name": "Data Sync: CRM → Database",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "position": [250, 300],
      "parameters": {
        "cronExpression": "0 */6 * * *"
      }
    },
    {
      "name": "Fetch CRM Data",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "method": "GET",
        "url": "https://api.crm.com/v2/contacts?updated_after={{$now.minus(6,'hours').toISO()}}",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "httpHeaderAuth"
      }
    },
    {
      "name": "Transform Data",
      "type": "n8n-nodes-base.code",
      "position": [650, 300],
      "parameters": {
        "language": "javaScript",
        "code": "return $input.all().map(item => ({\n  json: {\n    external_id: item.json.id,\n    name: item.json.full_name,\n    email: item.json.email,\n    synced_at: new Date().toISOString()\n  }\n}));"
      }
    },
    {
      "name": "Upsert to Database",
      "type": "n8n-nodes-base.postgres",
      "position": [850, 300],
      "parameters": {
        "operation": "upsert",
        "table": "contacts",
        "columns": "external_id,name,email,synced_at",
        "conflictColumn": "external_id"
      }
    },
    {
      "name": "Notify on Complete",
      "type": "n8n-nodes-base.slack",
      "position": [1050, 300],
      "parameters": {
        "channel": "#data-ops",
        "text": "✅ CRM sync complete: {{$json.affectedRows}} contacts updated"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{ "node": "Fetch CRM Data" }]] },
    "Fetch CRM Data": { "main": [[{ "node": "Transform Data" }]] },
    "Transform Data": { "main": [[{ "node": "Upsert to Database" }]] },
    "Upsert to Database": { "main": [[{ "node": "Notify on Complete" }]] }
  }
}
```

#### Template B: Notification Pipeline

```yaml
# Notification Pipeline: Monitor → Evaluate → Route → Notify
workflow:
  name: "Smart Notification Pipeline"
  trigger:
    type: webhook
    path: "/alerts"
    method: POST

  nodes:
    - name: "Evaluate Severity"
      type: Switch
      field: "{{ $json.severity }}"
      routes:
        critical: "PagerDuty + Slack + Email"
        warning: "Slack + Email"
        info: "Slack only"

    - name: "Enrich Alert"
      type: Code
      code: |
        const alert = $input.first().json;
        return [{
          json: {
            ...alert,
            timestamp: new Date().toISOString(),
            runbook_url: `https://wiki.internal/runbooks/${alert.service}`,
            on_call: await getOnCallEngineer(alert.team)
          }
        }];

    - name: "Send Slack"
      type: Slack
      channel: "#{{ $json.team }}-alerts"
      template: "🚨 *{{ $json.severity | upper }}*: {{ $json.message }}\nService: {{ $json.service }}\nRunbook: {{ $json.runbook_url }}"

    - name: "Send Email"
      type: Email
      condition: "severity in ['critical', 'warning']"
      to: "{{ $json.on_call.email }}"
      subject: "[{{ $json.severity }}] {{ $json.service }}: {{ $json.message }}"

    - name: "Page On-Call"
      type: HTTP Request
      condition: "severity == 'critical'"
      url: "https://api.pagerduty.com/incidents"
      method: POST
```

#### Template C: API Orchestration

```yaml
# API Orchestration: Aggregate data from multiple sources
workflow:
  name: "Multi-API Data Aggregator"
  trigger:
    type: webhook
    path: "/aggregate"
    method: GET

  nodes:
    - name: "Parallel Fetch"
      type: Merge
      mode: multiplex
      sources:
        - name: "Fetch Users"
          type: HTTP Request
          url: "https://api.users.com/v1/users"

        - name: "Fetch Orders"
          type: HTTP Request
          url: "https://api.orders.com/v1/orders"

        - name: "Fetch Analytics"
          type: HTTP Request
          url: "https://api.analytics.com/v1/metrics"

    - name: "Combine Results"
      type: Code
      code: |
        const [users, orders, analytics] = $input.all();
        return [{
          json: {
            users: users.json,
            orders: orders.json,
            analytics: analytics.json,
            generated_at: new Date().toISOString()
          }
        }];

    - name: "Cache Result"
      type: Redis
      operation: set
      key: "aggregated_data"
      ttl: 300

    - name: "Respond"
      type: "Respond to Webhook"
      responseBody: "={{ $json }}"
```

#### Template D: Scheduled Task with Error Handling

```yaml
workflow:
  name: "Daily Report Generator"
  trigger:
    type: cron
    expression: "0 8 * * 1-5"  # Weekdays at 8am

  error_handling:
    global:
      retry:
        maxRetries: 3
        waitBetween: 5000
        backoffFactor: 2
      onError:
        - type: Slack
          channel: "#errors"
          message: "❌ Daily report failed: {{ $execution.error.message }}"
        - type: Email
          to: "ops@company.com"

  nodes:
    - name: "Query Database"
      type: Postgres
      query: |
        SELECT
          date_trunc('day', created_at) as day,
          count(*) as total_orders,
          sum(amount) as revenue
        FROM orders
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY 1
        ORDER BY 1
      retryOnFail: true
      maxRetries: 3

    - name: "Generate Report"
      type: Code
      code: |
        const data = $input.all();
        const report = {
          title: `Weekly Report - ${new Date().toLocaleDateString()}`,
          metrics: data.map(d => d.json),
          total_revenue: data.reduce((sum, d) => sum + d.json.revenue, 0),
          avg_daily_orders: Math.round(
            data.reduce((sum, d) => sum + d.json.total_orders, 0) / data.length
          )
        };
        return [{ json: report }];

    - name: "Send Report"
      type: Email
      to: "team@company.com"
      subject: "{{ $json.title }}"
      html: true
```

---

### 4. n8n API v1 Operations

Use the n8n REST API for programmatic workflow management:

```yaml
# n8n API v1 Endpoints
api:
  base_url: "http://localhost:5678/api/v1"
  authentication:
    type: "API Key"
    header: "X-N8N-API-KEY"
    value: "{{ N8N_API_KEY }}"

  endpoints:
    workflows:
      list:
        method: GET
        path: /workflows
        query:
          active: true
          tags: "production"
          limit: 50

      get:
        method: GET
        path: /workflows/{id}

      create:
        method: POST
        path: /workflows
        body:
          name: "New Workflow"
          nodes: []
          connections: {}
          settings:
            executionOrder: "v1"

      update:
        method: PATCH
        path: /workflows/{id}
        body:
          name: "Updated Workflow"
          active: true

      delete:
        method: DELETE
        path: /workflows/{id}

      activate:
        method: PATCH
        path: /workflows/{id}/activate

      deactivate:
        method: PATCH
        path: /workflows/{id}/deactivate

    executions:
      list:
        method: GET
        path: /executions
        query:
          workflowId: "123"
          status: "error"
          limit: 20

      get:
        method: GET
        path: /executions/{id}

      delete:
        method: DELETE
        path: /executions/{id}

    credentials:
      list:
        method: GET
        path: /credentials

      create:
        method: POST
        path: /credentials
        body:
          name: "My API Key"
          type: "httpHeaderAuth"
          data:
            name: "Authorization"
            value: "Bearer token123"
```

---

### 5. Credential Management

```yaml
# Credential Types and Configuration
credentials:
  types:
    httpHeaderAuth:
      description: "API key in HTTP header"
      fields:
        name: "Authorization"
        value: "Bearer {{ API_TOKEN }}"

    httpBasicAuth:
      description: "Basic authentication"
      fields:
        user: "{{ USERNAME }}"
        password: "{{ PASSWORD }}"

    oAuth2Api:
      description: "OAuth 2.0 flow"
      fields:
        clientId: "{{ CLIENT_ID }}"
        clientSecret: "{{ CLIENT_SECRET }}"
        accessTokenUrl: "https://auth.example.com/oauth/token"
        authUrl: "https://auth.example.com/oauth/authorize"
        scope: "read write"

    postgresDb:
      description: "PostgreSQL connection"
      fields:
        host: "{{ DB_HOST }}"
        port: 5432
        database: "{{ DB_NAME }}"
        user: "{{ DB_USER }}"
        password: "{{ DB_PASSWORD }}"
        ssl: true

  security_practices:
    - "Never hardcode credentials in workflow JSON"
    - "Use environment variables for sensitive values"
    - "Rotate API keys regularly (90 day maximum)"
    - "Use OAuth2 over API keys when available"
    - "Restrict credential access by workflow owner"
    - "Encrypt credentials at rest (n8n default: AES-256)"
```

---

### 6. Error Handling & Retry Strategies

```
ERROR HANDLING PATTERNS
══════════════════════════════════════════════════════════════

Pattern 1: Node-Level Retry
────────────────────────────
  [HTTP Request] ──retry(3, exponential)──▶ [Next Node]
       │ (on permanent failure)
       └──▶ [Error Handler] ──▶ [Slack Notification]

Pattern 2: Error Workflow
────────────────────────────
  Main Workflow fails ──triggers──▶ Error Workflow
                                    │
                                    ├─▶ Log to database
                                    ├─▶ Notify team
                                    └─▶ Create incident ticket

Pattern 3: Try-Catch in Code Node
────────────────────────────
  [Code Node]
  try {
    const result = await fetchData();
    return [{ json: { success: true, data: result } }];
  } catch (error) {
    return [{ json: { success: false, error: error.message } }];
  }
  ├─▶ [If Success] ──▶ [Continue Pipeline]
  └─▶ [If Failure] ──▶ [Handle Error]

Pattern 4: Dead Letter Queue
────────────────────────────
  [Process Item] ──fail after retries──▶ [DLQ Database Table]
       │                                      │
       └── success ──▶ [Continue]       [Manual Review Workflow]
```

```yaml
# Retry Configuration
retry_strategies:
  immediate:
    maxRetries: 3
    waitBetween: 0

  linear_backoff:
    maxRetries: 5
    waitBetween: 2000  # ms, increases linearly

  exponential_backoff:
    maxRetries: 5
    waitBetween: 1000
    backoffFactor: 2  # 1s, 2s, 4s, 8s, 16s

  circuit_breaker:
    failureThreshold: 5
    resetTimeout: 60000  # 1 minute
    halfOpenRequests: 1
```

---

### 7. Docker Deployment

```yaml
# docker-compose.yml for n8n
version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=Europe/Madrid
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${DB_USER}
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
      - N8N_ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168  # 7 days in hours
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    container_name: n8n-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

```bash
# .env file
N8N_USER=admin
N8N_PASSWORD=secure_password_here
N8N_HOST=n8n.yourdomain.com
DB_USER=n8n
DB_PASSWORD=db_secure_password
ENCRYPTION_KEY=$(openssl rand -hex 32)
```

---

### 8. Self-Hosted vs Cloud Comparison

```
DEPLOYMENT COMPARISON
══════════════════════════════════════════════════════════════

Feature               │ Self-Hosted         │ n8n Cloud
──────────────────────┼─────────────────────┼─────────────────
Cost                  │ Infrastructure only │ $20-$300+/month
Data Privacy          │ Full control        │ EU/US servers
Custom Nodes          │ ✅ Full access      │ ✅ Supported
Execution Limits      │ None (your infra)   │ Plan-dependent
Scaling               │ Manual (K8s/Docker) │ Automatic
Maintenance           │ You manage          │ Managed
SSL/TLS               │ You configure       │ Included
Backup                │ You manage          │ Included
Uptime SLA            │ Depends on you      │ 99.9%
Version Control       │ Manual upgrade      │ Auto-updated
──────────────────────┼─────────────────────┼─────────────────
Best For              │ • Data sovereignty  │ • Quick start
                      │ • High volume       │ • Small teams
                      │ • Custom infra      │ • Less ops work
══════════════════════════════════════════════════════════════
```

---

### 9. Community Node Integration

```yaml
# Installing Community Nodes
community_nodes:
  installation:
    ui: "Settings → Community Nodes → Install"
    env: "N8N_COMMUNITY_PACKAGES_ENABLED=true"

  popular_nodes:
    - package: "n8n-nodes-google-sheets-trigger"
      description: "Trigger workflows on Google Sheets changes"

    - package: "n8n-nodes-discord"
      description: "Full Discord bot integration"

    - package: "n8n-nodes-puppeteer"
      description: "Web scraping and browser automation"

    - package: "n8n-nodes-openai"
      description: "OpenAI API integration (GPT, DALL-E, Whisper)"

    - package: "n8n-nodes-notion"
      description: "Notion database and page management"

  custom_node_creation:
    steps:
      - "Clone n8n-nodes-starter template"
      - "Define node properties (inputs, parameters, credentials)"
      - "Implement execute() method"
      - "Build with npm run build"
      - "Install locally: npm link in n8n's custom directory"
```

---

## Best Practices

1. **Name workflows descriptively**: Use pattern `[Trigger] Domain: Action` (e.g., `[Cron] Orders: Daily Report`)
2. **Use error workflows**: Every production workflow should have an error handler
3. **Tag and organize**: Use tags for environment (production, staging), domain (sales, ops), and frequency
4. **Version your workflows**: Export workflow JSON and commit to git on every change
5. **Test before activating**: Use manual execution to verify each node before setting the workflow active
6. **Limit webhook exposure**: Use authentication on all webhook triggers in production
7. **Prune execution logs**: Configure `EXECUTIONS_DATA_PRUNE=true` to avoid disk bloat
8. **Use sub-workflows**: Break complex workflows into reusable sub-workflows called via Execute Workflow node
9. **Monitor execution metrics**: Track success/failure rates and execution times
10. **Keep credentials separate**: Never embed credentials in workflow JSON; always use the credential store

---

## Examples

### Example 1: Create a Simple Webhook-to-Slack Workflow

**User**: "Create an n8n workflow that receives a webhook POST with a message and sends it to Slack."

**Agent generates**:

```json
{
  "name": "[Webhook] Notifications: Forward to Slack",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "webhookId": "msg-to-slack",
      "parameters": {
        "httpMethod": "POST",
        "path": "notify",
        "responseMode": "onReceived",
        "responseData": "allEntries"
      }
    },
    {
      "name": "Send to Slack",
      "type": "n8n-nodes-base.slack",
      "position": [500, 300],
      "parameters": {
        "channel": "#notifications",
        "text": "📬 *New notification*\n{{ $json.body.message }}\n_Source: {{ $json.body.source || 'unknown' }}_",
        "otherOptions": {}
      },
      "credentials": {
        "slackApi": { "id": "1", "name": "Slack Bot" }
      }
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Send to Slack", "type": "main", "index": 0 }]] }
  }
}
```

**Test**: `curl -X POST http://localhost:5678/webhook/notify -H "Content-Type: application/json" -d '{"message":"Hello from automation!","source":"test"}'`

---

### Example 2: Deploy n8n with Docker

**User**: "Help me deploy n8n self-hosted with Docker and PostgreSQL."

**Agent**:
1. Generates the `docker-compose.yml` from Section 7
2. Creates the `.env` file with secure defaults
3. Provides deployment commands:

```bash
# 1. Create project directory
mkdir n8n-deployment && cd n8n-deployment

# 2. Create .env file (edit with your values)
cp .env.example .env

# 3. Generate encryption key
echo "ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env

# 4. Start services
docker compose up -d

# 5. Check status
docker compose ps

# 6. View logs
docker compose logs -f n8n

# 7. Access UI
# Open http://localhost:5678 and log in with N8N_USER/N8N_PASSWORD
```

---

### Example 3: Query n8n API to List Failed Executions

**User**: "Show me all failed workflow executions from the last 24 hours."

**Agent**:

```bash
# List failed executions via n8n API v1
curl -s "http://localhost:5678/api/v1/executions?status=error&limit=50" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" | jq '
  .data[] | {
    id: .id,
    workflow: .workflowData.name,
    startedAt: .startedAt,
    stoppedAt: .stoppedAt,
    error: .data.resultData.error.message
  }'
```

Expected output:
```json
{
  "id": "1042",
  "workflow": "[Cron] Orders: Daily Report",
  "startedAt": "2026-02-22T08:00:01.234Z",
  "stoppedAt": "2026-02-22T08:00:05.678Z",
  "error": "Connection refused: postgres:5432"
}
```
