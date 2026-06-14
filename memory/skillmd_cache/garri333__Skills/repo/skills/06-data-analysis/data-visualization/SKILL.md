---
name: data-visualization
version: 1.0.0
description: Crear visualizaciones de datos efectivas con Python (matplotlib, seaborn, plotly) y JavaScript (Chart.js, D3). Usa cuando necesites representar datos de forma visual, crear dashboards o gráficos para reportes.
tags: [data, visualization, charts, plotly, matplotlib, seaborn, chartjs, d3, analytics]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Data Visualization Skill

## Cuándo usar esta skill
- El usuario pide crear un gráfico o visualización con datos
- Pasar datos tabulares a formato visual
- Crear dashboards o reportes visuales
- Elegir el tipo de gráfico adecuado para los datos

## Seleccionar el tipo de gráfico

| Objetivo | Tipo de gráfico |
|----------|----------------|
| Distribución | Histograma, Box plot, Violin plot |
| Correlación | Scatter plot, Heatmap, Bubble chart |
| Comparación | Bar chart, Grouped bars, Radar chart |
| Evolución temporal | Line chart, Area chart |
| Composición | Pie chart, Donut, Stacked bars, TreeMap |
| Jerarquía | TreeMap, Sunburst |
| Geográfico | Choropleth map, Bubble map |
| Distribución 2D | Heatmap, Contour plot |

**Reglas básicas:**
- Evitar pie charts con más de 5 categorías — usar barras horizontales
- Line charts solo para datos continuos/temporales
- Barras horizontales cuando los labels son largos
- No usar 3D — distorsiona la percepción

## Python — Matplotlib / Seaborn

### Setup
```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np

# Estilo consistente
sns.set_theme(style="whitegrid", palette="husl", font_scale=1.1)
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'axes.titlepad': 15,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})
```

### Bar chart — comparativa por categoría
```python
def bar_chart(data: dict, title: str, xlabel: str, ylabel: str, output_path: str = None):
    """
    data: {"Categoría A": 100, "Categoría B": 80, ...}
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(
        data.keys(), 
        data.values(),
        color=sns.color_palette("husl", len(data)),
        edgecolor='white',
        linewidth=0.5
    )
    
    # Añadir valores encima de las barras
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height + max(data.values()) * 0.01,
            f'{height:,.0f}',
            ha='center', va='bottom', fontsize=10
        )
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
    else:
        plt.show()
    
    plt.close()
```

### Line chart — evolución temporal
```python
def time_series_chart(df: pd.DataFrame, date_col: str, value_cols: list, title: str):
    """
    df: DataFrame con columna de fecha y columnas de valores
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = sns.color_palette("husl", len(value_cols))
    
    for i, col in enumerate(value_cols):
        ax.plot(
            df[date_col], df[col],
            linewidth=2.5,
            color=colors[i],
            label=col,
            marker='o', markersize=4
        )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.show()
```

### Heatmap — correlaciones
```python
def correlation_heatmap(df: pd.DataFrame, title: str = "Matriz de correlación"):
    """Visualizar correlaciones entre variables numéricas"""
    corr = df.select_dtypes(include=np.number).corr()
    
    mask = np.triu(np.ones_like(corr, dtype=bool))  # Solo triángulo inferior
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True, fmt='.2f',
        cmap='RdYlGn',
        center=0,
        vmin=-1, vmax=1,
        ax=ax,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8}
    )
    
    ax.set_title(title, pad=15, fontsize=14)
    plt.tight_layout()
    plt.show()
```

## Python — Plotly (interactivo)

```python
import plotly.express as px
import plotly.graph_objects as go

# Line chart interactivo
def interactive_line_chart(df: pd.DataFrame, x: str, y: str, color: str = None, title: str = ""):
    fig = px.line(
        df, x=x, y=y, color=color,
        title=title,
        template='plotly_white',
        line_shape='spline',
        markers=True
    )
    
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        margin=dict(t=60)
    )
    
    fig.show()
    # O guardar como imagen:
    # fig.write_image("chart.png", scale=2)
    # O como HTML interactivo:
    # fig.write_html("chart.html")

# Dashboard multi-chart
def create_dashboard(data: dict) -> go.Figure:
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Tráfico', 'Conversiones', 'Por país', 'Dispositivos'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "choropleth"}, {"type": "pie"}]]
    )
    
    # Añadir cada trace al subplot correspondiente
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['traffic'], name='Sesiones'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=data['months'], y=data['conversions'], name='Conversiones'),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Dashboard de Analytics',
        height=800,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig
```

## JavaScript — Chart.js (para web)

```html
<canvas id="myChart"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Line chart con multiple series
const ctx = document.getElementById('myChart').getContext('2d');

const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Sesiones',
        data: [1200, 1900, 3000, 5000, 4200, 6000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Usuarios únicos',
        data: [900, 1400, 2300, 3800, 3200, 4600],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: 'Evolución del tráfico 2024'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => value.toLocaleString()
        }
      }
    }
  }
});
</script>
```

## Principios de buena visualización

```
1. Título claro y descriptivo — el lector debe entender sin contexto adicional
2. Etiquetas en todos los ejes con unidades
3. Leyenda cuando hay más de una serie
4. Annotation o nota si hay datos anómalos o importantes
5. Colores accesibles (no depender solo de color para distinguir)
6. Menos es más — eliminar gridlines, bordes y elementos decorativos innecesarios
7. Escala Y desde 0 para barras; no necesariamente para líneas
8. Ordenar barras por valor (de mayor a menor), no alfabéticamente
```

## Referencias
- [matplotlib gallery](https://matplotlib.org/stable/gallery/)
- [seaborn tutorials](https://seaborn.pydata.org/tutorial.html)
- [Plotly Python docs](https://plotly.com/python/)
- [Chart.js documentation](https://www.chartjs.org/docs/)
- [Storytelling with Data (libro)](https://www.storytellingwithdata.com/)
