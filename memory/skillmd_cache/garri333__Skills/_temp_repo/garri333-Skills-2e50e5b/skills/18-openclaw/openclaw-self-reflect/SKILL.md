---
name: openclaw-self-reflect
version: 1.0.0
description: Auto-mejora del agente mediante análisis de conversaciones — analiza decisiones, identifica errores, extrae patrones, codifica aprendizajes. Métricas de rendimiento, scoring de calidad, loop de feedback y análisis de gaps de habilidades.
tags: [openclaw, self-reflection, self-improvement, performance-metrics, quality-scoring, feedback-loop, pattern-recognition, learning]
author: garri333
license: MIT
source: VoltAgent/awesome-openclaw-skills
---

# OpenClaw Self-Reflect Skill

> Auto-mejora continua del agente a través de análisis post-sesión. Identifica patrones de error, codifica aprendizajes y genera sugerencias de mejora automáticamente.

## Cuándo activar

- **Al finalizar cada sesión** o conversación significativa
- Cuando el agente comete un **error identificable** y necesita aprender de él
- Cuando se acumulan suficientes sesiones para hacer **análisis de patrones**
- Cuando se quiere evaluar la **calidad de outputs** del agente
- Cuando hay un **feedback negativo** del usuario (corrección, queja, re-intento)
- Periódicamente para **auditorías de rendimiento** (semanal/mensual)
- Cuando se detecta una **brecha de habilidades** en un dominio específico

## Instrucciones paso a paso

### 1. Análisis post-sesión

```python
class SessionAnalyzer:
    """
    Analiza una sesión completada para extraer aprendizajes.
    Se ejecuta automáticamente al cerrar sesión o bajo demanda.
    """
    
    def analyze_session(self, session: Session) -> SessionAnalysis:
        """
        Pipeline de análisis:
        1. Extraer decisiones tomadas
        2. Identificar errores y correcciones
        3. Detectar patrones
        4. Generar aprendizajes
        5. Calcular métricas
        """
        analysis = SessionAnalysis(session_id=session.id)
        
        # Paso 1: Extraer decisiones
        analysis.decisions = self.extract_decisions(session.messages)
        
        # Paso 2: Identificar errores
        analysis.mistakes = self.identify_mistakes(session.messages)
        
        # Paso 3: Detectar patrones
        analysis.patterns = self.detect_patterns(session.messages)
        
        # Paso 4: Generar aprendizajes codificados
        analysis.learnings = self.codify_learnings(
            analysis.decisions, 
            analysis.mistakes, 
            analysis.patterns
        )
        
        # Paso 5: Calcular métricas de calidad
        analysis.metrics = self.calculate_metrics(session)
        
        # Persistir análisis
        self.store_analysis(analysis)
        
        return analysis
    
    def extract_decisions(self, messages: list) -> list[Decision]:
        """
        Identifica puntos de decisión en la conversación:
        - Elección de herramienta/enfoque
        - Trade-offs evaluados
        - Alternativas descartadas
        """
        decisions = []
        
        for i, msg in enumerate(messages):
            if msg.role == "assistant":
                # Detectar decisiones explícitas
                decision_markers = [
                    "elegí", "decidí", "opté por", "voy a usar",
                    "la mejor opción", "en lugar de", "descarto",
                    "prefiero", "tiene más sentido"
                ]
                
                for marker in decision_markers:
                    if marker in msg.content.lower():
                        context = messages[max(0, i-2):i+2]
                        decisions.append(Decision(
                            description=extract_decision_summary(msg.content, marker),
                            context=context,
                            position=i,
                            alternatives=extract_alternatives(msg.content)
                        ))
        
        return decisions
    
    def identify_mistakes(self, messages: list) -> list[Mistake]:
        """
        Detecta errores mediante señales:
        - Correcciones del usuario
        - Re-intentos del agente
        - Errores de ejecución
        - Cambios de enfoque
        """
        mistakes = []
        
        for i, msg in enumerate(messages):
            # Señal 1: Corrección explícita del usuario
            if msg.role == "user":
                correction_markers = [
                    "no, ", "incorrecto", "error", "mal", "eso no",
                    "no funciona", "no es así", "está mal", "corrige"
                ]
                if any(m in msg.content.lower() for m in correction_markers):
                    mistakes.append(Mistake(
                        type="user_correction",
                        description=msg.content[:200],
                        agent_action=messages[i-1].content[:200] if i > 0 else "",
                        position=i,
                        severity=self.assess_severity(msg.content)
                    ))
            
            # Señal 2: Error de ejecución en tool calls
            if msg.role == "tool" and msg.is_error:
                mistakes.append(Mistake(
                    type="execution_error",
                    description=msg.error_message,
                    agent_action=messages[i-1].content[:200] if i > 0 else "",
                    position=i,
                    severity="MEDIUM"
                ))
            
            # Señal 3: Re-intento del agente (mismo tool call con params diferentes)
            if msg.role == "assistant" and i > 2:
                if self.is_retry(messages[i-2], msg):
                    mistakes.append(Mistake(
                        type="retry_needed",
                        description="Agente necesitó reintentar la misma operación",
                        position=i,
                        severity="LOW"
                    ))
        
        return mistakes
```

### 2. Codificación de aprendizajes

```python
class LearningCodifier:
    """
    Transforma errores y patrones en conocimiento reutilizable.
    Los aprendizajes se almacenan como reglas que el agente puede consultar.
    """
    
    def codify_learnings(
        self, decisions: list, mistakes: list, patterns: list
    ) -> list[Learning]:
        learnings = []
        
        # De errores → reglas de "no hacer"
        for mistake in mistakes:
            learning = Learning(
                id=generate_id(),
                type="avoidance_rule",
                trigger=mistake.type,
                rule=self.generate_rule_from_mistake(mistake),
                confidence=self.assess_confidence(mistake),
                source_session=mistake.session_id,
                created_at=datetime.utcnow(),
                times_applied=0
            )
            learnings.append(learning)
        
        # De decisiones exitosas → heurísticas
        successful_decisions = [d for d in decisions if d.outcome == "success"]
        for decision in successful_decisions:
            learning = Learning(
                id=generate_id(),
                type="heuristic",
                trigger=decision.context_type,
                rule=self.generate_heuristic(decision),
                confidence=0.7,  # Inicial, sube con confirmaciones
                source_session=decision.session_id,
                created_at=datetime.utcnow(),
                times_applied=0
            )
            learnings.append(learning)
        
        # De patrones → meta-estrategias
        for pattern in patterns:
            if pattern.frequency >= 3:  # Solo codificar patrones recurrentes
                learning = Learning(
                    id=generate_id(),
                    type="meta_strategy",
                    trigger=pattern.trigger_condition,
                    rule=pattern.strategy,
                    confidence=min(0.5 + pattern.frequency * 0.1, 0.95),
                    source_session="multi",
                    created_at=datetime.utcnow(),
                    times_applied=0
                )
                learnings.append(learning)
        
        return learnings
    
    def generate_rule_from_mistake(self, mistake: Mistake) -> str:
        """Genera una regla natural a partir de un error."""
        templates = {
            "user_correction": (
                f"Cuando {mistake.context}: NO {mistake.agent_action}. "
                f"En su lugar: {mistake.correction}."
            ),
            "execution_error": (
                f"Antes de {mistake.agent_action}: verificar que "
                f"{mistake.precondition_missing}."
            ),
            "retry_needed": (
                f"Para {mistake.operation}: usar parámetros "
                f"{mistake.correct_params} directamente."
            ),
        }
        return templates.get(mistake.type, f"Evitar: {mistake.description}")
```

```yaml
# .openclaw/learnings/rules.yaml — Ejemplo de aprendizajes codificados
learnings:
  - id: "learn_001"
    type: "avoidance_rule"
    rule: >
      Cuando se edita un archivo TypeScript, NO asumir que las importaciones 
      están actualizadas. Siempre verificar las importaciones existentes con 
      grep_search antes de añadir nuevas.
    confidence: 0.92
    times_applied: 7
    last_applied: "2026-02-06"
  
  - id: "learn_002"
    type: "heuristic"
    rule: >
      Para proyectos con monorepo pnpm: buscar pnpm-workspace.yaml primero,
      luego verificar cada package.json antes de ejecutar comandos.
      El install se hace en la raíz, no en subdirectorios.
    confidence: 0.88
    times_applied: 4
  
  - id: "learn_003"
    type: "meta_strategy"
    rule: >
      Cuando el usuario reporta un error de runtime: 1) Leer el error completo,
      2) Buscar el archivo y línea indicados, 3) Leer contexto amplio (±20 líneas),
      4) Buscar uso de la variable/función problemática en otros archivos.
      NO proponer solución antes del paso 4.
    confidence: 0.85
    times_applied: 12
```

### 3. Métricas de rendimiento

```python
class PerformanceMetrics:
    """Tracking de métricas cuantitativas del agente."""
    
    def calculate_metrics(self, session: Session) -> Metrics:
        return Metrics(
            # Eficiencia
            tool_calls_total=count_tool_calls(session),
            tool_calls_successful=count_successful_tools(session),
            tool_success_rate=successful / total if total > 0 else 1.0,
            retries=count_retries(session),
            
            # Calidad
            user_corrections=count_corrections(session),
            user_satisfaction=infer_satisfaction(session),  # 0-1 scale
            first_attempt_success_rate=count_first_attempts_ok(session) / total,
            
            # Complejidad
            session_length=len(session.messages),
            task_complexity=assess_complexity(session),
            
            # Aprendizaje
            new_learnings_generated=0,  # Se actualiza post-análisis
            existing_learnings_applied=count_learnings_used(session),
        )
    
    def aggregate_metrics(self, days: int = 30) -> AggregateMetrics:
        """Agregar métricas de múltiples sesiones."""
        sessions = load_sessions(last_n_days=days)
        all_metrics = [self.calculate_metrics(s) for s in sessions]
        
        return AggregateMetrics(
            period_days=days,
            total_sessions=len(sessions),
            avg_tool_success_rate=mean([m.tool_success_rate for m in all_metrics]),
            avg_user_satisfaction=mean([m.user_satisfaction for m in all_metrics]),
            total_corrections=sum([m.user_corrections for m in all_metrics]),
            improvement_trend=self.calculate_trend(all_metrics),
            top_error_categories=self.top_errors(sessions),
            skill_gaps=self.identify_skill_gaps(sessions),
        )
```

### 4. Quality scoring de outputs

```python
class OutputQualityScorer:
    """Evalúa la calidad de cada output del agente."""
    
    DIMENSIONS = {
        "accuracy": {
            "weight": 0.35,
            "signals": ["no_corrections", "tool_success", "code_compiles"]
        },
        "completeness": {
            "weight": 0.25,
            "signals": ["all_requirements_met", "no_followup_needed"]
        },
        "efficiency": {
            "weight": 0.20,
            "signals": ["minimal_retries", "optimal_tool_count", "concise_response"]
        },
        "style": {
            "weight": 0.10,
            "signals": ["proper_formatting", "clear_explanation", "code_quality"]
        },
        "safety": {
            "weight": 0.10,
            "signals": ["no_sensitive_data", "proper_error_handling"]
        }
    }
    
    def score_output(self, output: AgentOutput, context: SessionContext) -> QualityScore:
        scores = {}
        
        for dimension, config in self.DIMENSIONS.items():
            dimension_score = self.evaluate_dimension(output, context, config["signals"])
            scores[dimension] = dimension_score * config["weight"]
        
        total = sum(scores.values())
        
        return QualityScore(
            total=total,
            breakdown=scores,
            grade=self.to_grade(total),  # A, B, C, D, F
            suggestions=self.generate_suggestions(scores)
        )
```

### 5. Análisis de gaps de habilidades

```python
class SkillGapAnalyzer:
    """Identifica áreas donde el agente tiene debilidades."""
    
    def identify_gaps(self, sessions: list[Session], days: int = 30) -> list[SkillGap]:
        gaps = []
        
        # Agrupar errores por categoría/dominio
        error_clusters = self.cluster_errors(sessions)
        
        for cluster in error_clusters:
            if cluster.frequency >= 3 and cluster.avg_severity >= "MEDIUM":
                gap = SkillGap(
                    domain=cluster.domain,
                    description=f"Errores recurrentes en {cluster.domain}",
                    frequency=cluster.frequency,
                    examples=cluster.top_examples[:3],
                    suggested_skills=self.recommend_skills(cluster.domain),
                    suggested_learnings=self.recommend_learnings(cluster),
                    priority=self.calculate_priority(cluster)
                )
                gaps.append(gap)
        
        return sorted(gaps, key=lambda g: g.priority, reverse=True)
```

### 6. Feedback loop integration

```python
class FeedbackLoop:
    """
    Integra feedback del usuario para refinar aprendizajes.
    Cierra el ciclo: error → learning → aplicación → validación.
    """
    
    def process_feedback(self, feedback: UserFeedback):
        # Buscar learning relacionado
        related_learnings = find_learnings_for_context(feedback.context)
        
        for learning in related_learnings:
            if feedback.is_positive:
                # Reforzar el learning
                learning.confidence = min(learning.confidence + 0.05, 0.99)
                learning.times_validated += 1
            else:
                # Debilitar o marcar para revisión
                learning.confidence = max(learning.confidence - 0.15, 0.0)
                if learning.confidence < 0.3:
                    learning.status = "needs_review"
            
            update_learning(learning)
        
        # Si es feedback negativo sin learning existente → crear nuevo
        if not feedback.is_positive and not related_learnings:
            new_learning = codify_from_feedback(feedback)
            store_learning(new_learning)
    
    def generate_improvement_report(self, days: int = 7) -> ImprovementReport:
        """Genera reporte semanal de mejora."""
        metrics = aggregate_metrics(days)
        gaps = identify_gaps(days)
        learnings = get_recent_learnings(days)
        
        return ImprovementReport(
            period=f"Last {days} days",
            sessions_analyzed=metrics.total_sessions,
            quality_trend=metrics.improvement_trend,
            top_improvements=[l for l in learnings if l.impact == "positive"],
            remaining_gaps=gaps[:5],
            recommendations=generate_recommendations(metrics, gaps),
            overall_score=metrics.avg_user_satisfaction
        )
```

## Mejores prácticas

1. **Ejecutar análisis al final de cada sesión**: No acumular sin analizar; los aprendizajes son más valiosos cuando son frescos
2. **Codificar aprendizajes como reglas concretas y accionables**: "Verificar X antes de Y" es mejor que "tener cuidado con Z"
3. **Validar learnings con uso real**: Un learning sin validar (confidence < 0.5) no se aplica automáticamente
4. **No sobre-corregir**: Un solo error no justifica una regla permanente. Esperar a ver patrón (≥3 ocurrencias)
5. **Separar aprendizajes por dominio**: Los learnings de Python no aplican a Rust
6. **Metrics over feelings**: Basar mejoras en datos cuantitativos, no en impresiones subjetivas
7. **Hacer reports semanales**: Revisión periódica para detectar tendencias
8. **Incluir feedback del usuario**: Las correcciones del usuario son la señal más valiosa
9. **Podar aprendizajes obsoletos**: Reglas con confidence < 0.2 se eliminan automáticamente
10. **Compartir learnings entre proyectos**: Los meta-aprendizajes (sobre herramientas, patrones de código) son portables

## Ejemplos

### Ejemplo 1: Análisis post-sesión

```
Sesión completada: refactoring de componente React.

→ SessionAnalyzer.analyze_session(session)

Decisiones:
  1. Elegí dividir el componente en 3 sub-componentes (vs. 2)
  2. Usé useReducer en lugar de useState para estado complejo

Errores:
  1. [user_correction] Olvidé actualizar las importaciones en App.tsx
  2. [execution_error] replace_string_in_file falló por contexto insuficiente

Aprendizaje codificado:
  "Al refactorizar componentes React: después de mover código, SIEMPRE 
   verificar y actualizar importaciones en TODOS los archivos que lo usan."
  confidence: 0.7
```

### Ejemplo 2: Detección de skill gap

```
→ SkillGapAnalyzer.identify_gaps(last_30_days)

Gap detectado: "Docker & Containerización"
  - 5 errores en 30 días
  - Errores frecuentes: Dockerfile syntax, volume mounts, networking
  - Prioridad: ALTA
  - Sugerencia: Activar skill "docker-advanced"
```

### Ejemplo 3: Reporte de mejora semanal

```
→ FeedbackLoop.generate_improvement_report(days=7)

📊 Reporte de Mejora — Última semana
  Sessions: 23
  Quality trend: ↑ +8% vs. semana anterior
  Tool success rate: 94% (↑ de 89%)
  User corrections: 4 (↓ de 9)
  
  Top mejoras:
    ✓ "Verificar importaciones post-refactor" aplicada 5 veces sin error
    ✓ "Leer contexto amplio antes de editar" redujo retries un 40%
  
  Gaps pendientes:
    ⚠ Docker networking (3 errores)
    ⚠ TypeScript generics avanzados (2 errores)
```

### Ejemplo 4: Feedback loop en acción

```
Usuario corrige: "No, el hook useEffect necesita el dependency array"

→ FeedbackLoop.process_feedback(negative, context="React hooks")
→ Busca learnings existentes sobre React hooks
→ No encuentra → Crea nuevo:
   "En React: SIEMPRE incluir dependency array en useEffect. 
    [] para una vez, [dep1, dep2] para deps específicas."
   confidence: 0.7 (nuevo, pendiente de validación)
```
