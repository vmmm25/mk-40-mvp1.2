---
name: openclaw-reasoning
version: 1.0.0
description: Equilibrium-Native Reasoning (sis-skill) — patrones avanzados de razonamiento para resolución de problemas complejos. Chain-of-thought, tree-of-thought, análisis multi-perspectiva, deducción lógica, razonamiento inductivo, analogías, actualización bayesiana, matrices de decisión y pensamiento de primeros principios.
tags: [openclaw, reasoning, chain-of-thought, tree-of-thought, bayesian, decision-matrix, first-principles, socratic, deduction, problem-solving]
author: garri333
license: MIT
source: VoltAgent/awesome-openclaw-skills
---

# OpenClaw Reasoning Skill (sis-skill)

> Equilibrium-Native Reasoning — patrones avanzados de razonamiento para que agentes autónomos resuelvan problemas complejos de forma estructurada y rigurosa.

## Cuándo activar

- Cuando el problema es **ambiguo o complejo** y no tiene una solución directa obvia
- Cuando hay **múltiples alternativas** y se necesita evaluar trade-offs
- Cuando se requiere **deducción lógica** a partir de datos incompletos
- Cuando el agente necesita **justificar decisiones** con razonamiento transparente
- Cuando hay que realizar **análisis multi-perspectiva** (stakeholders, trade-offs, riesgos)
- Cuando se necesita **explorar un espacio de soluciones** amplio
- Cuando la decisión tiene **impacto significativo** y requiere pensamiento profundo
- Cuando se detecta **incertidumbre** y hay que actualizar creencias con nueva evidencia
- Cuando es necesario **descomponer un problema** hasta sus fundamentos

## Instrucciones paso a paso

### 1. Chain-of-Thought (CoT) — Razonamiento secuencial

```python
class ChainOfThought:
    """
    Razonamiento paso a paso explícito.
    Cada paso es verificable y construye sobre el anterior.
    """
    
    def reason(self, problem: str, context: dict = None) -> ReasoningResult:
        """
        Descompone el problema en pasos de razonamiento secuenciales.
        """
        chain = ReasoningChain(problem=problem)
        
        # Paso 1: Entender el problema
        chain.add_step(Step(
            type="understand",
            content="¿Qué se está pidiendo exactamente?",
            analysis=self.parse_requirements(problem),
            conclusion=None  # Se llena al analizar
        ))
        
        # Paso 2: Identificar información disponible
        chain.add_step(Step(
            type="gather",
            content="¿Qué información tenemos?",
            analysis=self.extract_facts(problem, context),
            conclusion="Hechos clave identificados"
        ))
        
        # Paso 3: Identificar restricciones
        chain.add_step(Step(
            type="constraints",
            content="¿Qué restricciones existen?",
            analysis=self.extract_constraints(problem, context),
            conclusion="Restricciones que limitan la solución"
        ))
        
        # Pasos intermedios: razonamiento
        intermediate_steps = self.generate_reasoning_steps(
            chain.steps, problem
        )
        for step in intermediate_steps:
            chain.add_step(step)
        
        # Paso final: Conclusión
        chain.add_step(Step(
            type="conclude",
            content="¿Cuál es la respuesta/solución?",
            analysis=self.synthesize(chain.steps),
            conclusion=self.derive_conclusion(chain)
        ))
        
        return ReasoningResult(
            chain=chain,
            confidence=self.assess_confidence(chain),
            answer=chain.steps[-1].conclusion
        )
```

```
# Ejemplo de Chain-of-Thought:
Problema: "¿Debemos migrar de MongoDB a PostgreSQL?"

Paso 1 [ENTENDER]: Se pregunta si migrar la base de datos principal
Paso 2 [HECHOS]: 
  - App actual: 50K usuarios, 2M documentos
  - MongoDB 4.4, sin esquema fijo
  - Equipo: 3 devs, experiencia SQL media
  - Problemas actuales: queries JOIN-like lentas, inconsistencia de datos
Paso 3 [RESTRICCIONES]:
  - Budget: 2 sprints máximo para migración
  - Downtime permitido: <4 horas
  - Debe mantener backward compatibility en API
Paso 4 [RAZONAMIENTO]:
  - MongoDB fortalezas: flexibilidad de esquema, horizontal scaling
  - PostgreSQL fortalezas: JOINs, ACID, constraints, extensiones
  - Los problemas actuales (JOINs, inconsistencia) son fortalezas de PostgreSQL
  - Pero: migrar 2M documentos con esquema variable es costoso
Paso 5 [CONCLUSIÓN]:
  Sí migrar, pero con enfoque gradual:
  1. Dual-write pattern durante 2 semanas
  2. Validar consistencia
  3. Switchover con <2h downtime
  Confianza: 0.78
```

### 2. Tree-of-Thought (ToT) — Exploración ramificada

```python
class TreeOfThought:
    """
    Explora múltiples caminos de razonamiento en paralelo.
    Evalúa y poda ramas menos prometedoras.
    """
    
    def explore(
        self, 
        problem: str, 
        breadth: int = 3,
        depth: int = 4,
        prune_threshold: float = 0.3
    ) -> ThoughtTree:
        """
        Genera un árbol de pensamientos con exploración BFS.
        
        Args:
            problem: El problema a resolver
            breadth: Número de ramas por nodo
            depth: Profundidad máxima del árbol
            prune_threshold: Score mínimo para mantener una rama
        """
        tree = ThoughtTree(root=ThoughtNode(content=problem, depth=0))
        
        current_level = [tree.root]
        
        for d in range(depth):
            next_level = []
            
            for node in current_level:
                # Generar múltiples continuaciones
                branches = self.generate_branches(node, breadth)
                
                for branch in branches:
                    # Evaluar promesa de cada rama
                    branch.score = self.evaluate_branch(branch, problem)
                    
                    # Podar ramas poco prometedoras
                    if branch.score >= prune_threshold:
                        node.children.append(branch)
                        next_level.append(branch)
            
            current_level = next_level
            
            if not current_level:
                break
        
        # Encontrar el mejor camino (leaf con mayor score acumulado)
        best_path = self.find_best_path(tree)
        
        return ThoughtTree(
            root=tree.root,
            best_path=best_path,
            all_paths=self.enumerate_paths(tree),
            pruned_count=tree.pruned_count
        )
    
    def evaluate_branch(self, node: ThoughtNode, original_problem: str) -> float:
        """
        Evalúa qué tan prometedora es una rama.
        Criterios: progreso hacia solución, coherencia, factibilidad.
        """
        scores = {
            "progress": self.assess_progress(node, original_problem),
            "coherence": self.assess_coherence(node),
            "feasibility": self.assess_feasibility(node),
            "novelty": self.assess_novelty(node),  # Penalizar redundancia
        }
        
        weights = {"progress": 0.4, "coherence": 0.25, "feasibility": 0.25, "novelty": 0.1}
        
        return sum(scores[k] * weights[k] for k in scores)
```

```
# Ejemplo de Tree-of-Thought:
Problema: "La app se ralentiza con >10K usuarios concurrentes"

Rama A: Optimización de DB
  ├─ A1: Añadir índices → Score: 0.6 (rápido pero limitado)
  ├─ A2: Read replicas → Score: 0.75 (escala reads)
  └─ A3: Caching layer → Score: 0.82 (mayor impacto) ← MEJOR
       ├─ A3a: Redis cache → Score: 0.85 ← MEJOR GLOBAL
       └─ A3b: CDN para estáticos → Score: 0.70

Rama B: Optimización de código
  ├─ B1: Async processing → Score: 0.55
  └─ B2: Connection pooling → Score: 0.65 [PODADO: < A3]

Rama C: Infraestructura
  ├─ C1: Horizontal scaling → Score: 0.72
  └─ C2: Load balancer tuning → Score: 0.45 [PODADO]

Best path: A → A3 (Caching) → A3a (Redis)
```

### 3. Análisis multi-perspectiva

```python
class MultiPerspectiveAnalysis:
    """
    Analiza un problema desde múltiples perspectivas/stakeholders.
    Cada perspectiva aporta criterios y prioridades diferentes.
    """
    
    DEFAULT_PERSPECTIVES = [
        "end_user",       # Experiencia del usuario final
        "developer",      # Mantenibilidad, complejidad técnica
        "business",       # ROI, time-to-market, costes
        "security",       # Riesgos, vulnerabilidades
        "ops",            # Operaciones, escalabilidad, monitorización
        "future",         # Deuda técnica, extensibilidad a 2 años
    ]
    
    def analyze(
        self, 
        problem: str, 
        options: list[str],
        perspectives: list[str] = None
    ) -> MultiPerspectiveResult:
        perspectives = perspectives or self.DEFAULT_PERSPECTIVES
        
        analysis = {}
        
        for perspective in perspectives:
            analysis[perspective] = PerspectiveAnalysis(
                perspective=perspective,
                criteria=self.get_criteria(perspective),
                evaluations={},
            )
            
            for option in options:
                score = self.evaluate_from_perspective(
                    option, perspective, problem
                )
                analysis[perspective].evaluations[option] = score
        
        # Sintetizar: encontrar opción con mejor balance
        synthesis = self.synthesize_perspectives(analysis, options)
        
        return MultiPerspectiveResult(
            perspectives=analysis,
            synthesis=synthesis,
            recommended_option=synthesis.best_option,
            trade_offs=synthesis.trade_offs,
            dissenting_views=synthesis.dissenting_perspectives
        )
```

### 4. Hipótesis, deducción y razonamiento inductivo

```python
class HypothesisEngine:
    """Genera, prueba y refina hipótesis."""
    
    def generate_hypotheses(self, observations: list[str]) -> list[Hypothesis]:
        """Genera hipótesis que explican las observaciones."""
        hypotheses = []
        
        for combo in itertools.combinations(observations, min(3, len(observations))):
            h = self.infer_hypothesis(combo)
            h.supporting_evidence = list(combo)
            h.contradicting_evidence = [
                o for o in observations if self.contradicts(h, o)
            ]
            h.confidence = (
                len(h.supporting_evidence) / 
                (len(h.supporting_evidence) + len(h.contradicting_evidence) + 1)
            )
            hypotheses.append(h)
        
        return sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
    
    def test_hypothesis(
        self, hypothesis: Hypothesis, test: str, result: bool
    ) -> Hypothesis:
        """Actualiza hipótesis con resultado de test."""
        if result:
            hypothesis.supporting_evidence.append(test)
            hypothesis.confidence = min(hypothesis.confidence * 1.2, 0.99)
        else:
            hypothesis.contradicting_evidence.append(test)
            hypothesis.confidence *= 0.5
        
        return hypothesis


class LogicalDeduction:
    """Deducción lógica formal."""
    
    def deduce(self, premises: list[str]) -> list[Deduction]:
        """
        Aplica reglas lógicas para derivar conclusiones.
        
        Soporta:
        - Modus ponens: Si P→Q y P, entonces Q
        - Modus tollens: Si P→Q y ¬Q, entonces ¬P
        - Silogismo: Si P→Q y Q→R, entonces P→R
        - Eliminación disyuntiva: Si P∨Q y ¬P, entonces Q
        """
        conclusions = []
        
        # Extraer implicaciones
        implications = self.extract_implications(premises)
        facts = self.extract_facts(premises)
        
        # Modus Ponens
        for impl in implications:
            if impl.antecedent in facts:
                conclusions.append(Deduction(
                    rule="modus_ponens",
                    premises=[impl.raw, f"Hecho: {impl.antecedent}"],
                    conclusion=impl.consequent,
                    confidence=0.95
                ))
        
        # Modus Tollens
        for impl in implications:
            negated_consequent = f"no {impl.consequent}"
            if negated_consequent in facts or self.is_negation_of(facts, impl.consequent):
                conclusions.append(Deduction(
                    rule="modus_tollens",
                    premises=[impl.raw, f"Hecho: ¬{impl.consequent}"],
                    conclusion=f"¬{impl.antecedent}",
                    confidence=0.95
                ))
        
        # Silogismo transitivo
        for i1 in implications:
            for i2 in implications:
                if i1.consequent == i2.antecedent:
                    conclusions.append(Deduction(
                        rule="transitive_syllogism",
                        premises=[i1.raw, i2.raw],
                        conclusion=f"{i1.antecedent} → {i2.consequent}",
                        confidence=0.90
                    ))
        
        return conclusions


class InductiveReasoning:
    """Razonamiento inductivo: de observaciones específicas a reglas generales."""
    
    def induce(self, observations: list[Observation]) -> list[InducedRule]:
        """
        Busca patrones en observaciones para inducir reglas generales.
        """
        rules = []
        
        # Agrupar por categoría
        grouped = group_by(observations, key=lambda o: o.category)
        
        for category, obs_group in grouped.items():
            # Buscar propiedades comunes
            common_props = self.find_common_properties(obs_group)
            
            if common_props and len(obs_group) >= 3:
                rules.append(InducedRule(
                    category=category,
                    rule=f"Todos los {category} tienden a: {', '.join(common_props)}",
                    supporting_observations=len(obs_group),
                    confidence=min(0.5 + len(obs_group) * 0.05, 0.90),
                    exceptions=self.find_exceptions(obs_group, common_props)
                ))
        
        return rules
```

### 5. Actualización bayesiana

```python
class BayesianUpdater:
    """
    Actualización bayesiana de creencias con nueva evidencia.
    P(H|E) = P(E|H) * P(H) / P(E)
    """
    
    def __init__(self):
        self.beliefs: dict[str, float] = {}  # Prior probabilities
    
    def set_prior(self, hypothesis: str, probability: float):
        """Establece probabilidad prior para una hipótesis."""
        self.beliefs[hypothesis] = probability
    
    def update(
        self, 
        hypothesis: str, 
        evidence: str,
        likelihood: float,      # P(E|H) - prob de ver evidencia si H es cierta
        false_positive: float    # P(E|¬H) - prob de ver evidencia si H es falsa
    ) -> float:
        """
        Actualiza la creencia en una hipótesis dada nueva evidencia.
        
        Args:
            hypothesis: La hipótesis a actualizar
            evidence: Descripción de la evidencia observada
            likelihood: P(E|H)
            false_positive: P(E|¬H)
        
        Returns:
            P(H|E) - Probabilidad posterior
        """
        prior = self.beliefs.get(hypothesis, 0.5)
        
        # Bayes' theorem
        p_evidence = likelihood * prior + false_positive * (1 - prior)
        posterior = (likelihood * prior) / p_evidence
        
        self.beliefs[hypothesis] = posterior
        
        return posterior
    
    def compare_hypotheses(
        self,
        hypotheses: list[str],
        evidence_chain: list[Evidence]
    ) -> dict[str, float]:
        """
        Compara múltiples hipótesis actualizando con cadena de evidencias.
        """
        # Inicializar priors uniformes si no existen
        for h in hypotheses:
            if h not in self.beliefs:
                self.beliefs[h] = 1.0 / len(hypotheses)
        
        # Actualizar con cada pieza de evidencia
        for evidence in evidence_chain:
            for h in hypotheses:
                self.update(
                    h, 
                    evidence.description,
                    evidence.likelihoods[h],
                    evidence.false_positive_rate
                )
            
            # Renormalizar
            total = sum(self.beliefs[h] for h in hypotheses)
            for h in hypotheses:
                self.beliefs[h] /= total
        
        return {h: self.beliefs[h] for h in hypotheses}
```

```
# Ejemplo de actualización bayesiana:
Hipótesis: "El bug está en el backend" vs "El bug está en el frontend"

Prior: 50% / 50%

Evidencia 1: "El error solo aparece en Chrome"
  → P(E|backend) = 0.1  (poco probable si es backend)
  → P(E|frontend) = 0.7  (probable si es frontend)
  → Posterior: backend=15%, frontend=85%

Evidencia 2: "El API response es correcto en Postman"
  → P(E|backend) = 0.05
  → P(E|frontend) = 0.9
  → Posterior: backend=2%, frontend=98%

Conclusión: El bug está casi seguro en el frontend (98%)
```

### 6. Matrices de decisión y trade-off analysis

```python
class DecisionMatrix:
    """
    Matriz de decisión ponderada para comparar opciones.
    """
    
    def evaluate(
        self,
        options: list[str],
        criteria: list[Criterion],
        scores: dict[str, dict[str, float]]
    ) -> DecisionResult:
        """
        Args:
            options: Opciones a evaluar
            criteria: Lista de criterios con peso
            scores: scores[opción][criterio] = 0.0-1.0
        """
        weighted_scores = {}
        
        for option in options:
            total = 0
            breakdown = {}
            for criterion in criteria:
                raw_score = scores[option][criterion.name]
                weighted = raw_score * criterion.weight
                total += weighted
                breakdown[criterion.name] = {
                    "raw": raw_score,
                    "weighted": weighted,
                    "weight": criterion.weight
                }
            weighted_scores[option] = {
                "total": total,
                "breakdown": breakdown
            }
        
        ranked = sorted(
            weighted_scores.items(), 
            key=lambda x: x[1]["total"], 
            reverse=True
        )
        
        return DecisionResult(
            ranking=ranked,
            winner=ranked[0][0],
            margin=ranked[0][1]["total"] - ranked[1][1]["total"] if len(ranked) > 1 else 1.0,
            sensitivity=self.sensitivity_analysis(options, criteria, scores)
        )
```

```
# Ejemplo de Matriz de Decisión:
Opciones: React vs Vue vs Svelte
Criterios (peso): Performance(0.2), DX(0.3), Ecosistema(0.25), Hiring(0.25)

            | Perf(0.2) | DX(0.3)   | Eco(0.25) | Hiring(0.25) | TOTAL
React       | 0.7(0.14) | 0.7(0.21) | 0.95(0.24)| 0.95(0.24)   | 0.83
Vue         | 0.8(0.16) | 0.9(0.27) | 0.7(0.18) | 0.6(0.15)    | 0.76
Svelte      | 0.95(0.19)| 0.85(0.26)| 0.4(0.10) | 0.3(0.08)    | 0.62

Winner: React (margin: 0.07 sobre Vue)
Nota: Si peso de Hiring baja a 0.10, Vue gana.
```

### 7. Cuestionamiento socrático y primeros principios

```python
class SocraticQuestioning:
    """
    Método socrático para profundizar en el entendimiento.
    Cuestiona suposiciones y busca la verdad fundamental.
    """
    
    QUESTION_TYPES = {
        "clarification": [
            "¿Qué quieres decir exactamente con '{concept}'?",
            "¿Puedes dar un ejemplo concreto?",
            "¿Cómo definirías '{concept}' de forma precisa?"
        ],
        "assumptions": [
            "¿Qué estamos asumiendo aquí?",
            "¿Es esa suposición necesariamente cierta?",
            "¿Qué pasaría si '{assumption}' fuera falsa?"
        ],
        "evidence": [
            "¿Qué evidencia soporta esta afirmación?",
            "¿Hay datos que contradigan esto?",
            "¿Cómo podemos verificar '{claim}'?"
        ],
        "perspectives": [
            "¿Cómo vería esto alguien que discrepa?",
            "¿Hay otro enfoque válido?",
            "¿Qué diría un experto en {domain}?"
        ],
        "consequences": [
            "¿Cuáles son las implicaciones de esto?",
            "¿Qué sucede si estamos equivocados?",
            "¿Cuál es el peor escenario posible?"
        ],
        "meta": [
            "¿Por qué es importante esta pregunta?",
            "¿Estamos haciendo la pregunta correcta?",
            "¿Qué no estamos considerando?"
        ]
    }
    
    def question(self, statement: str, depth: int = 3) -> QuestioningResult:
        """Aplica cuestionamiento socrático a una afirmación."""
        dialogue = []
        current = statement
        
        for d in range(depth):
            # Identificar tipo de pregunta más útil
            q_type = self.select_question_type(current, dialogue)
            question = self.generate_question(current, q_type)
            answer = self.attempt_answer(question, current)
            
            dialogue.append(QuestionAnswer(
                depth=d,
                question=question,
                question_type=q_type,
                answer=answer,
                revealed_assumptions=self.extract_assumptions(answer)
            ))
            
            current = answer
        
        return QuestioningResult(
            original_statement=statement,
            dialogue=dialogue,
            uncovered_assumptions=[a for qa in dialogue for a in qa.revealed_assumptions],
            refined_statement=self.refine_statement(statement, dialogue)
        )


class FirstPrinciplesThinking:
    """
    Pensamiento desde primeros principios.
    Descompone hasta verdades fundamentales y reconstruye.
    """
    
    def decompose(self, problem: str) -> FirstPrinciplesAnalysis:
        """
        1. Identificar suposiciones
        2. Descomponer hasta verdades fundamentales
        3. Reconstruir solución desde cero
        """
        # Fase 1: Listar todas las suposiciones
        assumptions = self.identify_assumptions(problem)
        
        # Fase 2: Cuestionar cada suposición
        challenged = []
        for assumption in assumptions:
            is_fundamental = self.is_fundamental_truth(assumption)
            challenged.append(ChallengedAssumption(
                assumption=assumption,
                is_fundamental=is_fundamental,
                evidence=self.find_evidence(assumption),
                can_be_removed=not is_fundamental
            ))
        
        # Fase 3: Extraer solo las verdades fundamentales
        fundamentals = [c.assumption for c in challenged if c.is_fundamental]
        
        # Fase 4: Reconstruir solución desde los fundamentales
        reconstructed = self.rebuild_from_fundamentals(problem, fundamentals)
        
        return FirstPrinciplesAnalysis(
            original_problem=problem,
            assumptions_found=len(assumptions),
            assumptions_removed=len([c for c in challenged if c.can_be_removed]),
            fundamental_truths=fundamentals,
            reconstructed_solution=reconstructed,
            innovation_potential=self.assess_innovation(reconstructed, problem)
        )
```

```
# Ejemplo de First Principles:
Problema: "El CI/CD tarda 45 minutos"

Suposiciones encontradas:
  1. "Necesitamos correr TODOS los tests" → ¿Fundamental? NO
  2. "Docker build debe ser from scratch" → ¿Fundamental? NO
  3. "Los tests deben correr secuencialmente" → ¿Fundamental? NO
  4. "El código debe compilar correctamente" → ¿Fundamental? SÍ
  5. "Los tests críticos deben pasar" → ¿Fundamental? SÍ

Verdades fundamentales: [4, 5]

Reconstrucción desde primeros principios:
  1. Solo compilar lo que cambió (incremental build) → -15 min
  2. Solo correr tests afectados por cambios → -20 min
  3. Cache de Docker layers agresivo → -5 min
  4. Tests en paralelo → -3 min
  Resultado: 45 min → 7 min (-84%)
```

## Mejores prácticas

1. **Elegir el patrón correcto**: CoT para problemas secuenciales, ToT para exploración, Bayesian para incertidumbre
2. **Hacer explícito el razonamiento**: Cada paso debe ser verificable y cuestionable
3. **Cuestionar suposiciones**: Usar Socrático antes de aceptar cualquier premisa como verdad
4. **Cuantificar incertidumbre**: Asignar probabilidades, no decir "probablemente" sin número
5. **Considerar múltiples perspectivas**: No optimizar solo para un stakeholder
6. **Sensitivity analysis siempre**: Verificar si pequeños cambios en pesos cambian la conclusión
7. **Documentar el razonamiento**: El proceso es tan valioso como la conclusión
8. **Actualizar creencias con evidencia**: No mantener una posición cuando la evidencia la contradice
9. **Primeros principios para innovar**: Cuando las soluciones convencionales no funcionan, descomponer desde cero
10. **Combinar patrones**: Los problemas complejos se benefician de usar varios patrones en secuencia

## Ejemplos

### Ejemplo 1: Chain-of-Thought para debugging

```
Error: "TypeError: Cannot read property 'map' of undefined" en UserList.jsx

CoT:
  1. [ENTENDER] Error de runtime, 'map' se llama sobre undefined
  2. [LOCALIZAR] UserList.jsx, probablemente en el render donde se mapea una lista
  3. [CAUSA] El array de usuarios es undefined en algún momento
  4. [¿CUÁNDO?] Probablemente en el render inicial antes de que la API responda
  5. [SOLUCIÓN] Añadir valor default: `const users = data?.users || []`
  6. [VERIFICAR] ¿Hay más accesos a data sin comprobación? → Sí, líneas 28, 45
  Confianza: 0.92
```

### Ejemplo 2: Bayesian para diagnóstico

```
Síntoma: "La app va lenta solo por las mañanas"

Hipótesis:
  H1: Pico de tráfico matutino → Prior: 40%
  H2: Cron job pesado → Prior: 30%  
  H3: Backup de DB → Prior: 20%
  H4: Cold start → Prior: 10%

Evidencia: "CloudWatch muestra CPU al 95% de 8:00 a 8:15"
  → Update: H2 sube a 55%, H3 sube a 30%

Evidencia: "El cron de reportes corre a las 8:00"
  → Update: H2 sube a 82%

Conclusión: El cron de reportes (82%) es la causa más probable
```

### Ejemplo 3: Decision Matrix para elegir stack

```
→ DecisionMatrix.evaluate(
    options=["Next.js", "Remix", "Astro"],
    criteria=[
      Criterion("SSR Performance", 0.3),
      Criterion("Developer Experience", 0.25),
      Criterion("Edge Deployment", 0.2),
      Criterion("Learning Curve", 0.15),
      Criterion("Community", 0.1)
    ]
  )

Resultado:
  1. Next.js: 0.81 ← Recomendado
  2. Remix: 0.78 (margin: 0.03)
  3. Astro: 0.72

Nota: Margin pequeño (0.03). Sensitivity: si Edge sube a 0.3, Remix gana.
```

### Ejemplo 4: First Principles para optimización

```
Problema: "Nuestro bundle JS es de 2.5MB"

First Principles:
  Suposición removida: "Necesitamos todas las dependencias cargadas al inicio"
  Verdad fundamental: "El usuario necesita ver contenido interactivo rápido"
  
  Reconstrucción:
    1. Critical CSS inline (verdad: necesita estilos base) → -200KB
    2. Code splitting por ruta (no todo al inicio) → -800KB
    3. Dynamic imports para features opcionales → -500KB
    4. Reemplazar moment.js por date-fns (tree-shakeable) → -300KB
    
  Resultado: 2.5MB → 700KB (-72%)
```
