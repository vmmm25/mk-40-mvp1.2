---
name: deepwiki
version: 1.0.0
description: Query any GitHub repository's documentation and codebase using DeepWiki via MCP or API. Get AI-powered answers about repo architecture, APIs, dependencies, and usage patterns.
tags: [deepwiki, github, documentation, mcp, code-search, repo-analysis, ai-tools]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# DeepWiki Skill

## What is DeepWiki?

DeepWiki (deepwiki.com) automatically generates AI-powered wikis for any GitHub repo. It analyzes the codebase, README, docs, and structure to answer questions like:
- "How do I configure this library?"
- "What are the main modules and their responsibilities?"
- "How does the authentication system work?"
- "Show me examples of how to use [function/class]"

## Access Methods

### Method 1: Web Interface (No Setup)

Visit: `https://deepwiki.com/{owner}/{repo}`

Examples:
- `https://deepwiki.com/vercel/next.js`
- `https://deepwiki.com/langchain-ai/langchain`
- `https://deepwiki.com/anthropics/anthropic-sdk-python`

### Method 2: MCP Server (Claude Desktop / Cursor / Copilot)

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "deepwiki": {
      "command": "uvx",
      "args": ["mcp-deepwiki"],
      "env": {}
    }
  }
}
```

Install the MCP server:
```bash
uvx install mcp-deepwiki
# or
pip install mcp-deepwiki
```

### Method 3: Direct API Queries via Requests

```python
import requests
from typing import Optional

DEEPWIKI_BASE = "https://deepwiki.com"

def ask_deepwiki(repo: str, question: str, token: Optional[str] = None) -> dict:
    """
    Ask a question about a GitHub repository using DeepWiki.
    
    Args:
        repo: "owner/repo" format (e.g., "langchain-ai/langchain")
        question: Natural language question about the repo
        token: Optional DeepWiki API token for private repos
    
    Returns:
        Answer with sources/citations
    """
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "repo": repo,
        "question": question,
    }
    
    response = requests.post(
        f"{DEEPWIKI_BASE}/api/ask",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def get_repo_wiki(repo: str) -> dict:
    """Get the generated wiki/overview of a repo."""
    response = requests.get(
        f"{DEEPWIKI_BASE}/api/wiki/{repo}",
        timeout=30
    )
    response.raise_for_status()
    return response.json()
```

## Common Query Patterns

```python
# Architecture overview
ask_deepwiki("langchain-ai/langchain", "What is the overall architecture? What are the main modules?")

# Getting started
ask_deepwiki("vercel/next.js", "How do I set up app router with server components and fetch data?")

# API reference
ask_deepwiki("anthropics/anthropic-sdk-python", "How do I use tool_use / function calling with Claude?")

# Configuration
ask_deepwiki("fastapi/fastapi", "How do I configure OAuth2 authentication with JWT tokens?")

# Troubleshooting
ask_deepwiki("openai/openai-python", "How do I handle rate limit errors and implement retry logic?")

# Contributing
ask_deepwiki("huggingface/transformers", "What is the process for adding a new model?")

# Migration
ask_deepwiki("tiangolo/fastapi", "How do I migrate from Flask to FastAPI? What are the main differences?")
```

## MCP Tool Usage (when connected via MCP)

When DeepWiki MCP is active in Claude/Copilot, these tools become available:

```
# Ask about a repo
tool: deepwiki_ask
params: {
  "repo": "langchain-ai/langchain",
  "question": "How do I create a custom tool?"
}

# Get wiki page
tool: deepwiki_get_wiki
params: {
  "repo": "openai/openai-python",
  "page": "authentication"
}

# Search codebase
tool: deepwiki_search
params: {
  "repo": "fastapi/fastapi",
  "query": "dependency injection"
}
```

## Batch Repo Analysis

```python
def analyze_multiple_repos(repos: list[str], questions: list[str]) -> dict:
    """
    Ask the same questions across multiple repos for comparison.
    E.g., compare how different frameworks handle authentication.
    """
    results = {}
    for repo in repos:
        results[repo] = {}
        for question in questions:
            try:
                answer = ask_deepwiki(repo, question)
                results[repo][question] = answer.get("answer", "No answer")
            except Exception as e:
                results[repo][question] = f"Error: {str(e)}"
    return results

# Compare authentication approaches
repos = ["tiangolo/fastapi", "pallets/flask", "encode/starlette"]
questions = [
    "How is authentication handled?",
    "What middleware options are available?",
    "How do I add JWT authentication?"
]
comparison = analyze_multiple_repos(repos, questions)
```

## Research Workflow: Understanding a New Library

```python
def onboard_to_repo(repo: str) -> dict:
    """Complete onboarding analysis of a new repository."""
    onboarding_questions = [
        "What does this library do? Give me a 3-sentence summary.",
        "What are the main classes/functions I need to learn?",
        "Show me the minimal working example to get started.",
        "What are the most common patterns used in production?",
        "What are the common pitfalls or gotchas to avoid?",
        "What are the main dependencies and why are they needed?",
        "How is the project structured? What's in each main directory?",
    ]
    
    report = {"repo": repo, "answers": {}}
    for q in onboarding_questions:
        try:
            result = ask_deepwiki(repo, q)
            report["answers"][q] = result.get("answer", "")
        except Exception as e:
            report["answers"][q] = f"Skipped: {e}"
    
    return report

# Quick onboarding report
report = onboard_to_repo("replicate/replicate-python")
for question, answer in report["answers"].items():
    print(f"\n### {question}")
    print(answer[:300])
```

## Integration with Code Generation

```python
def generate_code_from_repo(repo: str, task: str) -> str:
    """
    Ask DeepWiki to generate code that uses a specific repo correctly.
    
    Examples:
    - "Write code to send a message to Slack using the official SDK"
    - "Show me how to create a RAG pipeline with LangChain"
    - "How do I stream responses with the Anthropic Python SDK?"
    """
    question = f"Write complete, working Python code to: {task}. Use the actual API/patterns from this repo. Include imports."
    result = ask_deepwiki(repo, question)
    return result.get("answer", "No code generated")

# Examples:
code = generate_code_from_repo(
    "langchain-ai/langchain",
    "create a RAG pipeline with FAISS vector store and OpenAI embeddings"
)
print(code)
```

## Tips for Better Queries

```markdown
## Good query patterns:

✅ Specific: "How do I configure OAuth2 with Google provider?"
✅ Context: "I'm building a REST API. How do I add rate limiting?"
✅ Code-focused: "Show me an example of using async/await with FastAPI routes"
✅ Comparison: "What's the difference between app.get() and APIRouter?"

## Weak queries (avoid):

❌ Vague: "How does this work?"
❌ Too broad: "Explain everything about authentication"
❌ Generic: "What is Python?"

## Best repos to query:

• Documentation-heavy repos work best
• Projects with good README + docstrings
• Active repos with recent commits
• Any repo on GitHub with >100 stars
```

## References
- [DeepWiki](https://deepwiki.com) — Main web interface
- [mcp-deepwiki](https://github.com/regenrek/mcp-deepwiki) — MCP server
- [MCP Protocol](https://modelcontextprotocol.io/) — How MCP works
- [Devin DeepWiki](https://cognition.ai/blog/deepwiki) — Background article
