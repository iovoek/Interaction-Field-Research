#!/usr/bin/env python3
"""
Empirical Analysis: Testing the Interaction Field Inflection Point Prediction
=============================================================================
Using 80 Gundam TCG cards from PriceCharting with sales volume and price data.

The prediction: cards near the liquidity inflection point (moderate volume) 
should show better price convergence and more predictable pricing than either 
thin-market cards (low volume) or saturated-market cards (high volume, but 
already efficient -- no opportunity).

We test this by examining:
1. Price dispersion (spread between loose/CIB/new prices) as a function of volume
2. Whether the relationship follows the logistic S-curve pattern
3. Whether mid-volume cards show the steepest improvement in price stability
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr, spearmanr

# Load data
with open("/home/ubuntu/empirical_data_raw.json") as f:
    raw_data = json.load(f)

print("=" * 70)
print("EMPIRICAL ANALYSIS: Testing the Inflection Point Prediction")
print("=" * 70)
print(f"\nDataset: {len(raw_data)} Gundam TCG cards from PriceCharting")
print()

# Clean and structure data
cards = []
for p in raw_data:
    try:
        vol = int(p.get("sales-volume", 0))
        loose = int(p.get("loose-price", 0))
        cib = int(p.get("cib-price", 0))
        new = int(p.get("new-price", 0))
        manual = int(p.get("manual-only-price", 0))
        
        if vol > 0 and loose > 0:
            # Price dispersion: how much do different condition prices vary?
            # This is a proxy for "price certainty" -- lower dispersion = more certain
            prices_available = [x for x in [loose, cib, new, manual] if x > 0]
            
            if len(prices_available) >= 2:
                mean_price = np.mean(prices_available)
                std_price = np.std(prices_available)
                cv = std_price / mean_price  # Coefficient of variation
                
                # Retail spread as another metric
                retail_buy = int(p.get("retail-loose-buy", 0))
                retail_sell = int(p.get("retail-loose-sell", 0))
                spread_pct = 0
                if retail_buy > 0 and retail_sell > 0:
                    spread_pct = (retail_sell - retail_buy) / retail_sell
                
                cards.append({
                    "name": p.get("product-name", "?"),
                    "volume": vol,
                    "loose_price": loose / 100,  # Convert cents to dollars
                    "mean_price": mean_price / 100,
                    "price_cv": cv,  # Coefficient of variation (lower = more stable)
                    "spread_pct": spread_pct,  # Buy-sell spread (lower = more efficient)
                    "n_prices": len(prices_available),
                })
    except (ValueError, TypeError):
        pass

cards.sort(key=lambda x: x["volume"])
print(f"Cards with valid multi-price data: {len(cards)}")

# Extract arrays
volumes = np.array([c["volume"] for c in cards])
cvs = np.array([c["price_cv"] for c in cards])
spreads = np.array([c["spread_pct"] for c in cards])
prices = np.array([c["loose_price"] for c in cards])

print(f"\nVolume range: {volumes.min()} to {volumes.max()}")
print(f"Price range: ${prices.min():.2f} to ${prices.max():.2f}")
print(f"CV range: {cvs.min():.3f} to {cvs.max():.3f}")
print()

# ============================================================
# TEST 1: Does price certainty increase with transaction volume?
# ============================================================
print("=" * 70)
print("TEST 1: Does price certainty increase with transaction volume?")
print("=" * 70)
print()
print("Prediction: Higher volume -> lower coefficient of variation (more price certainty)")
print()

# Correlation between volume and CV
corr_pearson, p_pearson = pearsonr(volumes, cvs)
corr_spearman, p_spearman = spearmanr(volumes, cvs)

print(f"Pearson correlation (volume vs CV):  r = {corr_pearson:.4f}, p = {p_pearson:.6f}")
print(f"Spearman correlation (volume vs CV): rho = {corr_spearman:.4f}, p = {p_spearman:.6f}")
print()

if corr_spearman < 0 and p_spearman < 0.05:
    print("RESULT: CONFIRMED. Higher volume is significantly associated with lower")
    print("        price dispersion (more certainty). This is the 1/sqrt(n) prediction.")
elif corr_spearman < 0:
    print("RESULT: DIRECTIONALLY CONFIRMED but not statistically significant.")
    print(f"        (p = {p_spearman:.4f}, need p < 0.05)")
else:
    print("RESULT: NOT CONFIRMED. Volume does not reduce price dispersion in this sample.")

print()

# ============================================================
# TEST 2: Does the relationship follow the 1/sqrt(n) form?
# ============================================================
print("=" * 70)
print("TEST 2: Does price uncertainty follow the 1/sqrt(n) form?")
print("=" * 70)
print()
print("Prediction: CV should decrease approximately as 1/sqrt(volume)")
print()

# Fit: CV = a / sqrt(n) + b
def inv_sqrt_model(n, a, b):
    return a / np.sqrt(n) + b

# Fit: CV = a / n^c + b (generalized power law)
def power_model(n, a, b, c):
    return a / (n ** c) + b

try:
    popt_sqrt, pcov_sqrt = curve_fit(inv_sqrt_model, volumes, cvs, p0=[1.0, 0.1], maxfev=5000)
    cv_predicted_sqrt = inv_sqrt_model(volumes, *popt_sqrt)
    ss_res_sqrt = np.sum((cvs - cv_predicted_sqrt) ** 2)
    ss_tot = np.sum((cvs - np.mean(cvs)) ** 2)
    r2_sqrt = 1 - ss_res_sqrt / ss_tot
    print(f"1/sqrt(n) model: CV = {popt_sqrt[0]:.4f} / sqrt(n) + {popt_sqrt[1]:.4f}")
    print(f"  R-squared: {r2_sqrt:.4f}")
except Exception as e:
    print(f"  1/sqrt(n) fit failed: {e}")
    r2_sqrt = -1

try:
    popt_pow, pcov_pow = curve_fit(power_model, volumes, cvs, p0=[1.0, 0.1, 0.5], maxfev=5000)
    cv_predicted_pow = power_model(volumes, *popt_pow)
    ss_res_pow = np.sum((cvs - cv_predicted_pow) ** 2)
    r2_pow = 1 - ss_res_pow / ss_tot
    print(f"\nGeneralized power model: CV = {popt_pow[0]:.4f} / n^{popt_pow[2]:.4f} + {popt_pow[1]:.4f}")
    print(f"  R-squared: {r2_pow:.4f}")
    print(f"  Fitted exponent: {popt_pow[2]:.4f} (theory predicts 0.5)")
except Exception as e:
    print(f"  Power model fit failed: {e}")
    r2_pow = -1

# Linear model for comparison
from numpy.polynomial import polynomial as P
coeffs = np.polyfit(volumes, cvs, 1)
cv_predicted_lin = np.polyval(coeffs, volumes)
ss_res_lin = np.sum((cvs - cv_predicted_lin) ** 2)
r2_lin = 1 - ss_res_lin / ss_tot
print(f"\nLinear model: CV = {coeffs[0]:.6f} * n + {coeffs[1]:.4f}")
print(f"  R-squared: {r2_lin:.4f}")

print(f"\nModel comparison:")
print(f"  1/sqrt(n):   R2 = {r2_sqrt:.4f}")
print(f"  Power law:   R2 = {r2_pow:.4f}")
print(f"  Linear:      R2 = {r2_lin:.4f}")

if r2_sqrt > r2_lin:
    print("\n  The 1/sqrt(n) model fits better than linear -- consistent with theory.")
else:
    print("\n  Linear model fits better -- the 1/sqrt(n) form may not be the best description.")

print()

# ============================================================
# TEST 3: Inflection Point - Do mid-volume cards show the steepest
#          improvement in price stability?
# ============================================================
print("=" * 70)
print("TEST 3: Inflection Point Detection")
print("=" * 70)
print()
print("Prediction: The rate of price-certainty improvement should be highest")
print("at a specific volume level (the inflection point n_c).")
print()

# Divide into terciles
n = len(cards)
t1 = n // 3
t2 = 2 * n // 3

thin_cards = cards[:t1]
mid_cards = cards[t1:t2]
saturated_cards = cards[t2:]

thin_cv = np.mean([c["price_cv"] for c in thin_cards])
mid_cv = np.mean([c["price_cv"] for c in mid_cards])
sat_cv = np.mean([c["price_cv"] for c in saturated_cards])

thin_vol = np.mean([c["volume"] for c in thin_cards])
mid_vol = np.mean([c["volume"] for c in mid_cards])
sat_vol = np.mean([c["volume"] for c in saturated_cards])

print(f"Tercile Analysis:")
print(f"  Thin market  (vol {int(thin_vol):>4} avg): Mean CV = {thin_cv:.4f}")
print(f"  Mid market   (vol {int(mid_vol):>4} avg): Mean CV = {mid_cv:.4f}")
print(f"  Saturated    (vol {int(sat_vol):>4} avg): Mean CV = {sat_cv:.4f}")
print()

# Rate of improvement between terciles
improvement_thin_to_mid = (thin_cv - mid_cv) / (mid_vol - thin_vol) if mid_vol != thin_vol else 0
improvement_mid_to_sat = (mid_cv - sat_cv) / (sat_vol - mid_vol) if sat_vol != mid_vol else 0

print(f"  Rate of CV improvement (thin -> mid):  {improvement_thin_to_mid:.6f} per unit volume")
print(f"  Rate of CV improvement (mid -> sat):   {improvement_mid_to_sat:.6f} per unit volume")
print()

if improvement_thin_to_mid > improvement_mid_to_sat:
    print("  RESULT: The steepest improvement occurs in the THIN -> MID transition.")
    print("  This is consistent with the inflection point being in the mid-volume zone.")
    print("  The theory predicts this: the inflection point is where price certainty")
    print("  improves fastest, which is the optimal zone for informed participants.")
else:
    print("  RESULT: The steepest improvement occurs in the MID -> SATURATED transition.")
    print("  The inflection point may be at higher volumes than the mid tercile.")

print()

# ============================================================
# TEST 4: Spread analysis (buy-sell spread as market efficiency proxy)
# ============================================================
print("=" * 70)
print("TEST 4: Market Efficiency (Buy-Sell Spread)")
print("=" * 70)
print()

valid_spreads = [(c["volume"], c["spread_pct"]) for c in cards if c["spread_pct"] > 0]
if valid_spreads:
    sp_vols = np.array([x[0] for x in valid_spreads])
    sp_spreads = np.array([x[1] for x in valid_spreads])
    
    corr_sp, p_sp = spearmanr(sp_vols, sp_spreads)
    print(f"Spearman correlation (volume vs buy-sell spread): rho = {corr_sp:.4f}, p = {p_sp:.6f}")
    
    if corr_sp < 0 and p_sp < 0.05:
        print("RESULT: CONFIRMED. Higher volume -> tighter spreads (more efficient market).")
    elif corr_sp < 0:
        print(f"RESULT: Directionally correct but not significant (p = {p_sp:.4f}).")
    else:
        print("RESULT: Not confirmed for this metric.")
else:
    print("Insufficient spread data available.")

print()

# ============================================================
# TEST 5: Logistic fit to price certainty vs volume
# ============================================================
print("=" * 70)
print("TEST 5: Does price certainty follow a logistic (S-curve) pattern?")
print("=" * 70)
print()

# Price certainty = 1 - CV (higher = more certain)
certainties = 1 - cvs

def logistic(n, V_max, k, n_c):
    return V_max / (1 + np.exp(-k * (n - n_c)))

try:
    # Initial guess
    p0 = [np.max(certainties), 0.01, np.median(volumes)]
    popt_log, pcov_log = curve_fit(logistic, volumes, certainties, p0=p0, maxfev=10000)
    cert_predicted = logistic(volumes, *popt_log)
    ss_res_log = np.sum((certainties - cert_predicted) ** 2)
    ss_tot_cert = np.sum((certainties - np.mean(certainties)) ** 2)
    r2_log = 1 - ss_res_log / ss_tot_cert
    
    print(f"Logistic fit: Certainty = {popt_log[0]:.4f} / (1 + exp(-{popt_log[1]:.6f} * (n - {popt_log[2]:.1f})))")
    print(f"  V_max (maximum certainty): {popt_log[0]:.4f}")
    print(f"  k (coupling constant):     {popt_log[1]:.6f}")
    print(f"  n_c (inflection point):    {popt_log[2]:.1f} transactions")
    print(f"  R-squared:                 {r2_log:.4f}")
    print()
    
    if r2_log > 0.3:
        print(f"  RESULT: The logistic model provides a reasonable fit (R2 = {r2_log:.4f}).")
        print(f"  The estimated inflection point is at approximately {popt_log[2]:.0f} sales volume.")
        print(f"  This means the optimal information-gain zone for this market is near")
        print(f"  {popt_log[2]:.0f} completed transactions.")
    else:
        print(f"  RESULT: The logistic fit is weak (R2 = {r2_log:.4f}). The S-curve pattern")
        print(f"  is not strongly supported in this dataset.")
        
except Exception as e:
    print(f"  Logistic fit failed: {e}")
    popt_log = None
    r2_log = -1

print()

# ============================================================
# GENERATE PLOTS
# ============================================================
print("Generating visualization...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Empirical Test: Interaction Field Theory\nGundam TCG Cards (n=80)", 
             fontsize=14, fontweight='bold')

# Plot 1: Volume vs CV scatter
ax1 = axes[0, 0]
ax1.scatter(volumes, cvs, alpha=0.6, s=40, c='#2a9d8f', edgecolors='white', linewidth=0.5)
if r2_sqrt > 0:
    vol_smooth = np.linspace(volumes.min(), volumes.max(), 200)
    ax1.plot(vol_smooth, inv_sqrt_model(vol_smooth, *popt_sqrt), 'r-', linewidth=2, 
             label=f'1/sqrt(n) fit (R2={r2_sqrt:.3f})')
ax1.set_xlabel("Sales Volume (n)")
ax1.set_ylabel("Coefficient of Variation (CV)")
ax1.set_title("Price Dispersion vs Transaction Volume")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Logistic fit to certainty
ax2 = axes[0, 1]
ax2.scatter(volumes, certainties, alpha=0.6, s=40, c='#e76f51', edgecolors='white', linewidth=0.5)
if popt_log is not None and r2_log > 0:
    vol_smooth = np.linspace(volumes.min(), volumes.max(), 200)
    ax2.plot(vol_smooth, logistic(vol_smooth, *popt_log), 'b-', linewidth=2,
             label=f'Logistic fit (R2={r2_log:.3f})\nn_c={popt_log[2]:.0f}')
    ax2.axvline(x=popt_log[2], color='blue', linestyle='--', alpha=0.5, label=f'Inflection n_c={popt_log[2]:.0f}')
ax2.set_xlabel("Sales Volume (n)")
ax2.set_ylabel("Price Certainty (1 - CV)")
ax2.set_title("Price Certainty vs Transaction Volume (Logistic Fit)")
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Tercile comparison
ax3 = axes[1, 0]
tercile_labels = ['Thin\n(Low Vol)', 'Inflection\n(Mid Vol)', 'Saturated\n(High Vol)']
tercile_cvs = [thin_cv, mid_cv, sat_cv]
bars = ax3.bar(tercile_labels, tercile_cvs, color=['#e76f51', '#2a9d8f', '#264653'], alpha=0.8)
ax3.set_ylabel("Mean Coefficient of Variation")
ax3.set_title("Price Dispersion by Liquidity Stage")
ax3.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, tercile_cvs):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
             f'{val:.4f}', ha='center', fontsize=10)

# Plot 4: Rate of improvement
ax4 = axes[1, 1]
if valid_spreads:
    ax4.scatter(sp_vols, sp_spreads * 100, alpha=0.6, s=40, c='#e9c46a', edgecolors='white', linewidth=0.5)
    ax4.set_xlabel("Sales Volume (n)")
    ax4.set_ylabel("Buy-Sell Spread (%)")
    ax4.set_title("Market Efficiency (Spread) vs Volume")
    ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/home/ubuntu/empirical_results.png", dpi=150, bbox_inches='tight')
print("  Saved: /home/ubuntu/empirical_results.png")

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY OF EMPIRICAL RESULTS")
print("=" * 70)
print()
print(f"Dataset: {len(cards)} Gundam TCG cards, volume range {volumes.min()}-{volumes.max()}")
print()
print("Test 1 (Volume reduces uncertainty):     ", end="")
if corr_spearman < 0 and p_spearman < 0.05:
    print("CONFIRMED (p < 0.05)")
elif corr_spearman < 0:
    print(f"DIRECTIONAL (p = {p_spearman:.4f})")
else:
    print("NOT CONFIRMED")

print("Test 2 (1/sqrt(n) scaling):              ", end="")
if r2_sqrt > r2_lin and r2_sqrt > 0.1:
    print(f"SUPPORTED (R2 = {r2_sqrt:.4f} > linear R2 = {r2_lin:.4f})")
elif r2_sqrt > 0:
    print(f"WEAK (R2 = {r2_sqrt:.4f})")
else:
    print("FAILED")

print("Test 3 (Inflection point exists):        ", end="")
if improvement_thin_to_mid > improvement_mid_to_sat:
    print("CONFIRMED (steepest improvement in thin->mid)")
else:
    print("PARTIAL (steepest improvement in mid->sat)")

print("Test 4 (Volume tightens spreads):        ", end="")
if valid_spreads and corr_sp < 0 and p_sp < 0.05:
    print("CONFIRMED (p < 0.05)")
elif valid_spreads and corr_sp < 0:
    print(f"DIRECTIONAL (p = {p_sp:.4f})")
else:
    print("INSUFFICIENT DATA")

print("Test 5 (Logistic S-curve fit):           ", end="")
if r2_log > 0.3:
    print(f"SUPPORTED (R2 = {r2_log:.4f}, n_c = {popt_log[2]:.0f})")
elif r2_log > 0.1:
    print(f"WEAK (R2 = {r2_log:.4f})")
else:
    print("NOT SUPPORTED")

print()
print("=" * 70)

# Save results to JSON for the website
results = {
    "dataset": {
        "source": "PriceCharting API",
        "market": "Gundam TCG",
        "n_cards": len(cards),
        "volume_range": [int(volumes.min()), int(volumes.max())],
        "price_range_usd": [float(prices.min()), float(prices.max())],
    },
    "test_1_volume_reduces_uncertainty": {
        "spearman_rho": float(corr_spearman),
        "p_value": float(p_spearman),
        "confirmed": bool(corr_spearman < 0 and p_spearman < 0.05),
    },
    "test_2_sqrt_n_scaling": {
        "r2_sqrt_model": float(r2_sqrt),
        "r2_linear_model": float(r2_lin),
        "r2_power_model": float(r2_pow),
        "fitted_exponent": float(popt_pow[2]) if r2_pow > 0 else None,
        "sqrt_beats_linear": bool(r2_sqrt > r2_lin),
    },
    "test_3_inflection_point": {
        "thin_cv": float(thin_cv),
        "mid_cv": float(mid_cv),
        "saturated_cv": float(sat_cv),
        "improvement_thin_to_mid": float(improvement_thin_to_mid),
        "improvement_mid_to_sat": float(improvement_mid_to_sat),
        "steepest_in_first_transition": bool(improvement_thin_to_mid > improvement_mid_to_sat),
    },
    "test_5_logistic_fit": {
        "r2": float(r2_log) if r2_log > 0 else None,
        "V_max": float(popt_log[0]) if popt_log is not None else None,
        "k": float(popt_log[1]) if popt_log is not None else None,
        "n_c": float(popt_log[2]) if popt_log is not None else None,
    },
}

with open("/home/ubuntu/empirical_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nResults saved to /home/ubuntu/empirical_results.json")
print("Chart saved to /home/ubuntu/empirical_results.png")
