---
name: statistical-analysis
version: 1.0.0
description: Análisis estadístico de datos con Python: estadística descriptiva, pruebas de hipótesis, correlaciones y regresión. Usa cuando necesites analizar datos con rigor estadístico, validar hipótesis o encontrar relaciones entre variables.
tags: [statistics, data-analysis, python, scipy, pandas, hypothesis-testing, regression]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Statistical Analysis Skill

## Cuándo usar esta skill
- Analizar un dataset para extraer insights estadísticos
- Probar si una diferencia entre grupos es estadísticamente significativa
- Encontrar correlaciones entre variables
- Crear un modelo predictivo simple
- Validar si los datos siguen una distribución esperada

## Setup

```bash
pip install pandas numpy scipy statsmodels scikit-learn matplotlib seaborn
```

## Estadística descriptiva

```python
import pandas as pd
import numpy as np
from scipy import stats

def describe_dataset(df: pd.DataFrame) -> dict:
    """Análisis descriptivo completo de un dataset"""
    
    numerical = df.select_dtypes(include=np.number)
    categorical = df.select_dtypes(include=['object', 'category'])
    
    report = {
        "shape": df.shape,
        "missing_values": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "duplicates": df.duplicated().sum(),
    }
    
    if not numerical.empty:
        stats_df = numerical.describe()
        # Añadir métricas adicionales
        stats_df.loc['skewness'] = numerical.skew()
        stats_df.loc['kurtosis'] = numerical.kurtosis()
        report["numerical_stats"] = stats_df.to_dict()
    
    if not categorical.empty:
        report["categorical_info"] = {
            col: {
                "unique": df[col].nunique(),
                "top5": df[col].value_counts().head(5).to_dict()
            }
            for col in categorical.columns
        }
    
    return report
```

## Pruebas de hipótesis

### Diccionario de pruebas
```
Comparar medias:
  2 grupos independientes → t-test (paramétrico) o Mann-Whitney U (no param)
  2 grupos pareados      → paired t-test o Wilcoxon
  3+ grupos              → ANOVA (param) o Kruskal-Wallis (no param)

Comparar proporciones:
  2 grupos               → chi-squared test o z-test para proporciones
  Frecuencias observadas vs esperadas → chi-squared goodness of fit

Correlación:
  Variables continuas    → Pearson (param) o Spearman (no param)
  Variables ordinales    → Spearman o Kendall
```

### t-test — comparar dos grupos
```python
from scipy import stats

def compare_two_groups(group_a: list, group_b: list, alpha: float = 0.05) -> dict:
    """
    Comparar la media de dos grupos independientes
    H0: no hay diferencia entre los grupos
    H1: hay diferencia significativa
    """
    # Verificar normalidad (Shapiro-Wilk)
    _, p_norm_a = stats.shapiro(group_a) if len(group_a) <= 5000 else (None, 0)
    _, p_norm_b = stats.shapiro(group_b) if len(group_b) <= 5000 else (None, 0)
    
    is_normal = p_norm_a > 0.05 and p_norm_b > 0.05
    
    if is_normal:
        # Test de Levene para igualdad de varianzas
        _, p_equal_var = stats.levene(group_a, group_b)
        equal_var = p_equal_var > 0.05
        
        # Student's t-test (equal_var=True) o Welch's t-test (equal_var=False)
        stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=equal_var)
        test_name = "Student's t-test" if equal_var else "Welch's t-test"
    else:
        # Mann-Whitney U (no paramétrico)
        stat, p_value = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
        test_name = "Mann-Whitney U"
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.std(group_a)**2 + np.std(group_b)**2) / 2)
    cohens_d = (np.mean(group_a) - np.mean(group_b)) / pooled_std if pooled_std != 0 else 0
    
    effect_magnitude = (
        "negligible" if abs(cohens_d) < 0.2 else
        "small" if abs(cohens_d) < 0.5 else
        "medium" if abs(cohens_d) < 0.8 else
        "large"
    )
    
    return {
        "test": test_name,
        "statistic": round(stat, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "conclusion": (
            f"Hay una diferencia estadísticamente significativa (p={p_value:.4f} < α={alpha})"
            if p_value < alpha else
            f"No hay evidencia de diferencia significativa (p={p_value:.4f} > α={alpha})"
        ),
        "effect_size": {"cohens_d": round(cohens_d, 3), "magnitude": effect_magnitude},
        "descriptives": {
            "group_a": {"mean": round(np.mean(group_a), 2), "std": round(np.std(group_a), 2), "n": len(group_a)},
            "group_b": {"mean": round(np.mean(group_b), 2), "std": round(np.std(group_b), 2), "n": len(group_b)},
        }
    }
```

### Chi-squared — variables categóricas
```python
def chi_squared_test(observed: list, expected: list = None) -> dict:
    """
    Test chi-squared para variables categóricas
    Si no se dan expected, asume distribución uniforme
    """
    observed = np.array(observed)
    
    if expected is None:
        expected = np.full_like(observed, observed.sum() / len(observed), dtype=float)
    
    stat, p_value = stats.chisquare(observed, f_exp=expected)
    
    return {
        "chi2": round(stat, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
        "df": len(observed) - 1
    }
```

## Correlaciones

```python
def correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Matriz de correlaciones con significancia estadística
    """
    numerical = df.select_dtypes(include=np.number)
    cols = numerical.columns
    n = len(cols)
    
    result = pd.DataFrame(index=cols, columns=cols, dtype=float)
    p_values = pd.DataFrame(index=cols, columns=cols, dtype=float)
    
    for i, col_i in enumerate(cols):
        for j, col_j in enumerate(cols):
            if i == j:
                result.loc[col_i, col_j] = 1.0
                p_values.loc[col_i, col_j] = 0.0
            else:
                # Eliminar filas con NaN en cualquiera de las dos columnas
                mask = numerical[[col_i, col_j]].notna().all(axis=1)
                x = numerical.loc[mask, col_i]
                y = numerical.loc[mask, col_j]
                
                r, p = stats.pearsonr(x, y)
                result.loc[col_i, col_j] = round(r, 3)
                p_values.loc[col_i, col_j] = round(p, 4)
    
    return result, p_values
```

## Regresión lineal

```python
import statsmodels.api as sm

def linear_regression(df: pd.DataFrame, target: str, features: list) -> dict:
    """
    Regresión lineal con statsmodels (incluye p-values, R², etc.)
    """
    X = df[features].copy()
    y = df[target]
    
    # Eliminar filas con NaN
    mask = pd.concat([X, y], axis=1).notna().all(axis=1)
    X, y = X[mask], y[mask]
    
    # Añadir constante (intercepto)
    X_const = sm.add_constant(X)
    
    # Ajustar modelo
    model = sm.OLS(y, X_const).fit()
    
    return {
        "r_squared": round(model.rsquared, 4),
        "adj_r_squared": round(model.rsquared_adj, 4),
        "f_statistic": round(model.fvalue, 4),
        "f_p_value": round(model.f_pvalue, 6),
        "aic": round(model.aic, 2),
        "observations": int(model.nobs),
        "coefficients": {
            var: {
                "coef": round(coef, 4),
                "std_err": round(se, 4),
                "p_value": round(p, 6),
                "significant": p < 0.05,
                "conf_int_95": [round(model.conf_int().loc[var, 0], 4), 
                                round(model.conf_int().loc[var, 1], 4)]
            }
            for var, coef, se, p in zip(
                model.params.index,
                model.params,
                model.bse,
                model.pvalues
            )
        },
        "summary": str(model.summary())
    }
```

## Interpretación de resultados

### Guía para comunicar estadística

```
p-value:
≤ 0.001  → Evidencia muy fuerte contra H0
≤ 0.01   → Evidencia fuerte
≤ 0.05   → Evidencia moderada (significativo)
> 0.05   → Evidencia insuficiente (no significativo)

⚠️ Errores comunes al interpretar:
- "p < 0.05 significa que hay un efecto importante" → FALSO. Solo dice que hay evidencia de efecto.
  El tamaño del efecto (Cohen's d, r, R²) dice si es importante práticamente.
- "p > 0.05 prueba que no hay efecto" → FALSO. Solo que no hay evidencia suficiente.
- "p-value = probabilidad de que sea verdad" → FALSO. Es P(datos | H0=verdad).

Cohen's d (tamaño efecto):
< 0.2   → Negligible
0.2-0.5 → Pequeño  
0.5-0.8 → Mediano
> 0.8   → Grande

R² en regresión:
Explica qué % de la varianza de Y es explicada por X.
No hay valor universal "bueno" — depende del dominio.
En ciencias sociales, 0.30 puede ser excelente.
En ingeniería, 0.95+ puede ser lo esperado.
```

## Referencias
- [scipy.stats documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [statsmodels documentation](https://www.statsmodels.org/stable/index.html)
- [Statistics with Python (book)](https://www.oreilly.com/library/view/statistics-in-python/9781491975688/)
- [Common Statistical Tests](https://www.statstest.com/)
