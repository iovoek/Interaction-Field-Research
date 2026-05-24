"""
INFLECTION POINT ARBITRAGE TEST - MULTI-MARKET LONGITUDINAL

Tests the prediction across:
1. Stocks from IPO through maturity (longitudinal, same asset over time)
2. Cryptocurrency markets (high-frequency, wide liquidity range)
3. Cross-sectional stock market (wide volume range, multiple years)

The prediction: Price discovery rate (rate at which SD decreases) is
FASTEST when an asset is near its liquidity inflection point n_c.

This means: informed buyers have the largest edge in the inflection zone.
"""

import numpy as np
import json
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, kruskal
from scipy.optimize import curve_fit

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.run(['pip3', 'install', 'yfinance', '-q'])
    import yfinance as yf


def logistic(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))


# ============================================================
# TEST 1: STOCKS FROM IPO THROUGH MATURITY
# Track the same stock over its entire life from IPO to present
# Measure how price SD changes as cumulative volume grows
# ============================================================

def test_ipo_to_maturity():
    """
    Track stocks from their IPO through maturity.
    For each stock, compute rolling price SD and cumulative volume.
    Test if convergence rate is fastest in the inflection zone.
    """
    print("=" * 65)
    print("TEST 1: STOCKS FROM IPO THROUGH MATURITY")
    print("=" * 65)
    
    # Stocks with known IPO dates and long histories
    # Mix of tech, retail, biotech, finance -- wide variety
    stocks = {
        'TSLA': '2010-06-29',   # Tesla IPO
        'META': '2012-05-18',   # Facebook/Meta IPO
        'SNAP': '2017-03-02',   # Snap IPO
        'UBER': '2019-05-10',   # Uber IPO
        'COIN': '2021-04-14',   # Coinbase IPO
        'RIVN': '2021-11-10',   # Rivian IPO
        'PLTR': '2020-09-30',   # Palantir IPO
        'RBLX': '2021-03-10',   # Roblox IPO
        'ABNB': '2020-12-10',   # Airbnb IPO
        'SNOW': '2020-09-16',   # Snowflake IPO
        'ZM': '2019-04-18',    # Zoom IPO
        'DASH': '2020-12-09',   # DoorDash IPO
        'SQ': '2015-11-19',    # Square/Block IPO
        'SHOP': '2015-05-21',   # Shopify IPO
        'SPOT': '2018-04-03',   # Spotify IPO
    }
    
    results = []
    
    for ticker, ipo_date in stocks.items():
        print(f"  {ticker} (IPO: {ipo_date})...", end=' ', flush=True)
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=ipo_date, interval='1wk')
            
            if df is None or len(df) < 50:
                print("(insufficient data)")
                continue
            
            prices = df['Close'].values
            volumes = df['Volume'].values
            n_weeks = len(prices)
            
            # Compute cumulative volume (proxy for total transactions)
            cum_volume = np.cumsum(volumes)
            
            # Compute rolling SD of weekly returns (window=12 weeks = ~3 months)
            returns = np.diff(np.log(prices))
            window = 12
            rolling_sd = []
            rolling_cum_vol = []
            
            for i in range(window, len(returns) + 1):
                rolling_sd.append(np.std(returns[i-window:i]))
                rolling_cum_vol.append(cum_volume[i])
            
            rolling_sd = np.array(rolling_sd)
            rolling_cum_vol = np.array(rolling_cum_vol, dtype=float)
            
            if len(rolling_sd) < 20:
                print("(insufficient windows)")
                continue
            
            # Normalize cumulative volume to [0, 1] for zone classification
            cv_norm = (rolling_cum_vol - rolling_cum_vol.min()) / (rolling_cum_vol.max() - rolling_cum_vol.min())
            
            # Find n_c by fitting logistic to cumulative volume growth
            time_idx = np.arange(len(rolling_cum_vol), dtype=float)
            try:
                popt, _ = curve_fit(
                    logistic, time_idx, cv_norm,
                    p0=[1.0, 0.05, len(time_idx)/2],
                    bounds=([0.5, 0.001, 5], [2.0, 1.0, len(time_idx)*0.95]),
                    maxfev=5000
                )
                n_c_idx = int(popt[2])
            except:
                n_c_idx = len(time_idx) // 2
            
            # Zones based on time index relative to n_c
            thin_mask = time_idx < n_c_idx * 0.5
            infl_mask = (time_idx >= n_c_idx * 0.7) & (time_idx <= n_c_idx * 1.3)
            satu_mask = time_idx > n_c_idx * 1.5
            
            # Compute dSD/dt in each zone
            dsd = np.gradient(rolling_sd, time_idx)
            
            thin_rate = np.mean(dsd[thin_mask]) if thin_mask.sum() > 3 else None
            infl_rate = np.mean(dsd[infl_mask]) if infl_mask.sum() > 3 else None
            satu_rate = np.mean(dsd[satu_mask]) if satu_mask.sum() > 3 else None
            
            # Overall correlation
            rho, pval = spearmanr(time_idx, rolling_sd)
            
            result = {
                'ticker': ticker,
                'n_weeks': n_weeks,
                'n_c_idx': n_c_idx,
                'thin_rate': thin_rate,
                'infl_rate': infl_rate,
                'satu_rate': satu_rate,
                'rho': float(rho),
                'pval': float(pval)
            }
            results.append(result)
            
            # Determine fastest zone
            rates = [r for r in [thin_rate, infl_rate, satu_rate] if r is not None]
            labels = [l for l, r in zip(['thin', 'infl', 'satu'], [thin_rate, infl_rate, satu_rate]) if r is not None]
            if rates:
                fastest = labels[np.argmin(rates)]
            else:
                fastest = 'N/A'
            
            print(f"{n_weeks}wk, n_c={n_c_idx}, fastest={fastest}, rho={rho:.3f}")
            
        except Exception as e:
            print(f"(error: {str(e)[:40]})")
            continue
        
        time.sleep(0.3)
    
    return results


# ============================================================
# TEST 2: CRYPTOCURRENCY MARKETS
# Crypto has extreme liquidity variation and 24/7 trading
# ============================================================

def test_crypto_markets():
    """
    Test crypto assets at different maturity stages.
    BTC/ETH = saturated, mid-caps = inflection, micro-caps = thin.
    """
    print("\n" + "=" * 65)
    print("TEST 2: CRYPTOCURRENCY MARKETS (LONGITUDINAL)")
    print("=" * 65)
    
    # Use crypto tickers available via yfinance
    cryptos = {
        'BTC-USD': 'saturated',
        'ETH-USD': 'saturated',
        'SOL-USD': 'inflection',
        'DOGE-USD': 'inflection',
        'ADA-USD': 'inflection',
        'AVAX-USD': 'inflection',
        'LINK-USD': 'inflection',
        'DOT-USD': 'inflection',
        'MATIC-USD': 'inflection',
        'ATOM-USD': 'inflection',
    }
    
    results = []
    
    for ticker, expected_stage in cryptos.items():
        print(f"  {ticker} ({expected_stage})...", end=' ', flush=True)
        try:
            data = yf.Ticker(ticker)
            df = data.history(period='5y', interval='1wk')
            
            if df is None or len(df) < 50:
                print("(insufficient data)")
                continue
            
            prices = df['Close'].values
            volumes = df['Volume'].values
            n_weeks = len(prices)
            
            # Rolling SD of weekly returns
            returns = np.diff(np.log(prices))
            window = 12
            rolling_sd = []
            rolling_vol = []
            
            for i in range(window, len(returns) + 1):
                rolling_sd.append(np.std(returns[i-window:i]))
                rolling_vol.append(np.mean(volumes[i-window:i]))
            
            rolling_sd = np.array(rolling_sd)
            rolling_vol = np.array(rolling_vol)
            time_idx = np.arange(len(rolling_sd), dtype=float)
            
            # Find n_c
            cum_vol = np.cumsum(volumes[window:len(returns)+1])
            cv_norm = cum_vol / cum_vol.max() if cum_vol.max() > 0 else cum_vol
            try:
                popt, _ = curve_fit(
                    logistic, time_idx, cv_norm,
                    p0=[1.0, 0.05, len(time_idx)/2],
                    bounds=([0.5, 0.001, 5], [2.0, 1.0, len(time_idx)*0.95]),
                    maxfev=5000
                )
                n_c_idx = int(popt[2])
            except:
                n_c_idx = len(time_idx) // 2
            
            # Zones
            thin_mask = time_idx < n_c_idx * 0.5
            infl_mask = (time_idx >= n_c_idx * 0.7) & (time_idx <= n_c_idx * 1.3)
            satu_mask = time_idx > n_c_idx * 1.5
            
            dsd = np.gradient(rolling_sd, time_idx)
            
            thin_rate = np.mean(dsd[thin_mask]) if thin_mask.sum() > 3 else None
            infl_rate = np.mean(dsd[infl_mask]) if infl_mask.sum() > 3 else None
            satu_rate = np.mean(dsd[satu_mask]) if satu_mask.sum() > 3 else None
            
            rho, pval = spearmanr(time_idx, rolling_sd)
            
            results.append({
                'ticker': ticker,
                'expected_stage': expected_stage,
                'n_weeks': n_weeks,
                'n_c_idx': n_c_idx,
                'thin_rate': thin_rate,
                'infl_rate': infl_rate,
                'satu_rate': satu_rate,
                'rho': float(rho),
                'pval': float(pval)
            })
            
            rates = [r for r in [thin_rate, infl_rate, satu_rate] if r is not None]
            labels = [l for l, r in zip(['thin', 'infl', 'satu'], [thin_rate, infl_rate, satu_rate]) if r is not None]
            fastest = labels[np.argmin(rates)] if rates else 'N/A'
            print(f"{n_weeks}wk, fastest={fastest}, rho={rho:.3f}")
            
        except Exception as e:
            print(f"(error: {str(e)[:40]})")
            continue
        
        time.sleep(0.3)
    
    return results


# ============================================================
# TEST 3: CROSS-SECTIONAL MULTI-YEAR (2015-2024)
# Wide volume range, 10 years of data, many stocks
# ============================================================

def test_cross_sectional_multiyear():
    """
    Test across a wide range of stocks over 10 years.
    Classify by average daily volume into liquidity stages.
    Measure if mid-volume stocks show fastest price convergence.
    """
    print("\n" + "=" * 65)
    print("TEST 3: CROSS-SECTIONAL MULTI-YEAR (2015-2024)")
    print("=" * 65)
    
    # Wide range of stocks by expected liquidity
    tickers = [
        # Mega-cap (saturated)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM',
        # Large-cap (post-inflection)
        'CRM', 'ADBE', 'NFLX', 'AMD', 'INTC',
        # Mid-cap (inflection zone)
        'ETSY', 'ROKU', 'PINS', 'TTD', 'CRWD',
        # Small-cap (pre-inflection)
        'APPS', 'BIGC', 'DOCS', 'TASK', 'COUR',
        # Micro-cap (thin)
        'GEVO', 'WKHS', 'CLSK', 'MARA', 'RIOT',
    ]
    
    results = []
    
    for ticker in tickers:
        print(f"  {ticker}...", end=' ', flush=True)
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period='10y', interval='1wk')
            
            if df is None or len(df) < 100:
                print("(insufficient data)")
                continue
            
            prices = df['Close'].values
            volumes = df['Volume'].values
            avg_volume = np.mean(volumes)
            
            # Rolling SD of returns
            returns = np.diff(np.log(prices))
            window = 26  # 6 months
            rolling_sd = []
            
            for i in range(window, len(returns) + 1):
                rolling_sd.append(np.std(returns[i-window:i]))
            
            rolling_sd = np.array(rolling_sd)
            time_idx = np.arange(len(rolling_sd), dtype=float)
            
            # Overall trend in SD
            rho, pval = spearmanr(time_idx, rolling_sd)
            
            # Convergence rate (slope of SD over time)
            slope = np.polyfit(time_idx, rolling_sd, 1)[0]
            
            # Mean SD level
            mean_sd = np.mean(rolling_sd)
            
            results.append({
                'ticker': ticker,
                'avg_volume': float(avg_volume),
                'n_weeks': len(prices),
                'mean_sd': float(mean_sd),
                'convergence_slope': float(slope),
                'rho': float(rho),
                'pval': float(pval)
            })
            
            print(f"vol={avg_volume:.0f}, SD={mean_sd:.4f}, slope={slope:.6f}, rho={rho:.3f}")
            
        except Exception as e:
            print(f"(error: {str(e)[:40]})")
            continue
        
        time.sleep(0.2)
    
    return results


def analyze_and_report(ipo_results, crypto_results, cross_results):
    """Synthesize all results and produce final verdict."""
    
    print("\n" + "=" * 65)
    print("SYNTHESIS AND VERDICT")
    print("=" * 65)
    
    # TEST 1 ANALYSIS: IPO stocks
    print("\n--- TEST 1: IPO to Maturity ---")
    if ipo_results:
        n = len(ipo_results)
        # Count how many have inflection as fastest convergence zone
        infl_fastest = 0
        sd_decreasing = 0
        valid = [r for r in ipo_results if all(r.get(k) is not None for k in ['thin_rate', 'infl_rate', 'satu_rate'])]
        
        for r in valid:
            if r['infl_rate'] < r['thin_rate'] and r['infl_rate'] < r['satu_rate']:
                infl_fastest += 1
            if r['rho'] < -0.1:
                sd_decreasing += 1
        
        if valid:
            avg_thin = np.mean([r['thin_rate'] for r in valid])
            avg_infl = np.mean([r['infl_rate'] for r in valid])
            avg_satu = np.mean([r['satu_rate'] for r in valid])
            
            print(f"  Cards with all 3 zones: {len(valid)}/{n}")
            print(f"  Inflection fastest per-card: {infl_fastest}/{len(valid)} = {infl_fastest/len(valid)*100:.0f}%")
            print(f"  SD decreasing over time: {sd_decreasing}/{n} = {sd_decreasing/n*100:.0f}%")
            print(f"  Avg rates: thin={avg_thin:+.6f}, infl={avg_infl:+.6f}, satu={avg_satu:+.6f}")
            print(f"  Aggregate inflection fastest: {'YES' if avg_infl < avg_thin and avg_infl < avg_satu else 'NO'}")
        else:
            print("  No stocks had all three zones populated.")
    
    # TEST 2 ANALYSIS: Crypto
    print("\n--- TEST 2: Cryptocurrency ---")
    if crypto_results:
        n = len(crypto_results)
        valid = [r for r in crypto_results if all(r.get(k) is not None for k in ['thin_rate', 'infl_rate', 'satu_rate'])]
        infl_fastest = 0
        
        for r in valid:
            if r['infl_rate'] < r['thin_rate'] and r['infl_rate'] < r['satu_rate']:
                infl_fastest += 1
        
        if valid:
            avg_thin = np.mean([r['thin_rate'] for r in valid])
            avg_infl = np.mean([r['infl_rate'] for r in valid])
            avg_satu = np.mean([r['satu_rate'] for r in valid])
            
            print(f"  Cryptos with all 3 zones: {len(valid)}/{n}")
            print(f"  Inflection fastest per-asset: {infl_fastest}/{len(valid)} = {infl_fastest/len(valid)*100:.0f}%")
            print(f"  Avg rates: thin={avg_thin:+.6f}, infl={avg_infl:+.6f}, satu={avg_satu:+.6f}")
            print(f"  Aggregate inflection fastest: {'YES' if avg_infl < avg_thin and avg_infl < avg_satu else 'NO'}")
        else:
            print("  No cryptos had all three zones populated.")
    
    # TEST 3 ANALYSIS: Cross-sectional
    print("\n--- TEST 3: Cross-Sectional Multi-Year ---")
    if cross_results:
        # Sort by volume and split into terciles
        sorted_by_vol = sorted(cross_results, key=lambda x: x['avg_volume'])
        n = len(sorted_by_vol)
        tercile_size = n // 3
        
        thin = sorted_by_vol[:tercile_size]
        mid = sorted_by_vol[tercile_size:2*tercile_size]
        saturated = sorted_by_vol[2*tercile_size:]
        
        thin_slope = np.mean([r['convergence_slope'] for r in thin])
        mid_slope = np.mean([r['convergence_slope'] for r in mid])
        sat_slope = np.mean([r['convergence_slope'] for r in saturated])
        
        thin_sd = np.mean([r['mean_sd'] for r in thin])
        mid_sd = np.mean([r['mean_sd'] for r in mid])
        sat_sd = np.mean([r['mean_sd'] for r in saturated])
        
        print(f"  Stocks analyzed: {n}")
        print(f"  Tercile 1 (thin, low vol): slope={thin_slope:+.6f}, SD={thin_sd:.4f}")
        print(f"  Tercile 2 (mid, inflection): slope={mid_slope:+.6f}, SD={mid_sd:.4f}")
        print(f"  Tercile 3 (saturated, high vol): slope={sat_slope:+.6f}, SD={sat_sd:.4f}")
        print(f"  Mid-volume has fastest convergence: {'YES' if mid_slope < thin_slope and mid_slope < sat_slope else 'NO'}")
        
        # Kruskal-Wallis test for significant difference between groups
        thin_slopes = [r['convergence_slope'] for r in thin]
        mid_slopes = [r['convergence_slope'] for r in mid]
        sat_slopes = [r['convergence_slope'] for r in saturated]
        if len(thin_slopes) > 2 and len(mid_slopes) > 2 and len(sat_slopes) > 2:
            stat, pval = kruskal(thin_slopes, mid_slopes, sat_slopes)
            print(f"  Kruskal-Wallis H={stat:.3f}, p={pval:.4f}")
    
    # OVERALL VERDICT
    print("\n" + "=" * 65)
    print("OVERALL VERDICT")
    print("=" * 65)
    
    all_results = {
        'ipo': ipo_results,
        'crypto': crypto_results,
        'cross_sectional': cross_results
    }
    
    with open('/home/ubuntu/inflection_multimarket_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\nResults saved to /home/ubuntu/inflection_multimarket_results.json")
    
    # Generate comprehensive chart
    generate_comprehensive_chart(ipo_results, crypto_results, cross_results)


def generate_comprehensive_chart(ipo_results, crypto_results, cross_results):
    """Generate a 2x2 chart summarizing all three tests."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#1a1a2e')
    fig.suptitle('Inflection Point Arbitrage Test: Multi-Market Results', 
                 color='white', fontsize=14, fontweight='bold', y=0.98)
    
    colors = ['#e76f51', '#2a9d8f', '#e9c46a']
    zone_labels = ['Thin', 'Inflection', 'Saturated']
    
    # Plot 1: IPO convergence rates
    ax = axes[0, 0]
    ax.set_facecolor('#16213e')
    if ipo_results:
        valid = [r for r in ipo_results if all(r.get(k) is not None for k in ['thin_rate', 'infl_rate', 'satu_rate'])]
        if valid:
            rates = [np.mean([r['thin_rate'] for r in valid]),
                     np.mean([r['infl_rate'] for r in valid]),
                     np.mean([r['satu_rate'] for r in valid])]
            ax.bar(zone_labels, rates, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
            ax.axhline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.set_title('Test 1: IPO-to-Maturity\nConvergence Rate by Zone', color='white', fontsize=10)
    ax.set_ylabel('dSD/dt', color='white')
    ax.tick_params(colors='white')
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['bottom', 'left']: ax.spines[s].set_color('#444')
    
    # Plot 2: Crypto convergence rates
    ax = axes[0, 1]
    ax.set_facecolor('#16213e')
    if crypto_results:
        valid = [r for r in crypto_results if all(r.get(k) is not None for k in ['thin_rate', 'infl_rate', 'satu_rate'])]
        if valid:
            rates = [np.mean([r['thin_rate'] for r in valid]),
                     np.mean([r['infl_rate'] for r in valid]),
                     np.mean([r['satu_rate'] for r in valid])]
            ax.bar(zone_labels, rates, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
            ax.axhline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.set_title('Test 2: Cryptocurrency\nConvergence Rate by Zone', color='white', fontsize=10)
    ax.set_ylabel('dSD/dt', color='white')
    ax.tick_params(colors='white')
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['bottom', 'left']: ax.spines[s].set_color('#444')
    
    # Plot 3: Cross-sectional convergence slopes by volume tercile
    ax = axes[1, 0]
    ax.set_facecolor('#16213e')
    if cross_results:
        sorted_by_vol = sorted(cross_results, key=lambda x: x['avg_volume'])
        n = len(sorted_by_vol)
        t = n // 3
        thin = sorted_by_vol[:t]
        mid = sorted_by_vol[t:2*t]
        sat = sorted_by_vol[2*t:]
        slopes = [np.mean([r['convergence_slope'] for r in thin]),
                  np.mean([r['convergence_slope'] for r in mid]),
                  np.mean([r['convergence_slope'] for r in sat])]
        ax.bar(['Low Vol\n(Thin)', 'Mid Vol\n(Inflection)', 'High Vol\n(Saturated)'],
               slopes, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
        ax.axhline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
    ax.set_title('Test 3: Cross-Sectional (10yr)\nSD Trend Slope by Volume', color='white', fontsize=10)
    ax.set_ylabel('Slope of SD over time', color='white')
    ax.tick_params(colors='white')
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['bottom', 'left']: ax.spines[s].set_color('#444')
    
    # Plot 4: Per-stock rho distribution (all tests combined)
    ax = axes[1, 1]
    ax.set_facecolor('#16213e')
    all_rhos = []
    if ipo_results:
        all_rhos.extend([r['rho'] for r in ipo_results])
    if crypto_results:
        all_rhos.extend([r['rho'] for r in crypto_results])
    if cross_results:
        all_rhos.extend([r['rho'] for r in cross_results])
    
    if all_rhos:
        ax.hist(all_rhos, bins=15, color='#2a9d8f', alpha=0.8, edgecolor='white', linewidth=0.5)
        ax.axvline(0, color='white', linewidth=1, linestyle='--')
        mean_rho = np.mean(all_rhos)
        ax.axvline(mean_rho, color='#e9c46a', linewidth=2, label=f'Mean={mean_rho:.3f}')
        neg_count = sum(1 for r in all_rhos if r < -0.1)
        ax.set_title(f'All Assets: rho(time, SD)\n{neg_count}/{len(all_rhos)} show decreasing volatility', color='white', fontsize=10)
        ax.legend(facecolor='#16213e', edgecolor='#444', labelcolor='white', fontsize=9)
    ax.set_xlabel('Spearman rho', color='white')
    ax.set_ylabel('Count', color='white')
    ax.tick_params(colors='white')
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['bottom', 'left']: ax.spines[s].set_color('#444')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('/home/ubuntu/inflection_multimarket_chart.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print("Chart saved to /home/ubuntu/inflection_multimarket_chart.png")


if __name__ == '__main__':
    print("Running inflection point test across 3 markets...\n")
    
    ipo_results = test_ipo_to_maturity()
    crypto_results = test_crypto_markets()
    cross_results = test_cross_sectional_multiyear()
    
    analyze_and_report(ipo_results, crypto_results, cross_results)
