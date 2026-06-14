---
name: ga4-analytics
version: 1.0.0
description: Consultar y analizar datos de Google Analytics 4 mediante la Data API. Usa cuando necesites obtener métricas de tráfico, conversiones, comportamiento de usuarios o generar informes personalizados.
tags: [analytics, ga4, google-analytics, data, metrics, reporting, api]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# GA4 Analytics Skill

## Cuándo usar esta skill
- Obtener métricas de tráfico web (sesiones, usuarios, pageviews)
- Analizar conversiones y eventos
- Crear informes personalizados de GA4
- Comparar períodos (MoM, YoY)
- Exportar datos de GA4 para análisis externo

## Setup — Google Analytics Data API

### Credenciales necesarias
```bash
# 1. Crear Service Account en Google Cloud Console
# https://console.cloud.google.com/iam-admin/serviceaccounts
# 
# 2. Descargar JSON de credenciales
# 
# 3. Añadir el email del Service Account como "Viewer" en GA4
# GA4 Admin → Property Access Management → Add users
# 
# Variables de entorno necesarias:
GA4_PROPERTY_ID=123456789             # En GA4: Admin → Property Settings → Property ID
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

```

### Instalar dependencias
```bash
pip install google-analytics-data
# O
npm install @google-analytics/data
```

## Uso con Python

### Cliente básico
```python
from google.analyticsdata.v1beta import BetaAnalyticsDataClient
from google.analyticsdata.v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import os

client = BetaAnalyticsDataClient()
PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID")

def run_report(dimensions: list, metrics: list, date_range: tuple = ("30daysAgo", "today")):
    """
    Ejecutar un reporte de GA4
    
    Args:
        dimensions: Lista de dimensiones como strings ["date", "city", "pagePath"]
        metrics: Lista de métricas como strings ["sessions", "users", "screenPageViews"]
        date_range: Tuple (start_date, end_date) en formato "YYYY-MM-DD" o "NdaysAgo"
    """
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=date_range[0], end_date=date_range[1])],
    )
    
    response = client.run_report(request)
    
    # Convertir a lista de dicts
    results = []
    for row in response.rows:
        result = {}
        for i, dim in enumerate(dimensions):
            result[dim] = row.dimension_values[i].value
        for i, metric in enumerate(metrics):
            result[metric] = row.metric_values[i].value
        results.append(result)
    
    return results
```

### Reportes más usados

#### Tráfico general (últimos 30 días)
```python
traffic = run_report(
    dimensions=["date"],
    metrics=["sessions", "users", "newUsers", "screenPageViews", "bounceRate"],
    date_range=("30daysAgo", "today")
)
```

#### Top páginas por tráfico
```python
top_pages = run_report(
    dimensions=["pagePath", "pageTitle"],
    metrics=["screenPageViews", "averageSessionDuration", "bounceRate"],
    date_range=("30daysAgo", "today")
)
# Ordenar por pageviews
top_pages.sort(key=lambda x: int(x["screenPageViews"]), reverse=True)
```

#### Fuentes de tráfico (acquisition)
```python
sources = run_report(
    dimensions=["sessionSource", "sessionMedium"],
    metrics=["sessions", "users", "conversionRate"],
    date_range=("30daysAgo", "today")
)
```

#### Conversiones por evento
```python
conversions = run_report(
    dimensions=["eventName"],
    metrics=["eventCount", "totalUsers"],
    date_range=("30daysAgo", "today")
)
```

#### Rendimiento por dispositivo
```python
devices = run_report(
    dimensions=["deviceCategory"],
    metrics=["sessions", "users", "bounceRate", "averageSessionDuration"],
    date_range=("30daysAgo", "today")
)
```

#### Comparativa mes actual vs mes anterior
```python
current_month = run_report(["date"], ["sessions", "users"], ("30daysAgo", "today"))
previous_month = run_report(["date"], ["sessions", "users"], ("60daysAgo", "31daysAgo"))

current_total = sum(int(r["sessions"]) for r in current_month)
previous_total = sum(int(r["sessions"]) for r in previous_month)
change = ((current_total - previous_total) / previous_total) * 100
print(f"Sesiones: {current_total} vs {previous_total} ({change:+.1f}%)")
```

## Generar reporte en Markdown

```python
def generate_report(property_id: str = None) -> str:
    """Genera un reporte mensual completo en Markdown"""
    
    report_lines = ["# GA4 Report — Últimos 30 días\n"]
    
    # Métricas resumen
    summary = run_report(
        dimensions=["date"],
        metrics=["sessions", "users", "newUsers", "screenPageViews"],
        date_range=("30daysAgo", "today")
    )
    
    totals = {
        "sessions": sum(int(r["sessions"]) for r in summary),
        "users": sum(int(r["users"]) for r in summary),
        "new_users": sum(int(r["newUsers"]) for r in summary),
        "pageviews": sum(int(r["screenPageViews"]) for r in summary),
    }
    
    report_lines.append("## Resumen")
    report_lines.append(f"| Métrica | Valor |")
    report_lines.append(f"|---------|-------|")
    report_lines.append(f"| Sesiones | {totals['sessions']:,} |")
    report_lines.append(f"| Usuarios | {totals['users']:,} |")
    report_lines.append(f"| Nuevos usuarios | {totals['new_users']:,} |")
    report_lines.append(f"| Páginas vistas | {totals['pageviews']:,} |")
    
    # Top 10 páginas
    pages = run_report(["pagePath"], ["screenPageViews"], ("30daysAgo", "today"))
    pages.sort(key=lambda x: int(x["screenPageViews"]), reverse=True)
    
    report_lines.append("\n## Top 10 Páginas")
    report_lines.append("| Página | Vistas |")
    report_lines.append("|--------|--------|")
    for page in pages[:10]:
        report_lines.append(f"| {page['pagePath']} | {int(page['screenPageViews']):,} |")
    
    # Fuentes de tráfico
    sources = run_report(
        ["sessionSource", "sessionMedium"], 
        ["sessions"], 
        ("30daysAgo", "today")
    )
    sources.sort(key=lambda x: int(x["sessions"]), reverse=True)
    
    report_lines.append("\n## Fuentes de tráfico")
    report_lines.append("| Fuente | Medio | Sesiones |")
    report_lines.append("|--------|-------|----------|")
    for src in sources[:10]:
        report_lines.append(
            f"| {src['sessionSource']} | {src['sessionMedium']} | {int(src['sessions']):,} |"
        )
    
    return "\n".join(report_lines)

# Usar:
report = generate_report()
print(report)
# O guardar:
with open("ga4-report.md", "w") as f:
    f.write(report)
```

## Dimensiones y métricas clave

### Dimensiones más útiles
```
date                    — Fecha (YYYYMMDD)
pagePath                — Ruta de la página (/blog/post-1)
pageTitle               — Título de la página
sessionSource           — Fuente (google, newsletter, direct)
sessionMedium           — Medio (organic, email, cpc, referral)
sessionCampaignName     — Nombre de campaña UTM
deviceCategory          — desktop / mobile / tablet
country                 — País del usuario
city                    — Ciudad
eventName               — Nombre del evento (click, purchase, sign_up)
```

### Métricas más útiles
```
sessions                — Sesiones totales
users                   — Usuarios únicos
newUsers                — Usuarios nuevos
screenPageViews         — Páginas vistas
bounceRate              — Tasa de rebote (0-1)
averageSessionDuration  — Duración media de sesión (segundos)
conversions             — Conversiones
conversionRate          — Tasa de conversión (0-1)
totalRevenue            — Ingresos totales (si tienes e-commerce)
```

## Referencias
- [GA4 Data API Reference](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Available Dimensions & Metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts-create)
