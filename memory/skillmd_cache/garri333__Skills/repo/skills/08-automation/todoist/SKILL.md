---
name: todoist
version: 1.0.0
description: Manage tasks, projects, labels, and reminders via the Todoist REST API v2. Create tasks from natural language, bulk manage projects, and integrate with any workflow.
tags: [todoist, tasks, productivity, gtd, automation, reminders, projects]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Todoist Skill

## Setup

```bash
pip install todoist-api-python python-dotenv
```

`.env`:
```
TODOIST_API_TOKEN=your_api_token_here
```
Get your token at: https://todoist.com/prefs/integrations → API token

## Initialize Client

```python
from todoist_api_python.api import TodoistAPI
import os
from dotenv import load_dotenv

load_dotenv()
api = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
```

## Projects

```python
def list_projects():
    """List all projects."""
    return [(p.id, p.name, p.color) for p in api.get_projects()]

def create_project(name: str, color: str = "blue", favorite: bool = False):
    """Create a new project."""
    project = api.add_project(name=name, color=color, is_favorite=favorite)
    return {"id": project.id, "name": project.name}

def delete_project(project_id: str):
    """Delete a project and all its tasks."""
    return api.delete_project(project_id=project_id)

def get_project_by_name(name: str):
    """Find a project by name."""
    projects = api.get_projects()
    return next((p for p in projects if p.name.lower() == name.lower()), None)
```

## Tasks

```python
def get_tasks(project_id: str = None, label: str = None, filter_str: str = None):
    """Get tasks with optional filtering."""
    kwargs = {}
    if project_id:
        kwargs["project_id"] = project_id
    if label:
        kwargs["label"] = label
    if filter_str:
        kwargs["filter"] = filter_str

    tasks = api.get_tasks(**kwargs)
    return [{"id": t.id, "content": t.content, "due": t.due, "priority": t.priority, "labels": t.labels} for t in tasks]

def add_task(
    content: str,
    project_name: str = None,
    due_string: str = None,
    priority: int = 1,   # 1=normal, 2=medium, 3=high, 4=urgent
    labels: list[str] = None,
    description: str = None
):
    """Add a task. due_string accepts natural language: 'tomorrow', 'next Monday', 'every Friday'."""
    project_id = None
    if project_name:
        project = get_project_by_name(project_name)
        if project:
            project_id = project.id

    kwargs = {
        "content": content,
        "priority": priority,
    }
    if project_id:
        kwargs["project_id"] = project_id
    if due_string:
        kwargs["due_string"] = due_string
    if labels:
        kwargs["labels"] = labels
    if description:
        kwargs["description"] = description

    task = api.add_task(**kwargs)
    return {"id": task.id, "content": task.content, "due": task.due}

def complete_task(task_id: str):
    """Mark a task as complete."""
    return api.close_task(task_id=task_id)

def update_task(task_id: str, **kwargs):
    """Update task properties. Accepts: content, due_string, priority, labels, description."""
    return api.update_task(task_id=task_id, **kwargs)

def delete_task(task_id: str):
    """Delete a task permanently."""
    return api.delete_task(task_id=task_id)
```

## Natural Language Task Creation

```python
def add_task_natural(text: str):
    """
    Parse natural language to create structured tasks.
    
    Examples:
      "Review proposal #Work @high tomorrow"
      "Call dentist p1 next friday"
      "Team standup every weekday at 9:30am #Meetings @recurring"
    """
    # Todoist handles natural language in content + due_string
    # Extract project from #ProjectName
    import re
    project_match = re.search(r'#(\w+)', text)
    project_name = project_match.group(1) if project_match else None
    content = re.sub(r'#\w+', '', text).strip()

    # Extract priority from p1/p2/p3/p4 or @high/@urgent
    priority = 1
    priority_match = re.search(r'\bp([1-4])\b', text, re.IGNORECASE)
    if priority_match:
        p = int(priority_match.group(1))
        priority = 5 - p  # p1→4 (urgent), p4→1 (normal)
        content = re.sub(r'\bp[1-4]\b', '', content, flags=re.IGNORECASE).strip()

    return add_task(
        content=content,
        project_name=project_name,
        priority=priority,
        due_string=None  # Todoist auto-parsing handles this in content
    )
```

## Sections

```python
def list_sections(project_id: str):
    """List sections within a project."""
    return [(s.id, s.name) for s in api.get_sections(project_id=project_id)]

def create_section(project_id: str, name: str):
    """Create a new section inside a project."""
    section = api.add_section(name=name, project_id=project_id)
    return {"id": section.id, "name": section.name}

def add_task_to_section(content: str, section_id: str, **kwargs):
    """Add a task to a specific section."""
    return api.add_task(content=content, section_id=section_id, **kwargs)
```

## Labels

```python
def list_labels():
    """List all personal labels."""
    return [(l.id, l.name, l.color) for l in api.get_labels()]

def create_label(name: str, color: str = "blue"):
    """Create a new label."""
    label = api.add_label(name=name, color=color)
    return {"id": label.id, "name": label.name}

def get_tasks_by_label(label_name: str):
    """Get all tasks with a specific label."""
    return get_tasks(label=label_name)
```

## Filters (Power User)

```python
# Todoist filter syntax examples:
FILTERS = {
    "today":          "today",
    "overdue":        "overdue",
    "next_7_days":    "7 days",
    "high_priority":  "p1",
    "work_due":       "#Work & due before: +3 days",
    "no_due_date":    "no due date & !recurring",
    "created_today":  "created: today",
    "assigned_to_me": "assigned to: me",
}

def get_tasks_by_filter(filter_name: str):
    """Get tasks using a named filter."""
    filter_str = FILTERS.get(filter_name, filter_name)
    return get_tasks(filter_str=filter_str)

def get_daily_plan():
    """Get today's tasks sorted by priority."""
    tasks = get_tasks(filter_str="today | overdue")
    return sorted(tasks, key=lambda t: t["priority"], reverse=True)
```

## Bulk Operations

```python
def import_tasks_from_list(task_list: list[dict]):
    """
    Import multiple tasks at once.
    task_list: [{"content": "...", "project": "...", "due": "...", "priority": 1}]
    """
    results = []
    for task in task_list:
        try:
            result = add_task(
                content=task["content"],
                project_name=task.get("project"),
                due_string=task.get("due"),
                priority=task.get("priority", 1),
                labels=task.get("labels", []),
            )
            results.append({"status": "ok", "id": result["id"], "content": task["content"]})
        except Exception as e:
            results.append({"status": "error", "content": task["content"], "error": str(e)})
    return results

def complete_all_in_project(project_name: str):
    """Mark all tasks in a project as complete."""
    project = get_project_by_name(project_name)
    if not project:
        return {"error": "Project not found"}
    tasks = api.get_tasks(project_id=project.id)
    completed = []
    for t in tasks:
        api.close_task(task_id=t.id)
        completed.append(t.content)
    return {"completed": len(completed), "tasks": completed}
```

## Quick Action Patterns

```python
# Add daily review task every morning
add_task("Daily review: prioritize tasks", due_string="every day at 8:00am", priority=3)

# Create a project with sections
project = create_project("Sprint 42")
create_section(project["id"], "Backlog")
create_section(project["id"], "In Progress")
create_section(project["id"], "Done")

# Get everything due today, sorted by priority
daily_plan = get_daily_plan()
for task in daily_plan:
    print(f"[P{5-task['priority']}] {task['content']}")
```

## References
- [Todoist API v2 Docs](https://developer.todoist.com/rest/v2/) — REST API reference
- [todoist-api-python](https://github.com/Doist/todoist-api-python) — Official Python SDK
- [Todoist Filters](https://todoist.com/help/articles/introduction-to-filters) — Filter syntax
