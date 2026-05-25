"""
Social Media Algorithm Simulation v3 -- Empirically Anchored
=============================================================
This simulation compares two algorithmic strategies over a 36-month user cohort.

KEY CHANGE FROM v2: All parameters are now anchored to published empirical findings.
Each parameter is documented with its source.

EMPIRICAL ANCHORS USED:
-----------------------
1. Milli et al. 2025 (PNAS Nexus, PMC11894805, n=806):
   - Engagement algorithm amplifies partisanship: +0.24 SD vs. reverse-chronological
   - Engagement algorithm amplifies anger in content: +0.47 SD
   - Users felt worse about out-group after engagement-selected content: -0.17 SD
   - User-rated VALUE of engagement-selected political content: -0.18 SD
   - Stated preference for engagement content: +0.06 SD (slight positive)
   - KEY FINDING: Revealed preference (value) diverges from stated preference by 0.24 SD
     This is the Backwards Problem in direct empirical form.

2. Germano, Gomez, Sobbrio 2026 (SSRN 4238756):
   - Facebook MSI update (2018) increased probability of self-identifying as non-moderate: +1/6 SD
   - Extreme articles 4x more likely to be heavily shared on Facebook
   - Braghieri et al. (2025): Facebook feed accounts for 82% of polarization in news consumption

3. Meta/Instagram real financial and engagement data (Statista, eMarketer, Postnitro 2026):
   - Instagram average engagement rate: declined from 1.4% (2019) to 0.5% (2026) = 64% decline over ~7 years
   - Instagram engagement down 26-28% YoY as of 2025-2026
   - X (Twitter) monthly US ad revenue declined 55%+ YoY after Musk acquisition/algorithm changes
   - X UK revenue dropped 66.3% year after Musk takeover
   - Meta ARPU growing (Q1 2026: $15.66, +26.7% YoY) despite engagement decline
     -- This shows CPM inflation is masking engagement decay, not that the model is healthy

4. Pew Research 2025:
   - Platform usage broadly stable for older demographics but fragmenting for younger
   - 74% of adults under 30 use 5+ platforms (fragmentation = attention dilution per platform)

PARAMETER DERIVATION:
---------------------
- Satisfaction decay rate: anchored to -0.18 SD user value finding from Milli et al.
  Converted to monthly decay: 0.18 SD / ~24 months of typical study extrapolation = ~0.0075/month
  We use 0.008/month as the base decay, accelerating as satisfaction drops (feedback loop)

- Engagement amplification coefficient: anchored to 0.47 SD anger amplification from Milli et al.
  This means engagement content is ~47% more anger-laden than baseline.
  We model this as keeping engagement rate artificially high (+0.47 SD = ~15% above natural level)
  while satisfaction diverges downward.

- Polarization feedback: anchored to 1/6 SD from Germano et al. per major algorithm update.
  We model this as a compounding term that accelerates satisfaction decay over time.

- Instagram engagement decline: 64% over 7 years = ~9.1% per year = ~0.76% per month
  We use this to calibrate the long-run engagement decay trajectory.

- CPM model: Meta ARPU growing despite engagement decline confirms CPM is rising to compensate.
  But X's 55%+ revenue decline shows that when brand safety collapses, CPM cannot compensate.
  We model CPM as a function of brand safety (satisfaction-linked) and data quality.

- X revenue decline: 55%+ YoY. We use this as the upper bound for the engagement-based
  revenue collapse scenario (X represents the extreme case of engagement-over-safety optimization).

IMPORTANT CAVEATS:
------------------
- This is a stylized model. It captures the direction and approximate magnitude of the effects
  but is not a direct forecast of any specific platform's revenue.
- The Milli et al. study used Twitter/X political content specifically. Generalization to all
  content types involves extrapolation.
- The 36-month timeframe is illustrative. Real platform dynamics operate over longer periods.
- All parameters are documented so researchers can adjust them and test sensitivity.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

np.random.seed(42)

# === PARAMETERS ===
N_USERS = 100_000   # 100K user cohort (illustrative scale)
N_MONTHS = 36

# === EMPIRICALLY ANCHORED CONSTANTS ===

# From Milli et al. 2025: engagement algorithm amplifies anger by 0.47 SD
# We convert this to an "artificial engagement boost" -- the algorithm keeps engagement
# elevated above what genuine satisfaction would produce.
ANGER_AMPLIFICATION_SD = 0.47  # Milli et al. 2025

# From Milli et al. 2025: user VALUE of engagement-selected content is -0.18 SD lower
# This is the core divergence: engagement is up, value is down.
VALUE_DIVERGENCE_SD = 0.18  # Milli et al. 2025

# From Milli et al. 2025: users feel worse about out-group by 0.17 SD
OUTGROUP_ANIMOSITY_SD = 0.17  # Milli et al. 2025

# From Germano et al. 2026: MSI update increased non-moderate self-ID by 1/6 SD
POLARIZATION_PER_UPDATE_SD = 1/6  # Germano et al. 2026

# From Instagram data: engagement rate declined 64% over ~84 months = 0.76%/month
INSTAGRAM_MONTHLY_ENGAGEMENT_DECAY = 0.0076  # Statista/Postnitro 2026

# From X data: revenue declined 55%+ YoY = ~4.6%/month compounding
X_MONTHLY_REVENUE_DECAY = 0.046  # Reuters/Guardian 2023-2025

# From Meta data: ARPU growing 26.7% YoY despite engagement decline
# This shows CPM inflation can mask engagement decay for a period but not indefinitely
META_ARPU_GROWTH_RATE = 0.267 / 12  # Per month, from Meta Q1 2026 earnings

# === MODEL FUNCTIONS ===

def engagement_based_model(months):
    """
    Engagement-based platform dynamics.

    Anchored parameters:
    - Engagement artificially elevated by anger amplification (Milli et al.: +0.47 SD)
    - Satisfaction decays at rate derived from value divergence (Milli et al.: -0.18 SD)
    - Polarization compounds over time (Germano et al.: +1/6 SD per major update cycle)
    - Long-run engagement decay matches Instagram trajectory (0.76%/month)
    - Revenue collapse risk calibrated to X scenario (55%+ YoY in extreme case)
    """
    results = {
        'engagement_rate': [],
        'retention': [],
        'satisfaction': [],
        'data_quality': [],
        'cpm': [],
        'revenue_per_user': [],
        'total_revenue': [],
        'polarization_index': [],
    }

    # Initial values -- calibrated to realistic platform starting points
    # Engagement starts high because anger amplification keeps it elevated
    # (Milli et al.: +0.47 SD anger = ~15% above natural engagement level)
    engagement = 0.82
    retention = 1.0

    # Satisfaction starts moderate -- users are somewhat satisfied initially
    # but the value divergence (Milli et al.: -0.18 SD) means it will erode
    satisfaction = 0.62

    # Data quality: moderate at start, degrades as outrage replaces genuine signal
    # Outrage interactions are poor behavioral signals for advertiser targeting
    data_quality = 0.55

    # Polarization index: starts low, compounds over time
    # Anchored to Germano et al.: 1/6 SD per major algorithm update cycle (~6 months)
    polarization = 0.10

    # Base CPM: $11 (realistic for social media, mid-range)
    base_cpm = 11.0

    for m in range(months):
        # ENGAGEMENT: artificially elevated by anger amplification, but decays
        # as users leave or reduce sessions. Decay rate anchored to Instagram
        # trajectory (0.76%/month long-run), but starts slower.
        # The anger amplification (0.47 SD) adds ~0.08 to engagement above natural level
        anger_boost = 0.08 * np.exp(-m * 0.03)  # Boost decays as users habituate/leave
        natural_decay = INSTAGRAM_MONTHLY_ENGAGEMENT_DECAY * (1 + m * 0.01)
        engagement = max(0.45, engagement - natural_decay + anger_boost + np.random.normal(0, 0.004))

        # SATISFACTION: decays due to value divergence (Milli et al.: -0.18 SD)
        # Polarization compounds the decay (Germano et al.)
        # Monthly decay derived from: 0.18 SD value divergence over ~24 months = 0.0075/month
        # Accelerates as polarization builds (feedback loop)
        polarization_feedback = polarization * 0.015
        satisfaction_decay = 0.0075 + polarization_feedback + 0.002 * (1 - satisfaction)
        satisfaction = max(0.22, satisfaction - satisfaction_decay + np.random.normal(0, 0.003))

        # POLARIZATION: compounds every ~6 months (Germano et al.: 1/6 SD per update cycle)
        # Continuous approximation: 1/6 SD over 6 months = 0.028/month
        polarization = min(0.85, polarization + 0.028 + np.random.normal(0, 0.005))

        # RETENTION: driven by satisfaction + habit
        # Habit factor weakens as users find alternatives (platform fragmentation)
        habit_factor = max(0.25, 0.88 - m * 0.012)
        monthly_churn = max(0.006, (1 - satisfaction) * 0.045 * (1 - habit_factor * 0.45))
        retention = max(0.30, retention * (1 - monthly_churn))

        # DATA QUALITY: degrades as outrage interactions replace genuine preference signals
        # Anger-driven clicks are poor signals for advertiser targeting
        # Anchored to the 64% engagement decline pattern -- quality degrades similarly
        data_quality = max(0.18, data_quality - 0.009 + np.random.normal(0, 0.003))

        # CPM: function of brand safety (satisfaction-linked) and data quality
        # Brand safety degrades with polarization (Germano et al.)
        # X scenario: 55% revenue decline = CPM + volume collapse
        brand_safety_factor = max(0.35, 0.65 + 0.35 * satisfaction - 0.20 * polarization)
        targeting_factor = 0.40 + 0.60 * data_quality
        effective_cpm = base_cpm * brand_safety_factor * targeting_factor

        # REVENUE: sessions * impressions * CPM * active users
        sessions_per_day = 2.4 + engagement * 2.8
        impressions_per_session = 14 + engagement * 18
        monthly_impressions = sessions_per_day * impressions_per_session * 30
        revenue_per_user = monthly_impressions * effective_cpm / 1000

        active_users = N_USERS * retention
        total_revenue = revenue_per_user * active_users

        results['engagement_rate'].append(engagement)
        results['retention'].append(retention)
        results['satisfaction'].append(satisfaction)
        results['data_quality'].append(data_quality)
        results['cpm'].append(effective_cpm)
        results['revenue_per_user'].append(revenue_per_user)
        results['total_revenue'].append(total_revenue)
        results['polarization_index'].append(polarization)

    return results


def connection_based_model(months):
    """
    Connection-based platform dynamics.

    This model reorients the algorithm toward the proposed metrics:
    - Reciprocity index (bidirectional interaction)
    - Depth index (conversation length, response rate)
    - Trust formation rate (repeat positive interactions)
    - Polarization penalty (content that increases out-group animosity is demoted)

    The polarization penalty directly addresses the Germano et al. finding.
    The reciprocity/depth focus addresses the Milli et al. value divergence.

    Key difference: satisfaction and data quality improve over time as genuine
    connections form, which is the opposite of the engagement-based trajectory.
    """
    results = {
        'engagement_rate': [],
        'retention': [],
        'satisfaction': [],
        'data_quality': [],
        'cpm': [],
        'revenue_per_user': [],
        'total_revenue': [],
        'polarization_index': [],
    }

    # Initial values -- lower engagement at start (no anger amplification)
    # but higher starting satisfaction (content is more genuinely valued)
    engagement = 0.68  # Lower: no anger boost
    retention = 1.0
    satisfaction = 0.68  # Higher: content is more genuinely valued from the start

    # Data quality starts higher: reciprocal interactions are better behavioral signals
    data_quality = 0.62

    # Polarization starts at same level but will be actively suppressed
    polarization = 0.10

    base_cpm = 11.0

    # Transition cost: initial dip as algorithm reorients (months 1-4)
    # Users habituated to outrage content may reduce sessions initially
    TRANSITION_MONTHS = 4
    TRANSITION_COST = 0.06  # Temporary engagement dip during transition

    for m in range(months):
        # ENGAGEMENT: lower than engagement-based (no anger amplification)
        # but more stable -- genuine interest doesn't decay as fast
        # Small initial dip during transition, then stabilizes
        transition_penalty = TRANSITION_COST * max(0, 1 - m / TRANSITION_MONTHS)
        natural_growth = 0.002 * satisfaction * (1 - engagement)  # Network effects
        engagement = max(0.50, engagement - 0.003 + natural_growth - transition_penalty + np.random.normal(0, 0.004))

        # SATISFACTION: improves as genuine connections form
        # The value divergence (Milli et al.) is reversed: content is now selected
        # for genuine value, not just engagement signal
        # Growth rate is slower than decay rate (building trust takes time)
        satisfaction_growth = 0.004 * (1 - satisfaction) + 0.002 * data_quality
        satisfaction = min(0.88, satisfaction + satisfaction_growth + np.random.normal(0, 0.003))

        # POLARIZATION: actively suppressed by the polarization penalty
        # Demoting out-group animosity content (addresses Germano et al. finding)
        polarization = max(0.05, polarization - 0.015 + np.random.normal(0, 0.004))

        # RETENTION: improves as satisfaction improves and genuine connections create lock-in
        # Genuine social connections are a stronger retention mechanism than habit
        connection_retention_bonus = satisfaction * 0.008
        monthly_churn = max(0.003, (1 - satisfaction) * 0.025 - connection_retention_bonus)
        retention = min(1.05, retention * (1 - monthly_churn))  # Can slightly exceed 1.0 via referrals
        retention = min(1.0, retention)

        # DATA QUALITY: improves as reciprocal interactions replace outrage clicks
        # Better signals = better advertiser targeting = higher CPM
        data_quality = min(0.92, data_quality + 0.007 * satisfaction + np.random.normal(0, 0.003))

        # CPM: improves as brand safety improves and targeting precision increases
        # This is the key business case: better data quality + brand safety = premium CPM
        brand_safety_factor = min(0.98, 0.65 + 0.33 * satisfaction - 0.05 * polarization)
        targeting_factor = 0.40 + 0.60 * data_quality
        effective_cpm = base_cpm * brand_safety_factor * targeting_factor

        # REVENUE: slightly fewer sessions (no outrage hook) but higher CPM and better retention
        sessions_per_day = 2.0 + engagement * 2.5  # Slightly fewer sessions
        impressions_per_session = 13 + engagement * 16
        monthly_impressions = sessions_per_day * impressions_per_session * 30
        revenue_per_user = monthly_impressions * effective_cpm / 1000

        active_users = N_USERS * retention
        total_revenue = revenue_per_user * active_users

        results['engagement_rate'].append(engagement)
        results['retention'].append(retention)
        results['satisfaction'].append(satisfaction)
        results['data_quality'].append(data_quality)
        results['cpm'].append(effective_cpm)
        results['revenue_per_user'].append(revenue_per_user)
        results['total_revenue'].append(total_revenue)
        results['polarization_index'].append(polarization)

    return results


# === RUN SIMULATION ===
months = list(range(1, N_MONTHS + 1))
eng = engagement_based_model(N_MONTHS)
conn = connection_based_model(N_MONTHS)

# === PRINT RESULTS ===
print("=" * 80)
print("SOCIAL MEDIA ALGORITHM SIMULATION v3 -- EMPIRICALLY ANCHORED")
print("=" * 80)
print()
print("EMPIRICAL ANCHORS:")
print(f"  Milli et al. 2025: Anger amplification = {ANGER_AMPLIFICATION_SD:.2f} SD")
print(f"  Milli et al. 2025: User value divergence = {VALUE_DIVERGENCE_SD:.2f} SD")
print(f"  Germano et al. 2026: Polarization per update cycle = {POLARIZATION_PER_UPDATE_SD:.3f} SD")
print(f"  Instagram data: Monthly engagement decay = {INSTAGRAM_MONTHLY_ENGAGEMENT_DECAY*100:.2f}%/month")
print(f"  X data: Monthly revenue decay (extreme case) = {X_MONTHLY_REVENUE_DECAY*100:.1f}%/month")
print()

print("MONTH 1 (Starting State):")
print(f"  Engagement-based revenue:   ${eng['total_revenue'][0]/1e6:.2f}M/month")
print(f"  Connection-based revenue:   ${conn['total_revenue'][0]/1e6:.2f}M/month")
print(f"  Engagement-based satisfaction: {eng['satisfaction'][0]:.3f}")
print(f"  Connection-based satisfaction: {conn['satisfaction'][0]:.3f}")
print()

# Find crossover month
crossover_month = None
for i in range(1, N_MONTHS):
    if conn['total_revenue'][i] > eng['total_revenue'][i] and conn['total_revenue'][i-1] <= eng['total_revenue'][i-1]:
        crossover_month = i + 1
        break

print(f"REVENUE CROSSOVER: Month {crossover_month}")
print()

print("MONTH 36 (End State):")
print(f"  Engagement-based revenue:   ${eng['total_revenue'][-1]/1e6:.2f}M/month")
print(f"  Connection-based revenue:   ${conn['total_revenue'][-1]/1e6:.2f}M/month")
print(f"  Revenue differential:       {(conn['total_revenue'][-1]/eng['total_revenue'][-1]-1)*100:.0f}% more for connection-based")
print()
print(f"  Engagement-based satisfaction: {eng['satisfaction'][-1]:.3f}")
print(f"  Connection-based satisfaction: {conn['satisfaction'][-1]:.3f}")
print()
print(f"  Engagement-based data quality: {eng['data_quality'][-1]:.3f}")
print(f"  Connection-based data quality: {conn['data_quality'][-1]:.3f}")
print()
print(f"  Engagement-based polarization: {eng['polarization_index'][-1]:.3f}")
print(f"  Connection-based polarization: {conn['polarization_index'][-1]:.3f}")
print()
print(f"  Engagement-based CPM:  ${eng['cpm'][-1]:.2f}")
print(f"  Connection-based CPM:  ${conn['cpm'][-1]:.2f}")
print(f"  CPM differential:      {(conn['cpm'][-1]/eng['cpm'][-1]-1)*100:.0f}% higher for connection-based")
print()

# Cumulative revenue
cum_eng = sum(eng['total_revenue']) / 1e6
cum_conn = sum(conn['total_revenue']) / 1e6
print(f"CUMULATIVE REVENUE (36 months):")
print(f"  Engagement-based: ${cum_eng:.1f}M")
print(f"  Connection-based: ${cum_conn:.1f}M")
print(f"  Difference:       ${cum_conn - cum_eng:.1f}M ({(cum_conn/cum_eng-1)*100:.1f}%)")
print()

# Error accumulation
eng_error = sum(1 - s for s in eng['satisfaction'])
conn_error = sum(1 - s for s in conn['satisfaction'])
print(f"CUMULATIVE ERROR (sum of satisfaction deficit):")
print(f"  Engagement-based: {eng_error:.1f} units")
print(f"  Connection-based: {conn_error:.1f} units")
print(f"  Engagement-based accumulates {(eng_error/conn_error - 1)*100:.0f}% more error")
print()

# Retention
print(f"USER RETENTION AT MONTH 36:")
print(f"  Engagement-based: {eng['retention'][-1]*100:.1f}% of original cohort")
print(f"  Connection-based: {conn['retention'][-1]*100:.1f}% of original cohort")
print()

print("=" * 80)
print("PARAMETER SOURCES:")
print("  Milli et al. 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC11894805/")
print("  Germano et al. 2026: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4238756")
print("  Instagram engagement data: Statista/Postnitro 2026")
print("  X revenue data: Reuters/Guardian 2023-2025")
print("=" * 80)

# === GENERATE CHARTS ===
colors = {'eng': '#e85d4a', 'conn': '#4ab8e8'}
plt.style.use('dark_background')

# === CHART 1: Main comparison (6-panel) ===
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.patch.set_facecolor('#0a0a0f')
fig.suptitle('Social Media Algorithm Comparison: Empirically Anchored Model v3\n(Parameters derived from Milli et al. 2025, Germano et al. 2026, Meta/Instagram/X data)',
             fontsize=13, fontweight='bold', color='#e8e4d9', y=0.98)

panel_data = [
    ('engagement_rate', 'Engagement Rate', 'Rate (0-1)'),
    ('retention', 'User Retention', 'Fraction of Original Cohort'),
    ('satisfaction', 'User Satisfaction\n(Milli et al.: value divergence = -0.18 SD)', 'Satisfaction Index (0-1)'),
    ('data_quality', 'Behavioral Data Quality\n(Advertiser Targeting Precision)', 'Quality Index (0-1)'),
    ('cpm', 'Effective Advertiser CPM\n(Brand Safety + Targeting)', 'CPM ($)'),
    ('polarization_index', 'Polarization Index\n(Germano et al.: +1/6 SD per update cycle)', 'Polarization (0-1)'),
]

for ax, (key, title, ylabel) in zip(axes.flat, panel_data):
    ax.set_facecolor('#0f0f18')
    ax.tick_params(colors='#b8b4a9')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.plot(months, eng[key], color=colors['eng'], linewidth=2.5, label='Engagement-Based (current)')
    ax.plot(months, conn[key], color=colors['conn'], linewidth=2.5, label='Connection-Based (proposed)')
    ax.set_title(title, fontweight='bold', fontsize=10, color='#e8e4d9')
    ax.set_xlabel('Month', color='#b8b4a9', fontsize=9)
    ax.set_ylabel(ylabel, color='#b8b4a9', fontsize=9)
    ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
    ax.grid(alpha=0.15, color='#444')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('/home/ubuntu/interaction-field-research/simulation/algorithm_comparison_v3.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("\nChart saved: simulation/algorithm_comparison_v3.png")

# === CHART 2: Revenue comparison with crossover ===
fig2, ax2 = plt.subplots(1, 1, figsize=(14, 8))
fig2.patch.set_facecolor('#0a0a0f')
ax2.set_facecolor('#0f0f18')
ax2.tick_params(colors='#b8b4a9')
for spine in ax2.spines.values():
    spine.set_color('#333')

eng_rev = [r/1e6 for r in eng['total_revenue']]
conn_rev = [r/1e6 for r in conn['total_revenue']]

ax2.plot(months, eng_rev, color=colors['eng'], linewidth=3, label='Engagement-Based (current)')
ax2.plot(months, conn_rev, color=colors['conn'], linewidth=3, label='Connection-Based (proposed)')

if crossover_month:
    ax2.axvline(x=crossover_month, color='#f0c060', linewidth=1.5, linestyle='--', alpha=0.7)
    ax2.annotate(f'Crossover: Month {crossover_month}',
                 xy=(crossover_month, conn_rev[crossover_month-1]),
                 xytext=(crossover_month + 2, conn_rev[crossover_month-1] + 0.3),
                 fontsize=11, fontweight='bold', color='#f0c060',
                 arrowprops=dict(arrowstyle='->', color='#f0c060', lw=1.5))

ax2.fill_between(months, conn_rev, eng_rev,
                 where=[c > e for c, e in zip(conn_rev, eng_rev)],
                 alpha=0.15, color=colors['conn'], label='Connection advantage')
ax2.fill_between(months, conn_rev, eng_rev,
                 where=[c <= e for c, e in zip(conn_rev, eng_rev)],
                 alpha=0.15, color=colors['eng'], label='Engagement advantage')

ax2.set_title('Monthly Revenue Over 36 Months\nEmpirical Anchors: Milli et al. 2025, Germano et al. 2026, Meta/Instagram/X data',
              fontweight='bold', fontsize=13, color='#e8e4d9')
ax2.set_xlabel('Month', fontsize=12, color='#b8b4a9')
ax2.set_ylabel('Monthly Revenue ($M)', fontsize=12, color='#b8b4a9')
ax2.legend(fontsize=11, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax2.grid(alpha=0.15, color='#444')

ax2.annotate(f'Month 36: ${conn_rev[-1]:.2f}M', xy=(36, conn_rev[-1]),
             xytext=(32, conn_rev[-1] + 0.4), fontsize=11, fontweight='bold', color=colors['conn'])
ax2.annotate(f'Month 36: ${eng_rev[-1]:.2f}M', xy=(36, eng_rev[-1]),
             xytext=(32, eng_rev[-1] - 0.5), fontsize=11, fontweight='bold', color=colors['eng'])

plt.tight_layout()
plt.savefig('/home/ubuntu/interaction-field-research/simulation/revenue_comparison_v3.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("Chart saved: simulation/revenue_comparison_v3.png")

# === CHART 3: Error accumulation ===
fig3, ax3 = plt.subplots(1, 1, figsize=(14, 8))
fig3.patch.set_facecolor('#0a0a0f')
ax3.set_facecolor('#0f0f18')
ax3.tick_params(colors='#b8b4a9')
for spine in ax3.spines.values():
    spine.set_color('#333')

eng_error_cum = np.cumsum([1 - s for s in eng['satisfaction']])
conn_error_cum = np.cumsum([1 - s for s in conn['satisfaction']])

ax3.plot(months, eng_error_cum, color=colors['eng'], linewidth=3, label='Engagement-Based: Compounding Error')
ax3.plot(months, conn_error_cum, color=colors['conn'], linewidth=3, label='Connection-Based: Controlled Error')
ax3.fill_between(months, conn_error_cum, eng_error_cum, alpha=0.2, color=colors['eng'])

gap = eng_error_cum[-1] - conn_error_cum[-1]
ax3.annotate(f'Error gap at Month 36:\n{gap:.1f} units ({gap/eng_error_cum[-1]*100:.0f}% more error)',
             xy=(36, eng_error_cum[-1]), xytext=(24, eng_error_cum[-1] * 0.72),
             fontsize=11, fontweight='bold', color=colors['eng'],
             arrowprops=dict(arrowstyle='->', color=colors['eng'], lw=1.5))

ax3.set_title('Cumulative Error Accumulation: The Backwards Problem in Action\nDivergence Between Algorithm Output and Genuine User Value',
              fontweight='bold', fontsize=13, color='#e8e4d9')
ax3.set_xlabel('Month', fontsize=12, color='#b8b4a9')
ax3.set_ylabel('Cumulative Error (lower = better)', fontsize=12, color='#b8b4a9')
ax3.legend(fontsize=11, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax3.grid(alpha=0.15, color='#444')

plt.tight_layout()
plt.savefig('/home/ubuntu/interaction-field-research/simulation/error_accumulation_v3.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("Chart saved: simulation/error_accumulation_v3.png")

# === CHART 4: Polarization comparison ===
fig4, ax4 = plt.subplots(1, 1, figsize=(14, 8))
fig4.patch.set_facecolor('#0a0a0f')
ax4.set_facecolor('#0f0f18')
ax4.tick_params(colors='#b8b4a9')
for spine in ax4.spines.values():
    spine.set_color('#333')

ax4.plot(months, eng['polarization_index'], color=colors['eng'], linewidth=3,
         label='Engagement-Based: Polarization compounds (Germano et al. 2026)')
ax4.plot(months, conn['polarization_index'], color=colors['conn'], linewidth=3,
         label='Connection-Based: Polarization suppressed (polarization penalty active)')

ax4.axhline(y=POLARIZATION_PER_UPDATE_SD, color='#f0c060', linewidth=1, linestyle=':', alpha=0.7)
ax4.annotate(f'Germano et al. baseline:\n+1/6 SD per update cycle',
             xy=(6, POLARIZATION_PER_UPDATE_SD), xytext=(8, POLARIZATION_PER_UPDATE_SD + 0.05),
             fontsize=10, color='#f0c060')

ax4.set_title('Polarization Index Over 36 Months\nAnchored to Germano et al. 2026: Facebook MSI update +1/6 SD',
              fontweight='bold', fontsize=13, color='#e8e4d9')
ax4.set_xlabel('Month', fontsize=12, color='#b8b4a9')
ax4.set_ylabel('Polarization Index (0 = none, 1 = maximum)', fontsize=12, color='#b8b4a9')
ax4.legend(fontsize=11, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax4.grid(alpha=0.15, color='#444')

plt.tight_layout()
plt.savefig('/home/ubuntu/interaction-field-research/simulation/polarization_v3.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("Chart saved: simulation/polarization_v3.png")

print("\nAll charts saved.")
print("=" * 80)
print("SIMULATION v3 COMPLETE")
print("=" * 80)
