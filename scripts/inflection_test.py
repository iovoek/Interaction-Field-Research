#!/usr/bin/env python3
"""
INFLECTION POINT TEST: Extended Stock Market Analysis
=====================================================
Tests whether mid-liquidity stocks show the best risk-adjusted opportunity
for informed participants, using a larger sample and longer time horizon.

The prediction from the Interaction Field Equation:
- Thin markets (low n): high uncertainty, high potential but high noise
- Inflection zone (near n_c): optimal information advantage -- price is 
  converging but not yet efficient, informed participants gain most here
- Saturated markets (high n): efficient pricing, no edge for anyone

We test this with 1-year returns across the liquidity spectrum.
"""
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import time

client = ApiClient()

# Broader stock universe spanning full liquidity range
tickers = [
    # Ultra-liquid mega-caps (50M+ avg daily volume)
    "AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "META", "GOOGL", "AMD", "INTC", "BAC",
    # Large-cap liquid (10-50M volume)
    "BA", "DIS", "NFLX", "PYPL", "UBER", "COIN", "SNAP", "F", "GM", "T",
    # Mid-cap moderate (2-10M volume)
    "CROX", "ETSY", "DKNG", "RBLX", "PLTR", "RIVN", "SOFI", "LCID", "NIO", "MARA",
    # Small-cap lower (500K-2M volume)
    "BMBL", "DBI", "PRPL", "BBWI", "CLOV", "WKHS", "SNDL", "OPEN", "SKLZ", "ASTS",
]

print("=" * 70)
print("INFLECTION POINT TEST: Extended Stock Market Analysis")
print("=" * 70)
print(f"\nTesting {len(tickers)} stocks with 1-year daily data")
print()

# Fetch 1-year data
stock_data = []
failed = []

for i, ticker in enumerate(tickers):
    if (i + 1) % 10 == 0:
        print(f"  Progress: {i+1}/{len(tickers)}")
    
    try:
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': ticker,
            'region': 'US',
            'interval': '1d',
            'range': '1y',
            'includeAdjustedClose': True,
        })
        
        if response and 'chart' in response and 'result' in response['chart']:
            result = response['chart']['result'][0]
            quotes = result['indicators']['quote'][0]
            
            closes = [x for x in quotes.get('close', []) if x is not None]
            volumes = [x for x in quotes.get('volume', []) if x is not None]
            highs = [x for x in quotes.get('high', []) if x is not None]
            lows = [x for x in quotes.get('low', []) if x is not None]
            
            if len(closes) >= 100 and len(volumes) >= 100:
                closes_arr = np.array(closes)
                volumes_arr = np.array(volumes)
                
                # Daily returns
                returns = np.diff(closes_arr) / closes_arr[:-1]
                
                # Metrics
                daily_vol = np.std(returns)
                annual_vol = daily_vol * np.sqrt(252)
                avg_volume = np.mean(volumes_arr)
                mean_daily_return = np.mean(returns)
                annual_return = mean_daily_return * 252
                sharpe = (annual_return - 0.05) / annual_vol if annual_vol > 0 else 0
                
                # Information ratio: how predictable are the returns?
                # Higher autocorrelation = more predictable = more exploitable
                if len(returns) > 10:
                    autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
                else:
                    autocorr = 0
                
                # Price efficiency: how quickly do prices revert?
                # Mean reversion coefficient (negative = mean reverting = efficient)
                if len(closes_arr) > 20:
                    price_changes = np.diff(closes_arr)
                    reversion = np.corrcoef(price_changes[:-1], price_changes[1:])[0, 1]
                else:
                    reversion = 0
                
                # Maximum drawdown
                peak = np.maximum.accumulate(closes_arr)
                drawdown = (closes_arr - peak) / peak
                max_drawdown = drawdown.min()
                
                # Calmar ratio (return / max drawdown)
                calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
                
                stock_data.append({
                    "ticker": ticker,
                    "avg_volume": float(avg_volume),
                    "annual_volatility": float(annual_vol),
                    "annual_return": float(annual_return),
                    "sharpe_ratio": float(sharpe),
                    "autocorrelation": float(autocorr),
                    "mean_reversion": float(reversion),
                    "max_drawdown": float(max_drawdown),
                    "calmar_ratio": float(calmar),
                    "n_days": len(closes_arr),
                })
        else:
            failed.append(ticker)
    except Exception as e:
        failed.append(ticker)
    
    time.sleep(0.3)

print(f"\nSuccessfully fetched: {len(stock_data)} stocks")
if failed:
    print(f"Failed: {failed}")

# Sort by volume
stock_data.sort(key=lambda x: x["avg_volume"])

# Divide into quintiles for finer granularity
n = len(stock_data)
q_size = n // 5

quintiles = []
for i in range(5):
    start = i * q_size
    end = (i + 1) * q_size if i < 4 else n
    quintile = stock_data[start:end]
    quintiles.append(quintile)

labels = ["Very Thin", "Thin", "Mid (Inflection)", "Liquid", "Very Liquid"]

print(f"\n{'Quintile':<18} {'Avg Vol':<14} {'Volatility':<12} {'Return':<10} {'Sharpe':<10} {'Autocorr':<10} {'Reversion':<10}")
print("-" * 90)

quintile_stats = []
for i, (label, q) in enumerate(zip(labels, quintiles)):
    avg_vol = np.mean([s["avg_volume"] for s in q])
    avg_volatility = np.mean([s["annual_volatility"] for s in q])
    avg_return = np.mean([s["annual_return"] for s in q])
    avg_sharpe = np.mean([s["sharpe_ratio"] for s in q])
    avg_autocorr = np.mean([s["autocorrelation"] for s in q])
    avg_reversion = np.mean([s["mean_reversion"] for s in q])
    
    quintile_stats.append({
        "label": label,
        "avg_volume": avg_vol,
        "avg_volatility": avg_volatility,
        "avg_return": avg_return,
        "avg_sharpe": avg_sharpe,
        "avg_autocorr": avg_autocorr,
        "avg_reversion": avg_reversion,
    })
    
    print(f"{label:<18} {avg_vol:>12,.0f} {avg_volatility:>10.1%} {avg_return:>8.1%} {avg_sharpe:>8.3f} {avg_autocorr:>8.4f} {avg_reversion:>8.4f}")

print()

# Key test: does the mid quintile have the best information advantage?
# Information advantage = |autocorrelation| (predictability)
print("=" * 70)
print("INFLECTION POINT ANALYSIS")
print("-" * 70)
print()

# Test: autocorrelation should be highest in the inflection zone
# (prices are moving but not yet efficient, so patterns are exploitable)
autocorrs = [abs(q["avg_autocorr"]) for q in quintile_stats]
max_autocorr_idx = np.argmax(autocorrs)
print(f"Highest absolute autocorrelation (most predictable): {labels[max_autocorr_idx]}")
print(f"  This is where informed participants have the most edge.")
print()

# Test: volatility should decrease monotonically
vols_by_q = [q["avg_volatility"] for q in quintile_stats]
is_monotonic = all(vols_by_q[i] >= vols_by_q[i+1] for i in range(len(vols_by_q)-1))
print(f"Volatility monotonically decreasing with liquidity: {is_monotonic}")
if not is_monotonic:
    print(f"  Pattern: {' -> '.join([f'{v:.1%}' for v in vols_by_q])}")
print()

# Test: Sharpe ratio pattern
sharpes_by_q = [q["avg_sharpe"] for q in quintile_stats]
max_sharpe_idx = np.argmax(sharpes_by_q)
print(f"Best risk-adjusted return (Sharpe): {labels[max_sharpe_idx]} ({sharpes_by_q[max_sharpe_idx]:.3f})")
print(f"  Pattern: {' | '.join([f'{s:.3f}' for s in sharpes_by_q])}")
print()

# Overall correlations
all_vols = np.array([s["avg_volume"] for s in stock_data])
all_volatilities = np.array([s["annual_volatility"] for s in stock_data])
all_sharpes = np.array([s["sharpe_ratio"] for s in stock_data])
all_autocorrs = np.array([abs(s["autocorrelation"]) for s in stock_data])

rho_vol_volatility, p_vol_volatility = spearmanr(all_vols, all_volatilities)
rho_vol_autocorr, p_vol_autocorr = spearmanr(all_vols, all_autocorrs)

print(f"Spearman (volume vs volatility): rho={rho_vol_volatility:.4f}, p={p_vol_volatility:.6f}")
print(f"Spearman (volume vs |autocorrelation|): rho={rho_vol_autocorr:.4f}, p={p_vol_autocorr:.6f}")
print()

# Generate visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Inflection Point Analysis: Stock Market Liquidity Quintiles (1-Year Data)", 
             fontsize=13, fontweight='bold')

# Plot 1: Volatility by quintile
ax1 = axes[0, 0]
colors = ['#e76f51', '#f4a261', '#2a9d8f', '#264653', '#1d3557']
bars1 = ax1.bar(labels, [q["avg_volatility"]*100 for q in quintile_stats], color=colors, alpha=0.8)
ax1.set_ylabel("Annualized Volatility (%)")
ax1.set_title("Price Uncertainty Decreases with Liquidity")
ax1.grid(True, alpha=0.3, axis='y')
ax1.tick_params(axis='x', rotation=15)

# Plot 2: Sharpe ratio by quintile
ax2 = axes[0, 1]
bars2 = ax2.bar(labels, sharpes_by_q, color=colors, alpha=0.8)
ax2.set_ylabel("Sharpe Ratio")
ax2.set_title("Risk-Adjusted Returns by Liquidity Stage")
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='x', rotation=15)

# Plot 3: Autocorrelation by quintile (predictability)
ax3 = axes[1, 0]
bars3 = ax3.bar(labels, autocorrs, color=colors, alpha=0.8)
ax3.set_ylabel("|Autocorrelation| (Predictability)")
ax3.set_title("Price Predictability by Liquidity Stage")
ax3.grid(True, alpha=0.3, axis='y')
ax3.tick_params(axis='x', rotation=15)

# Plot 4: Scatter of volume vs volatility with all stocks
ax4 = axes[1, 1]
log_vols = np.log10(all_vols)
ax4.scatter(log_vols, all_volatilities * 100, alpha=0.7, s=60, c='#2a9d8f', edgecolors='white')
for s in stock_data:
    ax4.annotate(s["ticker"], (np.log10(s["avg_volume"]), s["annual_volatility"]*100), 
                fontsize=6, alpha=0.6)
ax4.set_xlabel("Log10(Average Daily Volume)")
ax4.set_ylabel("Annualized Volatility (%)")
ax4.set_title(f"Volume vs Volatility (rho={rho_vol_volatility:.3f}, p={p_vol_volatility:.4f})")
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/home/ubuntu/inflection_test_results.png", dpi=150, bbox_inches='tight')
print("Chart saved to /home/ubuntu/inflection_test_results.png")

# Save results
results = {
    "dataset": {"n_stocks": len(stock_data), "period": "1 year", "source": "Yahoo Finance"},
    "quintile_analysis": quintile_stats,
    "correlations": {
        "volume_vs_volatility": {"rho": float(rho_vol_volatility), "p": float(p_vol_volatility)},
        "volume_vs_autocorrelation": {"rho": float(rho_vol_autocorr), "p": float(p_vol_autocorr)},
    },
    "key_findings": {
        "volatility_monotonic_decrease": is_monotonic,
        "most_predictable_quintile": labels[max_autocorr_idx],
        "best_sharpe_quintile": labels[max_sharpe_idx],
    },
    "stocks": stock_data,
}

with open("/home/ubuntu/inflection_test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Results saved to /home/ubuntu/inflection_test_results.json")
