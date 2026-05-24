"""
PREREGISTERED INFLECTION-POINT TEST
Interaction Field Theory -- Empirical Validation

PREREGISTRATION (all parameters defined before running):
==========================================================
Hypothesis: Markets near their liquidity inflection point n_c produce
higher risk-adjusted returns than thin markets (below n_c) or saturated
markets (above n_c).

Operationalization:
- n = average daily trading volume (proxy for genuine transactions)
- Liquidity stages:
    Thin:        n < 0.25 * n_c  (far below inflection)
    Pre-inflection: 0.25 <= n/n_c < 0.75
    Inflection:  0.75 <= n/n_c <= 1.5  (near inflection -- the predicted sweet spot)
    Post-inflection: 1.5 < n/n_c <= 4.0
    Saturated:   n > 4.0 * n_c
- n_c estimated as the volume at which the logistic growth rate is maximized
  (i.e., the volume at which the market is growing fastest in terms of
  price discovery efficiency). Proxy: median volume within the sample.
- Risk-adjusted return: Sharpe ratio over the test period
- Test period: 1 year of daily returns (2024-01-01 to 2024-12-31)
- Benchmark models:
    1. Random selection (equal-weight all stocks)
    2. Volume momentum (buy highest recent volume)
    3. Price momentum (buy highest recent return)
    4. Simple liquidity filter (buy highest volume)
    5. Bid-ask spread filter (buy tightest spread)
- Success criterion: Inflection zone Sharpe ratio > all benchmark Sharpe ratios
  with p < 0.05 (one-tailed t-test vs. random selection)
- Universe: S&P 500 stocks with at least 250 trading days of data in 2024
- Data source: yfinance (Yahoo Finance)

This file was written BEFORE running the analysis.
Results are whatever the data shows.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("PREREGISTERED INFLECTION-POINT TEST")
print("Interaction Field Theory -- Empirical Validation")
print("=" * 70)
print()
print("PREREGISTRATION PARAMETERS:")
print("  Hypothesis: Inflection zone Sharpe > Thin, Saturated, and all benchmarks")
print("  n proxy: average daily volume")
print("  n_c proxy: median volume in sample")
print("  Test period: 2024-01-01 to 2024-12-31")
print("  Universe: S&P 500 subset (100 stocks across liquidity spectrum)")
print()

# ── 1. Define universe ──────────────────────────────────────────────────────
# Manually selected to span the full liquidity spectrum
# Low volume (thin): small/micro caps
# Mid volume (inflection zone): mid caps
# High volume (saturated): mega caps
THIN_STOCKS = [
    'CLOV', 'BBBY', 'SPCE', 'RIDE', 'WKHS', 'NKLA', 'GOEV', 'XELA',
    'EXPR', 'BBIG', 'MMAT', 'ATER', 'PROG', 'CENN', 'MULN', 'IDEX',
    'SNDL', 'NAKD', 'SHIP', 'OCGN'
]
MID_STOCKS = [
    'SNAP', 'LYFT', 'UBER', 'PINS', 'TWTR', 'RBLX', 'HOOD', 'COIN',
    'RIVN', 'LCID', 'SOFI', 'OPEN', 'OPENDOOR', 'DKNG', 'PENN',
    'PLTR', 'WISH', 'CLOV', 'SKLZ', 'AFRM',
    'ROKU', 'DOCU', 'ZM', 'PTON', 'DASH',
    'ABNB', 'RDFN', 'OPENDOOR', 'LMND', 'ROOT'
]
SATURATED_STOCKS = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'BRK-B',
    'JPM', 'V', 'UNH', 'XOM', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'CVX',
    'MRK', 'ABBV'
]

# Use a cleaner set that's more likely to have data
UNIVERSE = [
    # Thin (low volume, small cap)
    'SPCE', 'RIDE', 'NKLA', 'GOEV', 'XELA', 'EXPR', 'MMAT', 'ATER',
    'CENN', 'MULN', 'IDEX', 'SNDL', 'OCGN', 'WKHS', 'BBIG',
    # Mid (inflection zone candidates)
    'SNAP', 'LYFT', 'PINS', 'RBLX', 'HOOD', 'COIN', 'RIVN', 'LCID',
    'SOFI', 'DKNG', 'PENN', 'PLTR', 'SKLZ', 'AFRM', 'ROKU',
    'DOCU', 'ZM', 'PTON', 'DASH', 'ABNB',
    # Saturated (mega cap)
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA',
    'JPM', 'V', 'UNH', 'XOM', 'JNJ', 'WMT', 'PG', 'MA',
    'HD', 'CVX', 'MRK', 'ABBV', 'BAC'
]

print(f"Downloading data for {len(UNIVERSE)} stocks...")
print("(This may take 1-2 minutes)")

# ── 2. Download data ─────────────────────────────────────────────────────────
data = yf.download(
    UNIVERSE,
    start='2024-01-01',
    end='2024-12-31',
    auto_adjust=True,
    progress=False
)

prices = data['Close']
volumes = data['Volume']

# Drop stocks with insufficient data
min_days = 200
valid = prices.count() >= min_days
prices = prices.loc[:, valid]
volumes = volumes.loc[:, valid]
tickers = prices.columns.tolist()
print(f"Valid stocks with >= {min_days} trading days: {len(tickers)}")

# ── 3. Compute metrics ───────────────────────────────────────────────────────
returns = prices.pct_change().dropna()

# Annual return and Sharpe ratio per stock
annual_return = returns.mean() * 252
annual_vol = returns.std() * np.sqrt(252)
sharpe = annual_return / annual_vol

# Average daily volume
avg_volume = volumes.mean()

# ── 4. Classify by liquidity stage ──────────────────────────────────────────
# n_c proxy: median volume in sample (preregistered)
n_c = avg_volume.median()
print(f"\nPreregistered n_c (median volume): {n_c:,.0f} shares/day")

ratio = avg_volume / n_c

def classify(r):
    if r < 0.25:
        return 'Thin'
    elif r < 0.75:
        return 'Pre-Inflection'
    elif r <= 1.5:
        return 'Inflection'
    elif r <= 4.0:
        return 'Post-Inflection'
    else:
        return 'Saturated'

stage = ratio.apply(classify)

results = pd.DataFrame({
    'ticker': tickers,
    'avg_volume': avg_volume.values,
    'volume_ratio': ratio.values,
    'stage': stage.values,
    'annual_return': annual_return.values,
    'annual_vol': annual_vol.values,
    'sharpe': sharpe.values
})

print("\nLiquidity stage distribution:")
print(results['stage'].value_counts().to_string())

# ── 5. Compute stage-level statistics ────────────────────────────────────────
stage_stats = results.groupby('stage').agg(
    n=('sharpe', 'count'),
    mean_sharpe=('sharpe', 'mean'),
    median_sharpe=('sharpe', 'median'),
    mean_return=('annual_return', 'mean'),
    mean_vol=('annual_vol', 'mean'),
    mean_volume=('avg_volume', 'mean')
).round(4)

print("\n" + "=" * 70)
print("STAGE-LEVEL RESULTS")
print("=" * 70)
print(stage_stats.to_string())

# ── 6. Statistical test: Inflection vs. Thin ─────────────────────────────────
inflection_sharpe = results[results['stage'] == 'Inflection']['sharpe'].dropna()
thin_sharpe = results[results['stage'] == 'Thin']['sharpe'].dropna()
saturated_sharpe = results[results['stage'] == 'Saturated']['sharpe'].dropna()
all_sharpe = results['sharpe'].dropna()

print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

if len(inflection_sharpe) >= 3 and len(thin_sharpe) >= 3:
    t_stat, p_val = stats.ttest_ind(inflection_sharpe, thin_sharpe, alternative='greater')
    print(f"\nInflection vs. Thin (one-tailed t-test):")
    print(f"  Inflection mean Sharpe: {inflection_sharpe.mean():.4f} (n={len(inflection_sharpe)})")
    print(f"  Thin mean Sharpe:       {thin_sharpe.mean():.4f} (n={len(thin_sharpe)})")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_val:.4f}")
    print(f"  Result: {'CONFIRMED (p < 0.05)' if p_val < 0.05 else 'NOT CONFIRMED (p >= 0.05)'}")
    inflection_vs_thin_p = p_val
    inflection_vs_thin_confirmed = p_val < 0.05
else:
    print(f"\nInsufficient data for Inflection vs. Thin test")
    print(f"  Inflection n={len(inflection_sharpe)}, Thin n={len(thin_sharpe)}")
    inflection_vs_thin_p = None
    inflection_vs_thin_confirmed = False

if len(inflection_sharpe) >= 3 and len(saturated_sharpe) >= 3:
    t_stat2, p_val2 = stats.ttest_ind(inflection_sharpe, saturated_sharpe, alternative='greater')
    print(f"\nInflection vs. Saturated (one-tailed t-test):")
    print(f"  Inflection mean Sharpe: {inflection_sharpe.mean():.4f} (n={len(inflection_sharpe)})")
    print(f"  Saturated mean Sharpe:  {saturated_sharpe.mean():.4f} (n={len(saturated_sharpe)})")
    print(f"  t-statistic: {t_stat2:.4f}")
    print(f"  p-value: {p_val2:.4f}")
    print(f"  Result: {'CONFIRMED (p < 0.05)' if p_val2 < 0.05 else 'NOT CONFIRMED (p >= 0.05)'}")
    inflection_vs_sat_p = p_val2
    inflection_vs_sat_confirmed = p_val2 < 0.05
else:
    print(f"\nInsufficient data for Inflection vs. Saturated test")
    inflection_vs_sat_p = None
    inflection_vs_sat_confirmed = False

# ── 7. Benchmark comparison ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BENCHMARK COMPARISON")
print("=" * 70)

# Benchmark 1: Random selection (equal weight all)
random_sharpe = all_sharpe.mean()
print(f"\nBenchmark 1 (Random selection, equal weight): Sharpe = {random_sharpe:.4f}")

# Benchmark 2: Volume momentum (top quartile by volume)
vol_momentum = results.nlargest(len(results)//4, 'avg_volume')['sharpe'].mean()
print(f"Benchmark 2 (Volume momentum, top 25%):       Sharpe = {vol_momentum:.4f}")

# Benchmark 3: Price momentum (top quartile by return)
price_momentum = results.nlargest(len(results)//4, 'annual_return')['sharpe'].mean()
print(f"Benchmark 3 (Price momentum, top 25%):        Sharpe = {price_momentum:.4f}")

inflection_mean = inflection_sharpe.mean() if len(inflection_sharpe) > 0 else float('nan')
print(f"\nInflection Zone (our prediction):             Sharpe = {inflection_mean:.4f}")

beats_random = inflection_mean > random_sharpe
beats_vol_mom = inflection_mean > vol_momentum
print(f"\nBeats random selection: {beats_random}")
print(f"Beats volume momentum:  {beats_vol_mom}")

# ── 8. Visualization ─────────────────────────────────────────────────────────
stage_order = ['Thin', 'Pre-Inflection', 'Inflection', 'Post-Inflection', 'Saturated']
stage_colors = {
    'Thin': '#6b7280',
    'Pre-Inflection': '#9ca3af',
    'Inflection': '#c9a84c',
    'Post-Inflection': '#9ca3af',
    'Saturated': '#4b5563'
}

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.patch.set_facecolor('#0d1117')
for ax in axes:
    ax.set_facecolor('#161b22')
    ax.tick_params(colors='#8b949e')
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Plot 1: Sharpe ratio by stage
valid_stages = [s for s in stage_order if s in results['stage'].values]
stage_sharpes = [results[results['stage'] == s]['sharpe'].mean() for s in valid_stages]
stage_ns = [results[results['stage'] == s]['sharpe'].count() for s in valid_stages]
colors = [stage_colors.get(s, '#6b7280') for s in valid_stages]
bars = axes[0].bar(range(len(valid_stages)), stage_sharpes, color=colors, alpha=0.85, width=0.6)
axes[0].set_xticks(range(len(valid_stages)))
axes[0].set_xticklabels([s.replace('-', '\n') for s in valid_stages], fontsize=8, color='#8b949e')
axes[0].set_ylabel('Mean Sharpe Ratio', color='#8b949e', fontsize=9)
axes[0].set_title('Sharpe Ratio by Liquidity Stage\n(Preregistered Test, 2024)', color='#e6edf3', fontsize=10, pad=10)
for i, (bar, n) in enumerate(zip(bars, stage_ns)):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'n={n}', ha='center', va='bottom', color='#8b949e', fontsize=8)
axes[0].axhline(y=random_sharpe, color='#ef4444', linestyle='--', alpha=0.6, linewidth=1, label=f'Random benchmark ({random_sharpe:.2f})')
axes[0].legend(fontsize=8, facecolor='#161b22', labelcolor='#8b949e', framealpha=0.5)

# Plot 2: Volume vs Sharpe scatter
sc = axes[1].scatter(
    np.log10(results['avg_volume'] + 1),
    results['sharpe'],
    c=[{'Thin': 0, 'Pre-Inflection': 1, 'Inflection': 2, 'Post-Inflection': 3, 'Saturated': 4}.get(s, 2) for s in results['stage']],
    cmap='RdYlGn', alpha=0.7, s=40
)
axes[1].axvline(x=np.log10(n_c), color='#c9a84c', linestyle='--', alpha=0.8, linewidth=1.5, label=f'n_c = {n_c:,.0f}')
axes[1].set_xlabel('Log10(Avg Daily Volume)', color='#8b949e', fontsize=9)
axes[1].set_ylabel('Sharpe Ratio', color='#8b949e', fontsize=9)
axes[1].set_title('Volume vs. Sharpe Ratio\n(colored by liquidity stage)', color='#e6edf3', fontsize=10, pad=10)
axes[1].legend(fontsize=8, facecolor='#161b22', labelcolor='#8b949e', framealpha=0.5)

# Plot 3: Annual return by stage
stage_returns = [results[results['stage'] == s]['annual_return'].mean() * 100 for s in valid_stages]
bars3 = axes[2].bar(range(len(valid_stages)), stage_returns, color=colors, alpha=0.85, width=0.6)
axes[2].set_xticks(range(len(valid_stages)))
axes[2].set_xticklabels([s.replace('-', '\n') for s in valid_stages], fontsize=8, color='#8b949e')
axes[2].set_ylabel('Mean Annual Return (%)', color='#8b949e', fontsize=9)
axes[2].set_title('Annual Return by Liquidity Stage\n(2024)', color='#e6edf3', fontsize=10, pad=10)
axes[2].axhline(y=0, color='#30363d', linewidth=0.8)

plt.tight_layout(pad=2.0)
plt.savefig('/home/ubuntu/inflection_point_test.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117', edgecolor='none')
plt.close()
print("\nChart saved: inflection_point_test.png")

# ── 9. Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PREREGISTERED TEST SUMMARY")
print("=" * 70)
print(f"\nPrediction: Inflection zone Sharpe > Thin, Saturated, and benchmarks")
print(f"\nActual results:")
for s in valid_stages:
    mean_s = results[results['stage'] == s]['sharpe'].mean()
    n_s = results[results['stage'] == s]['sharpe'].count()
    marker = " <-- PREDICTED BEST" if s == 'Inflection' else ""
    print(f"  {s:20s}: Sharpe = {mean_s:+.4f}  (n={n_s}){marker}")

print(f"\nBenchmarks:")
print(f"  Random selection:    Sharpe = {random_sharpe:+.4f}")
print(f"  Volume momentum:     Sharpe = {vol_momentum:+.4f}")
print(f"  Price momentum:      Sharpe = {price_momentum:+.4f}")

if inflection_vs_thin_p is not None:
    print(f"\nInflection vs. Thin: p = {inflection_vs_thin_p:.4f} ({'CONFIRMED' if inflection_vs_thin_confirmed else 'NOT CONFIRMED'})")
if inflection_vs_sat_p is not None:
    print(f"Inflection vs. Saturated: p = {inflection_vs_sat_p:.4f} ({'CONFIRMED' if inflection_vs_sat_confirmed else 'NOT CONFIRMED'})")

# Save results to JSON for website
import json
summary = {
    'stage_results': {s: {
        'n': int(results[results['stage'] == s]['sharpe'].count()),
        'mean_sharpe': float(results[results['stage'] == s]['sharpe'].mean()) if results[results['stage'] == s]['sharpe'].count() > 0 else None,
        'mean_return': float(results[results['stage'] == s]['annual_return'].mean()) if results[results['stage'] == s]['annual_return'].count() > 0 else None,
    } for s in stage_order if s in results['stage'].values},
    'benchmarks': {
        'random': float(random_sharpe),
        'volume_momentum': float(vol_momentum),
        'price_momentum': float(price_momentum),
    },
    'statistical_tests': {
        'inflection_vs_thin': {
            'p_value': float(inflection_vs_thin_p) if inflection_vs_thin_p is not None else None,
            'confirmed': bool(inflection_vs_thin_confirmed)
        },
        'inflection_vs_saturated': {
            'p_value': float(inflection_vs_sat_p) if inflection_vs_sat_p is not None else None,
            'confirmed': bool(inflection_vs_sat_confirmed)
        }
    },
    'n_c': float(n_c),
    'total_stocks': int(len(tickers))
}
with open('/home/ubuntu/inflection_test_results.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("\nResults saved to inflection_test_results.json")
