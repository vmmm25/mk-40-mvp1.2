---
name: financial-analysis
version: 1.0.0
description: Análisis financiero de empresas y activos usando yfinance y pandas. Usa cuando necesites obtener datos bursátiles, calcular métricas financieras, analizar balances o comparar empresas.
tags: [finance, stocks, yfinance, analysis, investment, fundamentals, python]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Financial Analysis Skill

## Cuándo usar esta skill
- Obtener datos de precios históricos de acciones
- Analizar fundamentales de una empresa (P/E, P/B, etc.)
- Calcular métricas de rentabilidad y riesgo (Sharpe ratio, volatilidad)
- Comparar empresas del mismo sector
- Crear un análisis de cartera básico

## Setup

```bash
pip install yfinance pandas numpy matplotlib
```

## Obtener datos básicos de una acción

```python
import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_info(ticker: str) -> dict:
    """Información fundamental de una empresa"""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "price": info.get("currentPrice"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        # Valoración
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        # Crecimiento
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        # Rentabilidad
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "gross_margins": info.get("grossMargins"),
        "operating_margins": info.get("operatingMargins"),
        "profit_margins": info.get("profitMargins"),
        # Dividendo
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        # Deuda
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
    }


def get_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Obtener historial de precios
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist
```

## Análisis de rendimiento

```python
def performance_analysis(ticker: str, period: str = "1y") -> dict:
    """Métricas de rendimiento y riesgo"""
    hist = get_price_history(ticker, period=period)
    
    # Retornos diarios
    returns = hist['Close'].pct_change().dropna()
    
    # Métricas básicas
    total_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
    
    # Volatilidad anualizada (std diaria * sqrt(252))
    annual_volatility = returns.std() * np.sqrt(252) * 100
    
    # Sharpe Ratio (asumiendo risk-free rate del 4%)
    risk_free_rate = 0.04
    annual_return = returns.mean() * 252
    sharpe_ratio = (annual_return - risk_free_rate) / (returns.std() * np.sqrt(252))
    
    # Maximum Drawdown
    rolling_max = hist['Close'].expanding().max()
    drawdown = (hist['Close'] - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    # Beta vs S&P 500
    spy = yf.Ticker("SPY").history(period=period)['Close'].pct_change().dropna()
    # Alinear índices
    aligned = pd.concat([returns, spy], axis=1, join='inner')
    aligned.columns = ['stock', 'market']
    covariance = aligned.cov()
    beta = covariance.iloc[0, 1] / covariance.iloc[1, 1]
    
    return {
        "ticker": ticker,
        "period": period,
        "total_return_pct": round(total_return, 2),
        "annual_volatility_pct": round(annual_volatility, 2),
        "sharpe_ratio": round(sharpe_ratio, 3),
        "max_drawdown_pct": round(max_drawdown, 2),
        "beta": round(beta, 3),
        "avg_daily_return_pct": round(returns.mean() * 100, 4),
        "best_day_pct": round(returns.max() * 100, 2),
        "worst_day_pct": round(returns.min() * 100, 2),
    }
```

## Análisis comparativo de empresas

```python
def compare_companies(tickers: list[str]) -> pd.DataFrame:
    """Comparar métricas financieras de múltiples empresas"""
    
    metrics = []
    for ticker in tickers:
        try:
            info = get_stock_info(ticker)
            perf = performance_analysis(ticker)
            
            metrics.append({
                "Ticker": ticker,
                "Empresa": info["company"],
                "Sector": info["sector"],
                "Market Cap (B)": round(info["market_cap"] / 1e9, 1) if info["market_cap"] else None,
                "P/E": round(info["pe_ratio"], 1) if info["pe_ratio"] else None,
                "P/B": round(info["pb_ratio"], 2) if info["pb_ratio"] else None,
                "Margen neto %": round(info["profit_margins"] * 100, 1) if info["profit_margins"] else None,
                "ROE %": round(info["roe"] * 100, 1) if info["roe"] else None,
                "Crec. ingresos %": round(info["revenue_growth"] * 100, 1) if info["revenue_growth"] else None,
                "Deuda/Equity": round(info["debt_to_equity"], 2) if info["debt_to_equity"] else None,
                "Div. Yield %": round(info["dividend_yield"] * 100, 2) if info["dividend_yield"] else None,
                "Retorno 1Y %": perf["total_return_pct"],
                "Volatilidad %": perf["annual_volatility_pct"],
                "Sharpe": perf["sharpe_ratio"],
                "Beta": perf["beta"],
            })
        except Exception as e:
            print(f"Error con {ticker}: {e}")
    
    return pd.DataFrame(metrics).set_index("Ticker")


# Comparar empresas de big tech
comparison = compare_companies(["AAPL", "MSFT", "GOOGL", "META", "AMZN"])
print(comparison.to_string())
```

## Análisis de cartera

```python
def portfolio_analysis(holdings: dict, period: str = "1y") -> dict:
    """
    holdings: {"AAPL": 0.30, "MSFT": 0.25, "GOOGL": 0.20, "AMZN": 0.25}  # pesos
    """
    
    all_returns = {}
    for ticker in holdings:
        hist = get_price_history(ticker, period=period)
        all_returns[ticker] = hist['Close'].pct_change().dropna()
    
    returns_df = pd.DataFrame(all_returns).dropna()
    weights = np.array([holdings[t] for t in returns_df.columns])
    
    # Retorno de cartera
    portfolio_returns = returns_df @ weights
    
    # Métricas de cartera
    annual_return = portfolio_returns.mean() * 252 * 100
    annual_vol = portfolio_returns.std() * np.sqrt(252) * 100
    sharpe = (portfolio_returns.mean() * 252 - 0.04) / (portfolio_returns.std() * np.sqrt(252))
    
    # Matriz de correlaciones
    correlation_matrix = returns_df.corr().round(3)
    
    return {
        "total_return_pct": round((portfolio_returns + 1).prod() * 100 - 100, 2),
        "annual_return_pct": round(annual_return, 2),
        "annual_volatility_pct": round(annual_vol, 2),
        "sharpe_ratio": round(sharpe, 3),
        "correlations": correlation_matrix.to_dict(),
        "individual_weights": holdings,
    }
```

## Interpretar métricas financieras

```
P/E Ratio (Price-to-Earnings):
< 15    → Value stock (puede estar infravalorada o en declive)
15-25   → Fair value (typical)
25-40   → Growth premium (mercado espera crecimiento)
> 40    → Muy caro o high-growth (ej: tech en expansión)
N/A     → Sin beneficios (pérdidas)

P/B Ratio (Price-to-Book):
< 1     → Cotiza por debajo del valor contable (oportunidad o trampa)
1-3     → Razonable para muchos sectores
> 5     → Típico en empresas de tech/servicios (alto intangible)

ROE (Return on Equity):
< 10%   → Bajo
10-20%  → Bueno
> 20%   → Excelente

Margen neto:
< 5%    → Bajo (ej: retail, distribución)
5-15%   → Moderado
> 20%   → Alto (ej: software, pharma)

Beta:
< 1     → Menos volátil que el mercado (defensivo)
= 1     → Mueve como el mercado
> 1     → Más volátil (mayor riesgo/retorno potencial)

Deuda/Equity:
< 0.5   → Conservador
0.5-1.5 → Moderado
> 2     → Alto (puede ser un riesgo)

⚠️ Importante: Siempre comparar con el sector. Un P/E alto no es malo
si la empresa crece rápido. Un P/E bajo puede indicar problemas.
```

## Referencias
- [yfinance documentation](https://ranaroussi.github.io/yfinance/)
- [Investopedia — Financial Ratios](https://www.investopedia.com/financial-ratios-4689817)
- [Yahoo Finance](https://finance.yahoo.com/) — Fuente de los datos
- [EDGAR SEC Filings](https://www.sec.gov/cgi-bin/browse-edgar) — Datos oficiales US
