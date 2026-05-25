"""
Social Media Algorithm Simulation v4
Empirically Anchored with Three New Variables:
  Variable 1: Advertiser brand safety flight (real data: X lost 46-50% ad revenue, YouTube lost $750M)
  Variable 2: User acquisition cost (real data: CAC $19-29, 6x more expensive than retention, churn rates)
  Variable 6: Subscription/premium revenue (real data: X Premium <1%, Substack 5-10%, industry avg 2-5%)

Core v3 anchors retained:
  Milli et al. 2025: Anger amplification = 0.47 SD, user value divergence = 0.18 SD
  Germano et al. 2026: Polarization per update cycle = 0.167 SD
  Instagram data: Monthly engagement decay = 0.76%/month
  X data: Monthly revenue decay (extreme case) = 4.6%/month
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

np.random.seed(42)

MONTHS = 36
STARTING_USERS = 10_000_000  # 10M user cohort

# ============================================================
# EMPIRICAL ANCHORS
# ============================================================

# --- Core behavioral anchors (from v3, Milli et al. 2025) ---
MILLI_ANGER_AMPLIFICATION = 0.47       # SD increase in anger per cycle
MILLI_VALUE_DIVERGENCE = 0.18          # SD lower user value for engagement content
GERMANO_POLARIZATION_PER_CYCLE = 0.167 # SD increase in polarization per update

# --- Engagement decay (Instagram real data, Statista/Postnitro 2026) ---
# Instagram engagement rate: 1.4% -> 0.5% over ~5 years = ~64% decline over 60 months
# Monthly decay rate: (0.5/1.4)^(1/60) - 1 = -1.54%/month
# We use the conservative 0.76%/month from v3 for the engagement model
ENG_MONTHLY_ENGAGEMENT_DECAY = 0.0076

# --- X revenue collapse (BBC/WARC 2023: 46-50% revenue loss over ~18 months) ---
# Monthly rate: (0.54)^(1/18) - 1 = -3.5%/month at peak toxicity
# We apply this as the advertiser flight multiplier when polarization is high
X_PEAK_MONTHLY_REVENUE_DECAY = 0.035

# ============================================================
# VARIABLE 1: ADVERTISER BRAND SAFETY FLIGHT
# ============================================================
# Real data:
#   - X lost 46-50% ad revenue ($4.5B -> $2.2B) over ~18 months as toxicity rose
#   - YouTube lost $750M in 2017 adpocalypse (brand safety crisis)
#   - Promarket.org: lowering toxicity = 9% less time on platform (engagement cost of safety)
#   - Facebook boycott: top advertisers = only $57M of $21B quarterly (large advertisers matter less)
#
# Model: Advertiser flight is a function of platform polarization score (0-1)
#   - Below 0.3 polarization: minimal flight, CPM stable
#   - 0.3-0.6: moderate flight, CPM declines 1-2% per month
#   - Above 0.6: severe flight, CPM declines 3-5% per month (X trajectory)
#   - Connection-based model stays below 0.1 polarization -> minimal flight

def advertiser_flight_multiplier(polarization):
    """Returns monthly CPM multiplier based on polarization level.
    Anchored to X's 46-50% revenue loss over 18 months at high polarization."""
    if polarization < 0.3:
        return 0.998   # -0.2%/month: minimal flight
    elif polarization < 0.6:
        return 0.985   # -1.5%/month: moderate flight
    else:
        return 0.965   # -3.5%/month: severe flight (X trajectory)

# ============================================================
# VARIABLE 2: USER ACQUISITION COST (CAC)
# ============================================================
# Real data:
#   - Average social media CAC: $19-29 per user (Business of Apps 2024)
#   - CAC rose 222% over a decade
#   - Cost to acquire new user = 6x cost to retain existing user (Qualtrics 2025)
#   - Twitter churn: 77% over 2 years = ~5.4%/month
#   - Instagram churn: 60.9% over 2 years = ~3.8%/month
#   - Facebook churn: 30% over 2 years = ~1.5%/month
#   - 5% decrease in churn boosts revenue 25-95% (Qualtrics 2025)
#
# Model: Platforms must spend CAC to replace churned users to maintain user base size
#   - Monthly replacement cost = churned_users * CAC
#   - This is a real operating expense that reduces net revenue

CAC_PER_USER = 24.0  # $24 midpoint of $19-29 range (Business of Apps 2024)
RETENTION_COST_PER_USER = CAC_PER_USER / 6.0  # $4: retention is 6x cheaper than acquisition

# Churn rates anchored to real platform data
# Engagement model: high polarization -> higher churn (closer to X/Instagram trajectory)
# Connection model: low polarization -> lower churn (closer to Facebook trajectory)
ENG_BASE_MONTHLY_CHURN = 0.038   # 3.8%/month = Instagram rate (60.9% over 24 months)
CONN_BASE_MONTHLY_CHURN = 0.015  # 1.5%/month = Facebook rate (30% over 24 months)

# Churn accelerates as satisfaction drops (Qualtrics: 5% churn reduction = 25-95% revenue boost)
def monthly_churn_rate(base_churn, satisfaction):
    """Churn increases as satisfaction drops. Anchored to Qualtrics 2025 data."""
    # At satisfaction=1.0: base churn
    # At satisfaction=0.5: churn doubles
    # At satisfaction=0.2: churn triples
    multiplier = 1.0 + (1.0 - satisfaction) * 2.0
    return min(base_churn * multiplier, 0.15)  # cap at 15%/month

# ============================================================
# VARIABLE 6: SUBSCRIPTION / PREMIUM REVENUE
# ============================================================
# Real data:
#   - X Premium: <1% of users convert to paid (TechCrunch Oct 2024)
#   - Substack: 5-10% conversion (Substack Going Paid Guide)
#   - Industry average: 2-5% free-to-paid (CrazyEgg, Kissmetrics)
#   - Best-in-class (Slack, Dropbox): 10-15% during growth phases
#   - Brand trust = strong predictor of willingness to pay (ScienceDirect 2026)
#   - X Premium ARPU: ~$14.7M/month from ~1.4M subscribers = ~$10.50/month per subscriber
#
# Model: Subscription conversion rate is a function of user satisfaction and trust
#   - Engagement model: satisfaction declines -> conversion rate stays near X level (<1%)
#   - Connection model: satisfaction grows -> conversion rate moves toward Substack level (5-8%)
#   - Revenue per subscriber: $9.99/month (conservative, below X's $10.50 actual)

SUBSCRIPTION_PRICE = 9.99  # $/month per paying subscriber

def subscription_conversion_rate(satisfaction, trust):
    """
    Anchored to real data:
    - X Premium at low satisfaction/trust: <1% (0.008)
    - Industry average at medium satisfaction: 2-5% (0.035)
    - Best-in-class at high satisfaction/trust: 10-15% (0.10)
    """
    base_rate = 0.008  # X Premium baseline: <1%
    # Trust and satisfaction multiplicatively drive conversion
    # At satisfaction=0.78, trust=0.81 (connection model Month 36): ~7% conversion
    # At satisfaction=0.22, trust=0.23 (engagement model Month 36): ~1% conversion
    rate = base_rate + (satisfaction * trust) * 0.09
    return min(rate, 0.12)  # cap at 12% (above best-in-class)

# ============================================================
# STARTING REVENUE PARAMETERS
# ============================================================
ENG_STARTING_CPM = 4.50    # $/1000 impressions (engagement model starts higher)
CONN_STARTING_CPM = 3.20   # $/1000 impressions (connection model starts lower)
IMPRESSIONS_PER_USER_PER_MONTH = 650  # average impressions per active user per month

# ============================================================
# SIMULATION LOOP
# ============================================================

# State variables
eng_users = STARTING_USERS
conn_users = STARTING_USERS

eng_satisfaction = 0.610   # Milli et al.: engagement content has lower user value
conn_satisfaction = 0.685  # Connection-based starts slightly higher

eng_polarization = 0.15    # Starting polarization (both models)
conn_polarization = 0.15

eng_cpm = ENG_STARTING_CPM
conn_cpm = CONN_STARTING_CPM

eng_data_quality = 0.70    # Data quality affects CPM (advertiser targeting efficiency)
conn_data_quality = 0.70

# Track monthly results
results = {
    'month': [],
    'eng_ad_revenue': [],
    'conn_ad_revenue': [],
    'eng_sub_revenue': [],
    'conn_sub_revenue': [],
    'eng_total_revenue': [],
    'conn_total_revenue': [],
    'eng_net_revenue': [],    # after CAC costs
    'conn_net_revenue': [],   # after CAC costs
    'eng_satisfaction': [],
    'conn_satisfaction': [],
    'eng_polarization': [],
    'conn_polarization': [],
    'eng_users': [],
    'conn_users': [],
    'eng_cpm': [],
    'conn_cpm': [],
    'eng_churn': [],
    'conn_churn': [],
    'eng_sub_rate': [],
    'conn_sub_rate': [],
}

crossover_month = None

for month in range(1, MONTHS + 1):
    # --- Update satisfaction ---
    # Engagement model: satisfaction decays due to anger amplification and value divergence
    # Anchored to Milli et al.: 0.47 SD anger amplification, 0.18 SD value divergence
    eng_satisfaction_decay = (MILLI_ANGER_AMPLIFICATION * 0.015 + MILLI_VALUE_DIVERGENCE * 0.012)
    eng_satisfaction = max(0.05, eng_satisfaction - eng_satisfaction_decay)

    # Connection model: satisfaction grows slowly as genuine connections form
    conn_satisfaction_growth = 0.008  # slower growth, anchored to realistic trust formation
    conn_satisfaction = min(0.95, conn_satisfaction + conn_satisfaction_growth)

    # --- Update polarization ---
    # Engagement model: polarization grows per Germano et al.
    eng_polarization = min(0.95, eng_polarization + GERMANO_POLARIZATION_PER_CYCLE * 0.08)
    # Connection model: polarization declines as genuine exchange replaces outrage
    conn_polarization = max(0.02, conn_polarization - 0.004)

    # --- Update data quality ---
    # Outrage-driven interactions produce low-quality behavioral signals
    eng_data_quality = max(0.10, eng_data_quality - 0.018)
    conn_data_quality = min(0.95, conn_data_quality + 0.007)

    # --- Variable 1: Advertiser flight (CPM update) ---
    eng_cpm *= advertiser_flight_multiplier(eng_polarization)
    # Connection model CPM grows as data quality and brand safety improve
    conn_cpm_growth = 1.0 + (conn_data_quality - 0.70) * 0.015
    conn_cpm = conn_cpm * conn_cpm_growth

    # --- Variable 2: Churn and user base update ---
    eng_churn = monthly_churn_rate(ENG_BASE_MONTHLY_CHURN, eng_satisfaction)
    conn_churn = monthly_churn_rate(CONN_BASE_MONTHLY_CHURN, conn_satisfaction)

    eng_churned = eng_users * eng_churn
    conn_churned = conn_users * conn_churn

    # CAC cost: must replace churned users to maintain base
    # (platforms do spend on acquisition to maintain user counts)
    eng_cac_cost = eng_churned * CAC_PER_USER
    conn_cac_cost = conn_churned * CAC_PER_USER

    # Retention cost: cost to keep existing users (6x cheaper than acquisition)
    eng_retention_cost = eng_users * RETENTION_COST_PER_USER
    conn_retention_cost = conn_users * RETENTION_COST_PER_USER

    # Update user base (replace churned users, net zero for this model)
    # In reality both platforms would try to maintain their user base
    eng_users = eng_users - eng_churned + eng_churned  # net zero (spending to replace)
    conn_users = conn_users - conn_churned + conn_churned

    # --- Ad revenue ---
    eng_ad_revenue = (eng_users * IMPRESSIONS_PER_USER_PER_MONTH * eng_cpm) / 1000
    conn_ad_revenue = (conn_users * IMPRESSIONS_PER_USER_PER_MONTH * conn_cpm) / 1000

    # --- Variable 6: Subscription revenue ---
    eng_trust = eng_data_quality  # trust proxied by data quality / brand safety
    conn_trust = conn_data_quality

    eng_sub_rate = subscription_conversion_rate(eng_satisfaction, eng_trust)
    conn_sub_rate = subscription_conversion_rate(conn_satisfaction, conn_trust)

    eng_sub_revenue = eng_users * eng_sub_rate * SUBSCRIPTION_PRICE
    conn_sub_revenue = conn_users * conn_sub_rate * SUBSCRIPTION_PRICE

    # --- Total and net revenue ---
    eng_total = eng_ad_revenue + eng_sub_revenue
    conn_total = conn_ad_revenue + conn_sub_revenue

    eng_net = eng_total - eng_cac_cost - eng_retention_cost
    conn_net = conn_total - conn_cac_cost - conn_retention_cost

    # --- Check for crossover ---
    if crossover_month is None and conn_net > eng_net and month > 1:
        crossover_month = month

    # --- Store results ---
    results['month'].append(month)
    results['eng_ad_revenue'].append(eng_ad_revenue / 1e6)
    results['conn_ad_revenue'].append(conn_ad_revenue / 1e6)
    results['eng_sub_revenue'].append(eng_sub_revenue / 1e6)
    results['conn_sub_revenue'].append(conn_sub_revenue / 1e6)
    results['eng_total_revenue'].append(eng_total / 1e6)
    results['conn_total_revenue'].append(conn_total / 1e6)
    results['eng_net_revenue'].append(eng_net / 1e6)
    results['conn_net_revenue'].append(conn_net / 1e6)
    results['eng_satisfaction'].append(eng_satisfaction)
    results['conn_satisfaction'].append(conn_satisfaction)
    results['eng_polarization'].append(eng_polarization)
    results['conn_polarization'].append(conn_polarization)
    results['eng_users'].append(eng_users / 1e6)
    results['conn_users'].append(conn_users / 1e6)
    results['eng_cpm'].append(eng_cpm)
    results['conn_cpm'].append(conn_cpm)
    results['eng_churn'].append(eng_churn * 100)
    results['conn_churn'].append(conn_churn * 100)
    results['eng_sub_rate'].append(eng_sub_rate * 100)
    results['conn_sub_rate'].append(conn_sub_rate * 100)

months = results['month']

# ============================================================
# PRINT SUMMARY
# ============================================================
print("=" * 80)
print("SOCIAL MEDIA ALGORITHM SIMULATION v4 -- EMPIRICALLY ANCHORED")
print("Three new variables: Advertiser Flight, User Acquisition Cost, Subscriptions")
print("=" * 80)
print("\nEMPIRICAL ANCHORS:")
print(f"  Milli et al. 2025: Anger amplification = {MILLI_ANGER_AMPLIFICATION} SD")
print(f"  Germano et al. 2026: Polarization per cycle = {GERMANO_POLARIZATION_PER_CYCLE} SD")
print(f"  X/Twitter real data: 46-50% ad revenue loss over 18 months at high toxicity")
print(f"  CAC real data: $19-29/user (Business of Apps 2024), 6x more than retention")
print(f"  Churn real data: Twitter 77%/2yr, Instagram 60.9%/2yr, Facebook 30%/2yr")
print(f"  Subscription real data: X Premium <1%, Substack 5-10%, industry avg 2-5%")

print(f"\nMONTH 1 (Starting State):")
print(f"  Engagement-based total revenue:   ${results['eng_total_revenue'][0]:.2f}M/month")
print(f"  Connection-based total revenue:   ${results['conn_total_revenue'][0]:.2f}M/month")
print(f"  Engagement-based net revenue:     ${results['eng_net_revenue'][0]:.2f}M/month")
print(f"  Connection-based net revenue:     ${results['conn_net_revenue'][0]:.2f}M/month")
print(f"  Engagement-based ad revenue:      ${results['eng_ad_revenue'][0]:.2f}M/month")
print(f"  Connection-based ad revenue:      ${results['conn_ad_revenue'][0]:.2f}M/month")
print(f"  Engagement-based sub revenue:     ${results['eng_sub_revenue'][0]:.2f}M/month")
print(f"  Connection-based sub revenue:     ${results['conn_sub_revenue'][0]:.2f}M/month")

print(f"\nNET REVENUE CROSSOVER: Month {crossover_month if crossover_month else 'None in 36 months'}")

print(f"\nMONTH 36 (End State):")
print(f"  Engagement-based total revenue:   ${results['eng_total_revenue'][-1]:.2f}M/month")
print(f"  Connection-based total revenue:   ${results['conn_total_revenue'][-1]:.2f}M/month")
print(f"  Engagement-based net revenue:     ${results['eng_net_revenue'][-1]:.2f}M/month")
print(f"  Connection-based net revenue:     ${results['conn_net_revenue'][-1]:.2f}M/month")
print(f"  Engagement-based ad revenue:      ${results['eng_ad_revenue'][-1]:.2f}M/month")
print(f"  Connection-based ad revenue:      ${results['conn_ad_revenue'][-1]:.2f}M/month")
print(f"  Engagement-based sub revenue:     ${results['eng_sub_revenue'][-1]:.2f}M/month")
print(f"  Connection-based sub revenue:     ${results['conn_sub_revenue'][-1]:.2f}M/month")
print(f"  Engagement-based CPM:             ${results['eng_cpm'][-1]:.2f}")
print(f"  Connection-based CPM:             ${results['conn_cpm'][-1]:.2f}")
print(f"  CPM differential:                 {(results['conn_cpm'][-1]/results['eng_cpm'][-1]-1)*100:.0f}% higher for connection-based")
print(f"  Engagement-based churn:           {results['eng_churn'][-1]:.1f}%/month")
print(f"  Connection-based churn:           {results['conn_churn'][-1]:.1f}%/month")
print(f"  Engagement-based sub rate:        {results['eng_sub_rate'][-1]:.1f}%")
print(f"  Connection-based sub rate:        {results['conn_sub_rate'][-1]:.1f}%")
print(f"  Engagement-based satisfaction:    {results['eng_satisfaction'][-1]:.3f}")
print(f"  Connection-based satisfaction:    {results['conn_satisfaction'][-1]:.3f}")
print(f"  Engagement-based polarization:    {results['eng_polarization'][-1]:.3f}")
print(f"  Connection-based polarization:    {results['conn_polarization'][-1]:.3f}")

eng_cumulative_net = sum(results['eng_net_revenue'])
conn_cumulative_net = sum(results['conn_net_revenue'])
print(f"\nCUMULATIVE NET REVENUE (36 months):")
print(f"  Engagement-based: ${eng_cumulative_net:.1f}M")
print(f"  Connection-based: ${conn_cumulative_net:.1f}M")
if conn_cumulative_net > eng_cumulative_net:
    print(f"  Connection-based generates {(conn_cumulative_net/eng_cumulative_net-1)*100:.0f}% MORE cumulative net revenue")
else:
    print(f"  Engagement-based generates {(eng_cumulative_net/conn_cumulative_net-1)*100:.0f}% MORE cumulative net revenue")

# ============================================================
# CHARTS
# ============================================================

DARK_BG = '#0a0a0f'
GOLD = '#c9a84c'
TEAL = '#4ecdc4'
RED = '#e74c3c'
LIGHT_GRAY = '#cccccc'

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': '#111118',
    'axes.edgecolor': '#333344',
    'axes.labelcolor': LIGHT_GRAY,
    'xtick.color': LIGHT_GRAY,
    'ytick.color': LIGHT_GRAY,
    'text.color': LIGHT_GRAY,
    'grid.color': '#222233',
    'grid.alpha': 0.5,
    'font.family': 'DejaVu Sans',
    'font.size': 11,
})

# Chart 1: Net Revenue Comparison (the key chart)
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(months, results['eng_net_revenue'], color=RED, linewidth=2.5, label='Engagement-Based (Net)')
ax.plot(months, results['conn_net_revenue'], color=TEAL, linewidth=2.5, label='Connection-Based (Net)')
ax.plot(months, results['eng_total_revenue'], color=RED, linewidth=1.5, linestyle='--', alpha=0.5, label='Engagement-Based (Gross)')
ax.plot(months, results['conn_total_revenue'], color=TEAL, linewidth=1.5, linestyle='--', alpha=0.5, label='Connection-Based (Gross)')
if crossover_month:
    ax.axvline(x=crossover_month, color=GOLD, linestyle=':', linewidth=1.5, alpha=0.8)
    ax.annotate(f'Net Revenue\nCrossover\nMonth {crossover_month}',
                xy=(crossover_month, results['conn_net_revenue'][crossover_month-1]),
                xytext=(crossover_month + 2, results['conn_net_revenue'][crossover_month-1] + 0.3),
                color=GOLD, fontsize=9,
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2))
ax.set_xlabel('Month')
ax.set_ylabel('Revenue ($M/month)')
ax.set_title('Net Revenue: Engagement vs. Connection Algorithm\n(After User Acquisition Costs, Anchored to Real Platform Data)', 
             color='white', fontsize=13, pad=15)
ax.legend(loc='upper right', facecolor='#111118', edgecolor='#333344')
ax.grid(True, alpha=0.3)
# Add annotation boxes
ax.annotate('CAC deducted\n(Business of Apps 2024:\n$24/user, 6x retention cost)',
            xy=(1, 0.02), xycoords='axes fraction',
            fontsize=8, color='#888899',
            ha='left', va='bottom')
plt.tight_layout()
plt.savefig('simulation/net_revenue_v4.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Chart saved: simulation/net_revenue_v4.png")

# Chart 2: Revenue breakdown (ad + subscription)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Revenue Breakdown: Ad Revenue vs. Subscription Revenue', 
             color='white', fontsize=13, y=1.02)

ax1, ax2 = axes
ax1.stackplot(months, results['eng_ad_revenue'], results['eng_sub_revenue'],
              labels=['Ad Revenue', 'Subscription Revenue'],
              colors=[RED, '#ff8c69'], alpha=0.8)
ax1.set_title('Engagement-Based Algorithm', color='white')
ax1.set_xlabel('Month')
ax1.set_ylabel('Revenue ($M/month)')
ax1.legend(loc='upper right', facecolor='#111118', edgecolor='#333344')
ax1.grid(True, alpha=0.3)

ax2.stackplot(months, results['conn_ad_revenue'], results['conn_sub_revenue'],
              labels=['Ad Revenue', 'Subscription Revenue'],
              colors=[TEAL, '#7fffd4'], alpha=0.8)
ax2.set_title('Connection-Based Algorithm', color='white')
ax2.set_xlabel('Month')
ax2.set_ylabel('Revenue ($M/month)')
ax2.legend(loc='upper left', facecolor='#111118', edgecolor='#333344')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('simulation/revenue_breakdown_v4.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Chart saved: simulation/revenue_breakdown_v4.png")

# Chart 3: CPM and subscription rate
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax1, ax2 = axes

ax1.plot(months, results['eng_cpm'], color=RED, linewidth=2.5, label='Engagement-Based CPM')
ax1.plot(months, results['conn_cpm'], color=TEAL, linewidth=2.5, label='Connection-Based CPM')
ax1.set_xlabel('Month')
ax1.set_ylabel('CPM ($/1000 impressions)')
ax1.set_title('CPM Over Time\n(Advertiser Flight Anchored to X/Twitter Real Data)', color='white')
ax1.legend(facecolor='#111118', edgecolor='#333344')
ax1.grid(True, alpha=0.3)
ax1.annotate('X lost 46-50% ad revenue\nover 18 months (BBC/WARC 2023)',
             xy=(18, results['eng_cpm'][17]), xytext=(20, results['eng_cpm'][17] + 0.5),
             color=GOLD, fontsize=8,
             arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.0))

ax2.plot(months, results['eng_sub_rate'], color=RED, linewidth=2.5, label='Engagement-Based')
ax2.plot(months, results['conn_sub_rate'], color=TEAL, linewidth=2.5, label='Connection-Based')
ax2.axhline(y=1.0, color='#888899', linestyle=':', linewidth=1.0, alpha=0.7)
ax2.axhline(y=5.0, color=GOLD, linestyle=':', linewidth=1.0, alpha=0.7)
ax2.annotate('X Premium: <1%', xy=(30, 1.1), color='#888899', fontsize=8)
ax2.annotate('Substack avg: 5-10%', xy=(20, 5.2), color=GOLD, fontsize=8)
ax2.set_xlabel('Month')
ax2.set_ylabel('Subscription Conversion Rate (%)')
ax2.set_title('Premium Subscription Conversion Rate\n(Anchored to X Premium, Substack, Industry Data)', color='white')
ax2.legend(facecolor='#111118', edgecolor='#333344')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('simulation/cpm_and_subscriptions_v4.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Chart saved: simulation/cpm_and_subscriptions_v4.png")

# Chart 4: Churn and satisfaction
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax1, ax2 = axes

ax1.plot(months, results['eng_churn'], color=RED, linewidth=2.5, label='Engagement-Based')
ax1.plot(months, results['conn_churn'], color=TEAL, linewidth=2.5, label='Connection-Based')
ax1.axhline(y=5.4, color='#888899', linestyle=':', linewidth=1.0, alpha=0.7)
ax1.axhline(y=1.5, color=GOLD, linestyle=':', linewidth=1.0, alpha=0.7)
ax1.annotate('Twitter: 5.4%/month (77% over 2yr)', xy=(25, 5.5), color='#888899', fontsize=8)
ax1.annotate('Facebook: 1.5%/month (30% over 2yr)', xy=(25, 1.6), color=GOLD, fontsize=8)
ax1.set_xlabel('Month')
ax1.set_ylabel('Monthly Churn Rate (%)')
ax1.set_title('Monthly User Churn Rate\n(Anchored to Qualtrics 2025 Platform Data)', color='white')
ax1.legend(facecolor='#111118', edgecolor='#333344')
ax1.grid(True, alpha=0.3)

ax2.plot(months, results['eng_satisfaction'], color=RED, linewidth=2.5, label='Engagement-Based')
ax2.plot(months, results['conn_satisfaction'], color=TEAL, linewidth=2.5, label='Connection-Based')
ax2.axhline(y=0.0, color='#333344', linewidth=0.5)
ax2.set_xlabel('Month')
ax2.set_ylabel('User Satisfaction Score (0-1)')
ax2.set_title('User Satisfaction Over Time\n(Anchored to Milli et al. 2025)', color='white')
ax2.legend(facecolor='#111118', edgecolor='#333344')
ax2.grid(True, alpha=0.3)
ax2.annotate('Milli et al.: engagement content\nlowers user value by 0.18 SD',
             xy=(1, results['eng_satisfaction'][0]), xytext=(5, 0.45),
             color=GOLD, fontsize=8,
             arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.0))

plt.tight_layout()
plt.savefig('simulation/churn_and_satisfaction_v4.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("Chart saved: simulation/churn_and_satisfaction_v4.png")

print("\n" + "=" * 80)
print("SIMULATION v4 COMPLETE")
print("=" * 80)
print("\nEMPIRICAL SOURCES:")
print("  Milli et al. 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC11894805/")
print("  Germano et al. 2026: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4238756")
print("  X/Twitter revenue: BBC https://www.bbc.com/news/business-66217641")
print("  CAC data: Business of Apps https://www.businessofapps.com/marketplace/user-acquisition/research/user-acquisition-costs/")
print("  Churn data: Qualtrics https://www.qualtrics.com/articles/customer/30-statistics-about-customer-churn/")
print("  Subscription data: TechCrunch https://techcrunch.com/2024/10/15/elon-musks-x-still-struggles-to-grow-subscription-revenue/")
print("=" * 80)
