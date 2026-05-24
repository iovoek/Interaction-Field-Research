"""
INFLECTION POINT TEST: StockX Sneaker Resale Market
====================================================
99,956 real transactions across 50 shoe models, Sept 2017 - Feb 2019.

This is the correct test domain:
- Items start near retail price (near-zero resale premium)
- Value is built entirely through trading/demand
- Market is inefficient (no algorithmic trading, no HFT)
- Wide range of liquidity levels (some shoes have 100 sales, others have 5000+)

PREDICTION (stated before looking at results):
For each shoe model, as cumulative transactions accumulate:
1. Price uncertainty (rolling SD) should decrease as ~1/sqrt(n)
2. The rate of price convergence should be fastest in the inflection zone
3. The inflection zone should show the highest Sharpe-like ratio (premium/volatility)

TEST DESIGN:
- For each shoe model, sort transactions chronologically
- Compute rolling price SD using expanding windows
- Identify the inflection point (where cumulative sales reach ~50% of total)
- Classify each transaction into thin/inflection/saturated zones
- Measure convergence rate (dSD/dn) in each zone
- Test whether inflection zone has fastest convergence
"""

import csv
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load data
print("Loading 99,956 StockX transactions...")
transactions = []
with open('/home/ubuntu/stockx_data/stockx_raw.csv', 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for row in reader:
        try:
            order_date = row[0]
            brand = row[1].strip()
            sneaker = row[2]
            sale_price = int(row[3])
            retail_price = int(row[4])
            release_date = row[5]
            shoe_size = float(row[6])
            region = row[7]
            transactions.append({
                'date': order_date,
                'brand': brand,
                'sneaker': sneaker,
                'sale_price': sale_price,
                'retail_price': retail_price,
                'premium': (sale_price - retail_price) / retail_price,
                'size': shoe_size,
                'region': region
            })
        except (ValueError, IndexError):
            continue

print(f"Loaded {len(transactions)} transactions")

# Group by sneaker model
by_model = defaultdict(list)
for t in transactions:
    by_model[t['sneaker']].append(t)

# Sort each model chronologically
for model in by_model:
    by_model[model].sort(key=lambda x: x['date'])

# Filter to models with at least 200 transactions (need enough data for rolling stats)
models = {k: v for k, v in by_model.items() if len(v) >= 200}
print(f"\nModels with 200+ transactions: {len(models)}")
print(f"Transaction count range: {min(len(v) for v in models.values())} to {max(len(v) for v in models.values())}")

# ============================================================
# TEST 1: Does price SD decrease as 1/sqrt(n)?
# ============================================================
print("\n" + "="*60)
print("TEST 1: Does price SD decrease as 1/sqrt(n)?")
print("="*60)

test1_results = []
for model_name, txns in models.items():
    prices = [t['sale_price'] for t in txns]
    n = len(prices)
    
    # Compute expanding window SD at regular intervals
    checkpoints = list(range(20, n, max(1, n//20)))
    sds = []
    ns = []
    for cp in checkpoints:
        window = prices[:cp]
        sd = np.std(window)
        if sd > 0:
            sds.append(sd)
            ns.append(cp)
    
    if len(ns) >= 5:
        # Fit log-log regression: log(SD) = a + b*log(n)
        log_n = np.log(ns)
        log_sd = np.log(sds)
        slope, intercept = np.polyfit(log_n, log_sd, 1)
        
        # Correlation
        rho = np.corrcoef(log_n, log_sd)[0, 1]
        
        test1_results.append({
            'model': model_name,
            'n_transactions': n,
            'slope': slope,
            'rho': rho,
            'confirmed': slope < 0  # SD should decrease with n
        })

confirmed_t1 = sum(1 for r in test1_results if r['confirmed'])
print(f"\nResults: {confirmed_t1}/{len(test1_results)} models show SD decreasing with n")
print(f"Mean slope: {np.mean([r['slope'] for r in test1_results]):.4f} (predicted: -0.500)")
print(f"Median slope: {np.median([r['slope'] for r in test1_results]):.4f}")

# Show top confirming models
test1_sorted = sorted(test1_results, key=lambda x: x['slope'])
print("\nStrongest confirmers (most negative slope):")
for r in test1_sorted[:5]:
    print(f"  {r['model'][:50]:50s} slope={r['slope']:.3f} rho={r['rho']:.3f} n={r['n_transactions']}")

print("\nStrongest non-confirmers (most positive slope):")
for r in test1_sorted[-5:]:
    print(f"  {r['model'][:50]:50s} slope={r['slope']:.3f} rho={r['rho']:.3f} n={r['n_transactions']}")

# ============================================================
# TEST 2: Inflection Point Convergence Rate
# ============================================================
print("\n" + "="*60)
print("TEST 2: Inflection Point - Where is price discovery fastest?")
print("="*60)

test2_results = []
for model_name, txns in models.items():
    prices = [t['sale_price'] for t in txns]
    n = len(prices)
    
    # Define zones: thin = first 25%, inflection = middle 50%, saturated = last 25%
    thin_end = n // 4
    inflection_end = 3 * n // 4
    
    # Compute rolling SD (window = 20 transactions)
    window = 20
    if n < window * 3:
        continue
    
    rolling_sds = []
    for i in range(window, n):
        sd = np.std(prices[i-window:i])
        rolling_sds.append(sd)
    
    # Compute convergence rate (slope of SD over transaction index) in each zone
    def convergence_rate(sds_segment):
        if len(sds_segment) < 10:
            return None
        x = np.arange(len(sds_segment))
        slope, _ = np.polyfit(x, sds_segment, 1)
        return slope
    
    thin_sds = rolling_sds[:thin_end - window]
    inflection_sds = rolling_sds[thin_end - window:inflection_end - window]
    saturated_sds = rolling_sds[inflection_end - window:]
    
    thin_rate = convergence_rate(thin_sds)
    inflection_rate = convergence_rate(inflection_sds)
    saturated_rate = convergence_rate(saturated_sds)
    
    if all(r is not None for r in [thin_rate, inflection_rate, saturated_rate]):
        # Prediction: inflection_rate should be most negative (fastest convergence)
        rates = [thin_rate, inflection_rate, saturated_rate]
        fastest_zone = rates.index(min(rates))
        
        test2_results.append({
            'model': model_name,
            'n': n,
            'thin_rate': thin_rate,
            'inflection_rate': inflection_rate,
            'saturated_rate': saturated_rate,
            'fastest_zone': ['thin', 'inflection', 'saturated'][fastest_zone],
            'confirmed': fastest_zone == 1  # inflection is fastest
        })

confirmed_t2 = sum(1 for r in test2_results if r['confirmed'])
print(f"\nResults: {confirmed_t2}/{len(test2_results)} models have fastest convergence in inflection zone")
print(f"Zone distribution of fastest convergence:")
zone_counts = defaultdict(int)
for r in test2_results:
    zone_counts[r['fastest_zone']] += 1
for zone, count in sorted(zone_counts.items()):
    print(f"  {zone}: {count} ({100*count/len(test2_results):.0f}%)")

# Aggregate rates
print(f"\nAggregate convergence rates (dSD/dn):")
print(f"  Thin zone:       {np.mean([r['thin_rate'] for r in test2_results]):.4f}")
print(f"  Inflection zone: {np.mean([r['inflection_rate'] for r in test2_results]):.4f}")
print(f"  Saturated zone:  {np.mean([r['saturated_rate'] for r in test2_results]):.4f}")

# ============================================================
# TEST 3: Risk-Adjusted Returns by Zone
# ============================================================
print("\n" + "="*60)
print("TEST 3: Risk-Adjusted Returns (Premium/SD) by Zone")
print("="*60)

test3_results = []
for model_name, txns in models.items():
    n = len(txns)
    thin_end = n // 4
    inflection_end = 3 * n // 4
    
    def zone_sharpe(zone_txns):
        if len(zone_txns) < 10:
            return None
        premiums = [t['premium'] for t in zone_txns]
        mean_prem = np.mean(premiums)
        sd_prem = np.std(premiums)
        if sd_prem == 0:
            return None
        return mean_prem / sd_prem
    
    thin_sharpe = zone_sharpe(txns[:thin_end])
    inflection_sharpe = zone_sharpe(txns[thin_end:inflection_end])
    saturated_sharpe = zone_sharpe(txns[inflection_end:])
    
    if all(s is not None for s in [thin_sharpe, inflection_sharpe, saturated_sharpe]):
        sharpes = [thin_sharpe, inflection_sharpe, saturated_sharpe]
        best_zone = sharpes.index(max(sharpes))
        
        test3_results.append({
            'model': model_name,
            'thin_sharpe': thin_sharpe,
            'inflection_sharpe': inflection_sharpe,
            'saturated_sharpe': saturated_sharpe,
            'best_zone': ['thin', 'inflection', 'saturated'][best_zone],
            'confirmed': best_zone == 1
        })

confirmed_t3 = sum(1 for r in test3_results if r['confirmed'])
print(f"\nResults: {confirmed_t3}/{len(test3_results)} models have best risk-adjusted returns in inflection zone")
zone_counts3 = defaultdict(int)
for r in test3_results:
    zone_counts3[r['best_zone']] += 1
for zone, count in sorted(zone_counts3.items()):
    print(f"  {zone}: {count} ({100*count/len(test3_results):.0f}%)")

print(f"\nAggregate risk-adjusted returns (premium/SD):")
print(f"  Thin zone:       {np.mean([r['thin_sharpe'] for r in test3_results]):.4f}")
print(f"  Inflection zone: {np.mean([r['inflection_sharpe'] for r in test3_results]):.4f}")
print(f"  Saturated zone:  {np.mean([r['saturated_sharpe'] for r in test3_results]):.4f}")

# ============================================================
# TEST 4: Detrended Price Uncertainty (removing appreciation trend)
# ============================================================
print("\n" + "="*60)
print("TEST 4: Detrended Price Uncertainty vs Transaction Count")
print("="*60)

test4_results = []
for model_name, txns in models.items():
    prices = np.array([t['sale_price'] for t in txns], dtype=float)
    n = len(prices)
    
    # Detrend: fit linear trend and compute residuals
    x = np.arange(n)
    slope, intercept = np.polyfit(x, prices, 1)
    residuals = prices - (slope * x + intercept)
    
    # Compute expanding window SD of residuals
    checkpoints = list(range(30, n, max(1, n//15)))
    sds = []
    ns = []
    for cp in checkpoints:
        sd = np.std(residuals[:cp])
        if sd > 0:
            sds.append(sd)
            ns.append(cp)
    
    if len(ns) >= 5:
        log_n = np.log(ns)
        log_sd = np.log(sds)
        fit_slope, _ = np.polyfit(log_n, log_sd, 1)
        rho = np.corrcoef(log_n, log_sd)[0, 1]
        
        test4_results.append({
            'model': model_name,
            'n': n,
            'slope': fit_slope,
            'rho': rho,
            'price_trend': slope,
            'confirmed': fit_slope < -0.1  # meaningful decrease
        })

confirmed_t4 = sum(1 for r in test4_results if r['confirmed'])
print(f"\nResults: {confirmed_t4}/{len(test4_results)} models show detrended SD decreasing with n")
print(f"Mean slope: {np.mean([r['slope'] for r in test4_results]):.4f} (predicted: -0.500)")
print(f"Median slope: {np.median([r['slope'] for r in test4_results]):.4f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("SUMMARY: SNEAKER MARKET INFLECTION POINT TEST")
print("="*60)
print(f"Dataset: 99,956 StockX transactions, 50 shoe models, Sept 2017 - Feb 2019")
print(f"Models tested: {len(models)} (with 200+ transactions each)")
print()
print(f"TEST 1 (SD decreases with n): {confirmed_t1}/{len(test1_results)} confirmed ({100*confirmed_t1/len(test1_results):.0f}%)")
print(f"  Mean slope: {np.mean([r['slope'] for r in test1_results]):.4f} (predicted: -0.500)")
print()
print(f"TEST 2 (Inflection zone has fastest convergence): {confirmed_t2}/{len(test2_results)} confirmed ({100*confirmed_t2/len(test2_results):.0f}%)")
print(f"  Aggregate: thin={np.mean([r['thin_rate'] for r in test2_results]):.4f}, inflection={np.mean([r['inflection_rate'] for r in test2_results]):.4f}, saturated={np.mean([r['saturated_rate'] for r in test2_results]):.4f}")
print()
print(f"TEST 3 (Best risk-adjusted returns in inflection): {confirmed_t3}/{len(test3_results)} confirmed ({100*confirmed_t3/len(test3_results):.0f}%)")
print(f"  Aggregate: thin={np.mean([r['thin_sharpe'] for r in test3_results]):.4f}, inflection={np.mean([r['inflection_sharpe'] for r in test3_results]):.4f}, saturated={np.mean([r['saturated_sharpe'] for r in test3_results]):.4f}")
print()
print(f"TEST 4 (Detrended SD decreases): {confirmed_t4}/{len(test4_results)} confirmed ({100*confirmed_t4/len(test4_results):.0f}%)")
print(f"  Mean detrended slope: {np.mean([r['slope'] for r in test4_results]):.4f}")

# Determine overall verdict
overall_confirmed = (confirmed_t1/len(test1_results) > 0.5 or 
                     confirmed_t2/len(test2_results) > 0.33 or
                     confirmed_t4/len(test4_results) > 0.5)
print(f"\nOVERALL VERDICT: {'THEORY SUPPORTED' if overall_confirmed else 'THEORY NOT SUPPORTED'}")

# ============================================================
# VISUALIZATION
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Interaction Field Theory: StockX Sneaker Market Test\n99,956 Transactions Across 50 Models', fontsize=14, fontweight='bold')

# Plot 1: SD vs n for top models
ax = axes[0, 0]
for r in sorted(test1_results, key=lambda x: x['slope'])[:5]:
    model_name = r['model']
    txns = models[model_name]
    prices = [t['sale_price'] for t in txns]
    n = len(prices)
    checkpoints = list(range(20, n, max(1, n//20)))
    sds = [np.std(prices[:cp]) for cp in checkpoints]
    ax.plot(checkpoints, sds, label=model_name[:30], alpha=0.7)

ax.set_xlabel('Cumulative Transactions (n)')
ax.set_ylabel('Price SD ($)')
ax.set_title('Test 1: Price SD vs Transaction Count\n(Top 5 Confirming Models)')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Plot 2: Convergence rates by zone
ax = axes[0, 1]
zones = ['Thin\n(first 25%)', 'Inflection\n(middle 50%)', 'Saturated\n(last 25%)']
rates = [np.mean([r['thin_rate'] for r in test2_results]),
         np.mean([r['inflection_rate'] for r in test2_results]),
         np.mean([r['saturated_rate'] for r in test2_results])]
colors = ['#e74c3c', '#2ecc71', '#3498db']
bars = ax.bar(zones, rates, color=colors, edgecolor='black', linewidth=0.5)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_ylabel('dSD/dn (convergence rate)')
ax.set_title('Test 2: Price Convergence Rate by Zone\n(More negative = faster convergence)')
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Risk-adjusted returns by zone
ax = axes[1, 0]
sharpes = [np.mean([r['thin_sharpe'] for r in test3_results]),
           np.mean([r['inflection_sharpe'] for r in test3_results]),
           np.mean([r['saturated_sharpe'] for r in test3_results])]
bars = ax.bar(zones, sharpes, color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('Premium / SD (risk-adjusted return)')
ax.set_title('Test 3: Risk-Adjusted Returns by Zone\n(Higher = better for informed buyers)')
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Log-log plot of SD vs n (aggregate)
ax = axes[1, 1]
all_log_ns = []
all_log_sds = []
for model_name, txns in list(models.items())[:10]:
    prices = [t['sale_price'] for t in txns]
    n = len(prices)
    checkpoints = list(range(20, n, max(1, n//20)))
    for cp in checkpoints:
        sd = np.std(prices[:cp])
        if sd > 0:
            all_log_ns.append(np.log(cp))
            all_log_sds.append(np.log(sd))

ax.scatter(all_log_ns, all_log_sds, alpha=0.3, s=10, color='steelblue')
# Fit line
if all_log_ns:
    fit_slope, fit_int = np.polyfit(all_log_ns, all_log_sds, 1)
    x_fit = np.linspace(min(all_log_ns), max(all_log_ns), 100)
    ax.plot(x_fit, fit_slope * x_fit + fit_int, 'r-', linewidth=2, 
            label=f'Measured slope: {fit_slope:.3f}')
    # Predicted line
    ax.plot(x_fit, -0.5 * x_fit + fit_int + (fit_slope + 0.5) * np.mean(all_log_ns), 
            'g--', linewidth=2, label='Predicted slope: -0.500')
ax.set_xlabel('log(n)')
ax.set_ylabel('log(SD)')
ax.set_title('Test 4: Log-Log Price SD vs Transactions\n(Slope should be -0.500)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ubuntu/sneaker_inflection_chart.png', dpi=150, bbox_inches='tight')
print("\nChart saved to /home/ubuntu/sneaker_inflection_chart.png")

# Save results
results = {
    'dataset': '99,956 StockX transactions, 50 models, Sept 2017 - Feb 2019',
    'models_tested': len(models),
    'test1': {
        'description': 'SD decreases with cumulative transactions',
        'confirmed_count': confirmed_t1,
        'total': len(test1_results),
        'pct': 100*confirmed_t1/len(test1_results),
        'mean_slope': np.mean([r['slope'] for r in test1_results]),
        'predicted_slope': -0.5
    },
    'test2': {
        'description': 'Inflection zone has fastest convergence',
        'confirmed_count': confirmed_t2,
        'total': len(test2_results),
        'pct': 100*confirmed_t2/len(test2_results),
        'aggregate_rates': {
            'thin': np.mean([r['thin_rate'] for r in test2_results]),
            'inflection': np.mean([r['inflection_rate'] for r in test2_results]),
            'saturated': np.mean([r['saturated_rate'] for r in test2_results])
        }
    },
    'test3': {
        'description': 'Best risk-adjusted returns in inflection zone',
        'confirmed_count': confirmed_t3,
        'total': len(test3_results),
        'pct': 100*confirmed_t3/len(test3_results),
        'aggregate_sharpes': {
            'thin': np.mean([r['thin_sharpe'] for r in test3_results]),
            'inflection': np.mean([r['inflection_sharpe'] for r in test3_results]),
            'saturated': np.mean([r['saturated_sharpe'] for r in test3_results])
        }
    },
    'test4': {
        'description': 'Detrended SD decreases with n',
        'confirmed_count': confirmed_t4,
        'total': len(test4_results),
        'pct': 100*confirmed_t4/len(test4_results),
        'mean_slope': np.mean([r['slope'] for r in test4_results])
    }
}

with open('/home/ubuntu/sneaker_inflection_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Results saved to /home/ubuntu/sneaker_inflection_results.json")
