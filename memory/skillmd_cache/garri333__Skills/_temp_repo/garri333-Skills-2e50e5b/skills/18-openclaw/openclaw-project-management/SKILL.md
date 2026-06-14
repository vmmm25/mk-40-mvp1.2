---
name: openclaw-project-management
version: 1.0.0
description: Gestión de proyectos con patrón task-observer — planificación, descomposición de tareas, sprints, kanban, tracking de dependencias, reporting de progreso, identificación de riesgos, hitos e integración con GitHub Projects, Linear y Jira.
tags: [openclaw, project-management, task-tracking, sprint, kanban, github-projects, linear, jira, planning, milestones]
author: garri333
license: MIT
source: VoltAgent/awesome-openclaw-skills
---

# OpenClaw Project Management Skill

> Gestión de proyectos con el patrón task-observer. Planifica, descompone, asigna, trackea y reporta progreso de tareas integrándose con las principales plataformas de gestión.

## Cuándo activar

- Cuando se inicia un **nuevo proyecto** o feature significativa que requiere planificación
- Cuando hay que **descomponer un objetivo** en tareas manejables
- Cuando se necesita **tracking de progreso** y visibilidad del estado del proyecto
- Cuando hay **dependencias** entre tareas que deben gestionarse
- Cuando se requiere **sprint planning** o gestión de backlog
- Cuando el equipo necesita **dashboards de estado** y reporting
- Cuando hay que identificar y gestionar **riesgos** del proyecto
- Cuando se trabaja con **GitHub Projects, Linear o Jira** y se necesita sincronización

## Instrucciones paso a paso

### 1. Patrón Task-Observer

```python
class TaskObserver:
    """
    Patrón Observer aplicado a gestión de tareas.
    Los observers reaccionan a cambios de estado en tareas.
    """
    
    def __init__(self):
        self.observers: dict[str, list[Callable]] = {
            "task_created": [],
            "task_updated": [],
            "task_completed": [],
            "task_blocked": [],
            "sprint_started": [],
            "sprint_completed": [],
            "milestone_reached": [],
            "risk_identified": [],
        }
    
    def subscribe(self, event: str, callback: Callable):
        self.observers[event].append(callback)
    
    def notify(self, event: str, data: dict):
        for callback in self.observers[event]:
            callback(data)


class ProjectManager:
    """Gestor central de proyecto con task-observer."""
    
    def __init__(self, project_name: str):
        self.project = Project(name=project_name)
        self.observer = TaskObserver()
        
        # Registrar observers por defecto
        self.observer.subscribe("task_completed", self.check_dependencies)
        self.observer.subscribe("task_completed", self.update_progress)
        self.observer.subscribe("task_blocked", self.notify_blockers)
        self.observer.subscribe("milestone_reached", self.generate_report)
        self.observer.subscribe("risk_identified", self.escalate_risk)
```

### 2. Planificación y descomposición de proyectos

```python
class ProjectPlanner:
    """Descompone un objetivo en tareas accionables."""
    
    def plan_project(self, objective: str, constraints: dict = None) -> ProjectPlan:
        """
        Descomposición jerárquica:
        Proyecto → Épicas → Historias → Tareas → Subtareas
        """
        plan = ProjectPlan(
            objective=objective,
            created_at=datetime.utcnow(),
            constraints=constraints or {}
        )
        
        # Nivel 1: Identificar épicas
        epics = self.decompose_to_epics(objective)
        
        for epic in epics:
            # Nivel 2: Descomponer épica en historias de usuario
            stories = self.decompose_to_stories(epic)
            
            for story in stories:
                # Nivel 3: Descomponer historia en tareas técnicas
                tasks = self.decompose_to_tasks(story)
                
                # Estimar cada tarea
                for task in tasks:
                    task.estimate = self.estimate_task(task)
                    task.dependencies = self.identify_dependencies(task, plan)
                    task.risk_level = self.assess_task_risk(task)
                
                story.tasks = tasks
            epic.stories = stories
        
        plan.epics = epics
        plan.total_estimate = sum(t.estimate for t in plan.all_tasks())
        plan.critical_path = self.calculate_critical_path(plan)
        
        return plan
    
    def decompose_to_tasks(self, story: UserStory) -> list[Task]:
        """Genera tareas técnicas para una historia de usuario."""
        return [
            Task(
                id=generate_id(),
                title=title,
                description=desc,
                story_id=story.id,
                status="backlog",
                priority=priority,
                labels=labels,
                assignee=None,
                estimate_hours=None,
                dependencies=[],
                subtasks=[]
            )
            for title, desc, priority, labels
            in analyze_story_requirements(story)
        ]
```

```yaml
# .openclaw/project/plan.yaml — Ejemplo de plan de proyecto
project:
  name: "Migración API v2"
  objective: "Migrar API REST v1 a v2 con GraphQL y autenticación OAuth2"
  start_date: "2026-02-10"
  target_date: "2026-03-15"
  
  epics:
    - id: "E001"
      title: "Setup GraphQL"
      status: "in_progress"
      stories:
        - id: "S001"
          title: "Como developer, quiero un schema GraphQL para queries de usuarios"
          tasks:
            - id: "T001"
              title: "Definir schema GraphQL para User"
              status: "done"
              estimate_hours: 4
              assignee: "dev1"
            - id: "T002"
              title: "Implementar resolvers de User"
              status: "in_progress"
              estimate_hours: 8
              assignee: "dev1"
              depends_on: ["T001"]
            - id: "T003"
              title: "Tests de integración GraphQL"
              status: "backlog"
              estimate_hours: 6
              depends_on: ["T002"]
    
    - id: "E002"
      title: "Autenticación OAuth2"
      status: "backlog"
      depends_on: ["E001"]
```

### 3. Sprint planning y Kanban

```python
class SprintManager:
    """Gestión de sprints y tablero Kanban."""
    
    KANBAN_COLUMNS = ["backlog", "todo", "in_progress", "review", "done"]
    
    def plan_sprint(
        self, 
        backlog: list[Task], 
        capacity_hours: int, 
        sprint_days: int = 14
    ) -> Sprint:
        """
        Selecciona tareas del backlog para el sprint basándose en:
        - Prioridad
        - Dependencias resueltas
        - Capacidad del equipo
        """
        sprint = Sprint(
            id=generate_sprint_id(),
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=sprint_days),
            capacity_hours=capacity_hours,
            tasks=[]
        )
        
        available_hours = capacity_hours
        
        # Ordenar backlog por prioridad (urgente > alto > medio > bajo)
        sorted_backlog = sorted(backlog, key=lambda t: t.priority_score, reverse=True)
        
        for task in sorted_backlog:
            # Verificar que dependencias están completadas
            if not self.dependencies_resolved(task):
                continue
            
            if task.estimate_hours <= available_hours:
                sprint.tasks.append(task)
                task.status = "todo"
                task.sprint_id = sprint.id
                available_hours -= task.estimate_hours
            
            if available_hours <= 0:
                break
        
        sprint.committed_hours = capacity_hours - available_hours
        self.observer.notify("sprint_started", sprint.to_dict())
        
        return sprint
    
    def get_kanban_board(self, sprint_id: str = None) -> KanbanBoard:
        """Genera el tablero Kanban actual."""
        tasks = get_sprint_tasks(sprint_id) if sprint_id else get_all_active_tasks()
        
        board = {}
        for column in self.KANBAN_COLUMNS:
            board[column] = [t for t in tasks if t.status == column]
        
        return KanbanBoard(
            columns=board,
            wip_limits={"in_progress": 3, "review": 2},
            blocked=[t for t in tasks if t.is_blocked]
        )
    
    def move_task(self, task_id: str, new_status: str):
        """Mueve tarea en el Kanban con validaciones."""
        task = get_task(task_id)
        old_status = task.status
        
        # Validar transición
        valid_transitions = {
            "backlog": ["todo"],
            "todo": ["in_progress", "backlog"],
            "in_progress": ["review", "todo", "blocked"],
            "review": ["done", "in_progress"],
            "done": []  # Final state
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            raise InvalidTransition(f"Cannot move from {old_status} to {new_status}")
        
        # Check WIP limits
        if new_status == "in_progress":
            current_wip = count_tasks_in_status("in_progress")
            if current_wip >= self.wip_limits["in_progress"]:
                raise WIPLimitExceeded("WIP limit reached for in_progress")
        
        task.status = new_status
        task.updated_at = datetime.utcnow()
        save_task(task)
        
        self.observer.notify("task_updated", {
            "task_id": task_id, 
            "from": old_status, 
            "to": new_status
        })
        
        if new_status == "done":
            self.observer.notify("task_completed", task.to_dict())
```

### 4. Tracking de dependencias

```python
class DependencyTracker:
    """Gestión de dependencias entre tareas."""
    
    def add_dependency(self, task_id: str, depends_on: str):
        """Añade dependencia verificando que no haya ciclos."""
        if self.creates_cycle(task_id, depends_on):
            raise CyclicDependency(
                f"Adding {depends_on} as dependency of {task_id} creates a cycle"
            )
        
        task = get_task(task_id)
        task.dependencies.append(depends_on)
        save_task(task)
    
    def creates_cycle(self, task_id: str, new_dep: str) -> bool:
        """DFS para detectar ciclos en el grafo de dependencias."""
        visited = set()
        
        def dfs(current):
            if current == task_id:
                return True
            if current in visited:
                return False
            visited.add(current)
            task = get_task(current)
            return any(dfs(dep) for dep in task.dependencies)
        
        return dfs(new_dep)
    
    def get_critical_path(self, project: Project) -> list[Task]:
        """Calcula el camino crítico del proyecto (cadena más larga)."""
        # Topological sort + longest path
        tasks = project.all_tasks()
        
        # Calcular longest path desde cada nodo
        memo = {}
        
        def longest_from(task_id):
            if task_id in memo:
                return memo[task_id]
            task = get_task(task_id)
            dependents = [t for t in tasks if task_id in t.dependencies]
            
            if not dependents:
                memo[task_id] = (task.estimate_hours, [task])
                return memo[task_id]
            
            best = max(
                [(task.estimate_hours + longest_from(d.id)[0], 
                  [task] + longest_from(d.id)[1]) 
                 for d in dependents],
                key=lambda x: x[0]
            )
            memo[task_id] = best
            return best
        
        # Encontrar inicio (tareas sin dependencias)
        roots = [t for t in tasks if not t.dependencies]
        critical = max([longest_from(r.id) for r in roots], key=lambda x: x[0])
        
        return critical[1]
    
    def check_blockers(self) -> list[BlockerReport]:
        """Identifica tareas bloqueadas por dependencias no resueltas."""
        blocked = []
        
        for task in get_all_active_tasks():
            unresolved = [
                dep for dep in task.dependencies 
                if get_task(dep).status != "done"
            ]
            if unresolved and task.status in ["todo", "in_progress"]:
                blocked.append(BlockerReport(
                    task=task,
                    blocked_by=unresolved,
                    estimated_delay=sum(get_task(d).estimate_hours for d in unresolved),
                    suggestion=self.suggest_unblock(task, unresolved)
                ))
        
        return blocked
```

### 5. Progress reporting y dashboards

```python
class ProgressReporter:
    """Genera reportes de progreso y dashboards."""
    
    def generate_status_dashboard(self, project: Project) -> Dashboard:
        tasks = project.all_tasks()
        sprint = get_current_sprint()
        
        return Dashboard(
            project_name=project.name,
            
            # Progreso general
            overall_progress=count_done(tasks) / len(tasks) * 100,
            tasks_total=len(tasks),
            tasks_done=count_done(tasks),
            tasks_in_progress=count_in_status(tasks, "in_progress"),
            tasks_blocked=count_blocked(tasks),
            
            # Sprint actual
            sprint_progress=sprint.progress_percentage if sprint else None,
            sprint_burndown=self.calculate_burndown(sprint),
            days_remaining=sprint.days_remaining if sprint else None,
            
            # Velocity
            velocity_current=self.calculate_velocity(last_n_sprints=1),
            velocity_avg=self.calculate_velocity(last_n_sprints=3),
            velocity_trend=self.velocity_trend(),
            
            # Riesgos
            active_risks=get_active_risks(project),
            blockers=DependencyTracker().check_blockers(),
            
            # Milestones
            next_milestone=get_next_milestone(project),
            milestones_completed=count_completed_milestones(project),
            milestones_total=count_total_milestones(project),
            
            # Timeline
            estimated_completion=self.estimate_completion(project),
            on_track=self.is_on_track(project),
        )
    
    def generate_sprint_report(self, sprint: Sprint) -> SprintReport:
        """Reporte al final del sprint."""
        return SprintReport(
            sprint_id=sprint.id,
            committed=len(sprint.tasks),
            completed=count_done(sprint.tasks),
            carried_over=[t for t in sprint.tasks if t.status != "done"],
            velocity=sum(t.story_points for t in sprint.tasks if t.status == "done"),
            burndown_chart=self.generate_burndown_data(sprint),
            retrospective_items={
                "went_well": [],      # Se llena con input
                "needs_improvement": [],
                "action_items": [],
            }
        )
```

```
# Dashboard de ejemplo (texto)
═══════════════════════════════════════════════════
  📊 PROJECT: Migración API v2
  Updated: 2026-02-15 14:30
═══════════════════════════════════════════════════

  Progress: ████████░░░░░░░░ 52% (26/50 tasks)

  Sprint 3 (Feb 10-24):
    ████████████░░░░ 75% (9/12 tasks)
    Days remaining: 9
    Burndown: On track ✓

  Velocity: 24 pts/sprint (avg: 22)

  ⚠ Blockers: 2
    - T018: Blocked by T015 (OAuth config)
    - T023: Blocked by external API access

  🎯 Next Milestone: "Alpha Release" — Feb 28
    Progress: 68% (17/25 tasks)

  📈 Estimated completion: Mar 12 (target: Mar 15) ✓
═══════════════════════════════════════════════════
```

### 6. Integración con plataformas

```python
class PlatformIntegration:
    """Sincronización bidireccional con GitHub Projects, Linear, Jira."""
    
    def sync_github_projects(self, project: Project, gh_project_id: str):
        """Sincroniza con GitHub Projects v2."""
        for task in project.all_tasks():
            existing = gh_api.find_item(gh_project_id, task.external_id)
            
            if existing:
                # Actualizar estado
                gh_api.update_item(gh_project_id, existing.id, {
                    "status": map_status_to_github(task.status),
                    "title": task.title,
                    "assignees": [task.assignee] if task.assignee else [],
                    "labels": task.labels,
                })
            else:
                # Crear nuevo item
                item = gh_api.create_item(gh_project_id, {
                    "title": task.title,
                    "body": task.description,
                    "status": map_status_to_github(task.status),
                })
                task.external_id = item.id
    
    def sync_linear(self, project: Project, team_id: str):
        """Sincroniza con Linear."""
        for task in project.all_tasks():
            linear_api.upsert_issue(team_id, {
                "title": task.title,
                "description": task.description,
                "state": map_status_to_linear(task.status),
                "priority": map_priority_to_linear(task.priority),
                "estimate": task.story_points,
                "labels": task.labels,
            })
    
    def sync_jira(self, project: Project, jira_project_key: str):
        """Sincroniza con Jira."""
        for task in project.all_tasks():
            jira_api.upsert_issue(jira_project_key, {
                "summary": task.title,
                "description": task.description,
                "status": map_status_to_jira(task.status),
                "priority": map_priority_to_jira(task.priority),
                "story_points": task.story_points,
                "assignee": task.assignee,
                "sprint": task.sprint_id,
            })
```

### 7. Identificación de riesgos

```python
class RiskIdentifier:
    """Identifica riesgos del proyecto automáticamente."""
    
    def scan_risks(self, project: Project) -> list[Risk]:
        risks = []
        
        # Riesgo 1: Scope creep
        new_tasks_this_sprint = count_tasks_added_during_sprint()
        if new_tasks_this_sprint > 3:
            risks.append(Risk(
                type="scope_creep",
                severity="HIGH",
                detail=f"{new_tasks_this_sprint} tareas añadidas mid-sprint",
                mitigation="Revisar y priorizar. Mover tareas no críticas al próximo sprint."
            ))
        
        # Riesgo 2: Velocidad decreciente
        if self.velocity_declining(last_n=3):
            risks.append(Risk(
                type="velocity_decline",
                severity="MEDIUM",
                detail="Velocidad ha decrecido 3 sprints consecutivos",
                mitigation="Investigar causas. Reducir WIP. Pair programming."
            ))
        
        # Riesgo 3: Dependencias externas
        external_blocks = [t for t in project.all_tasks() if t.blocked_by_external]
        if external_blocks:
            risks.append(Risk(
                type="external_dependency",
                severity="HIGH",
                detail=f"{len(external_blocks)} tareas bloqueadas por dependencias externas",
                mitigation="Contactar equipos externos. Buscar alternativas."
            ))
        
        # Riesgo 4: Deadline en peligro
        estimated = self.estimate_completion(project)
        if estimated > project.target_date:
            delay_days = (estimated - project.target_date).days
            risks.append(Risk(
                type="deadline_risk",
                severity="CRITICAL",
                detail=f"Estimación excede deadline por {delay_days} días",
                mitigation="Re-priorizar. Reducir scope. Añadir recursos."
            ))
        
        return risks
```

## Mejores prácticas

1. **Descomponer hasta tareas de 2-8 horas**: Tareas más grandes son difíciles de estimar y trackear
2. **Respetar WIP limits**: No tener más de 3 tareas in_progress simultáneamente
3. **Actualizar estado diariamente**: El tablero solo es útil si refleja la realidad
4. **Identificar dependencias temprano**: Las dependencias no gestionadas son la mayor fuente de bloqueos
5. **Calcular y usar velocidad**: Planificar sprints basándose en velocity histórica, no en deseos
6. **Critical path visible**: Todo el equipo debe conocer y priorizar el camino crítico
7. **Retrospectivas al final de cada sprint**: Mejorar el proceso, no solo el producto
8. **Sincronización bidireccional**: Si se usa una plataforma externa, mantener sync automático
9. **Riesgos revisados semanalmente**: No esperar a que se materialicen
10. **Milestones como checkpoints**: Celebrar logros intermedios para mantener momentum

## Ejemplos

### Ejemplo 1: Planificar nuevo proyecto

```
Usuario: "Necesito migrar la API de REST a GraphQL"

→ ProjectPlanner.plan_project("Migrar API REST a GraphQL")

Resultado:
  Epic 1: Schema GraphQL (12h)
    - T1: Definir types (4h)
    - T2: Implementar queries (4h, depends: T1)
    - T3: Implementar mutations (4h, depends: T1)
  
  Epic 2: Resolvers (20h)
    - T4: User resolvers (8h, depends: T2)
    - T5: Product resolvers (8h, depends: T2)
    - T6: Auth middleware (4h)
  
  Epic 3: Testing & Migración (16h)
    - T7: Tests de integración (8h, depends: T4, T5)
    - T8: Migración progresiva (8h, depends: T7)
  
  Critical path: T1 → T2 → T4/T5 → T7 → T8 (36h)
  Estimación: 3 sprints
```

### Ejemplo 2: Sprint planning

```
→ SprintManager.plan_sprint(backlog, capacity_hours=40, sprint_days=14)

Sprint 1 seleccionado:
  Todo: T1 (4h), T2 (4h), T3 (4h), T6 (4h) = 16h committed
  Capacidad restante: 24h para tareas de otros proyectos
  
  Nota: T4 y T5 no incluidos porque dependen de T2 (aún no completada)
```

### Ejemplo 3: Dashboard de progreso

```
→ ProgressReporter.generate_status_dashboard(project)

  Progreso: 52% | Sprint 3: 75%
  Velocity: 24 pts (↑ de 20)
  Blockers: 2 tareas
  Next milestone: Alpha Release (Feb 28) — 68%
  On track: ✓
```

### Ejemplo 4: Riesgo detectado

```
→ RiskIdentifier.scan_risks(project)

⚠ CRITICAL: Deadline en peligro
  Estimación actual: Mar 18 (target: Mar 15)
  Delay: 3 días
  Mitigación sugerida:
    1. Mover T23 (docs) al post-launch
    2. Paralelizar T18 y T19 (asignar 2nd developer)
    3. Reducir scope de T20 (implementación mínima)
```
