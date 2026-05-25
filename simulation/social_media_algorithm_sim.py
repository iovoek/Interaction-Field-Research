"""
Social Media Algorithm Simulation v2
======================================
Compares two algorithmic strategies over a simulated user population:
  1. Engagement-Based (current): optimizes for clicks, reactions, shares
  2. Connection-Based (proposed): optimizes for reciprocal interaction, trust, depth

Key modeling decisions:
- Engagement-based starts with HIGHER short-term revenue (realistic)
- Connection-based has a transition cost (initial dip) before surpassing
- Error accumulation is modeled as divergence from genuine user value
- Revenue model accounts for CPM, retention, data quality, and brand safety

Outputs numerical results and generates comparison charts.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

np.random.seed(42)

# === PARAMETERS ===
N_USERS = 100000  # 100K user cohort
N_MONTHS = 36

# === MODEL FUNCTIONS ===

def engagement_based_model(months):
    """
    Engagement-based platform dynamics over time.
    
    Characteristics:
    - High initial engagement and revenue
    - Gradual user attrition as satisfaction erodes
    - Declining data quality as outrage replaces genuine signal
    - Declining CPM as brand safety degrades
    """
    results = {
        'engagement_rate': [],
        'retention': [],
        'satisfaction': [],
        'data_quality': [],
        'cpm': [],
        'revenue_per_user': [],
        'total_revenue': [],
    }
    
    # Initial values
    engagement = 0.82  # High initial engagement
    retention = 1.0
    satisfaction = 0.65  # Users start somewhat satisfied
    data_quality = 0.55  # Moderate data quality
    base_cpm = 12.0  # Starting CPM
    
    for m in range(months):
        # Engagement stays high (outrage is sticky) but slowly declines as users leave
        engagement = max(0.55, engagement - 0.003 + np.random.normal(0, 0.005))
        
        # Satisfaction erodes because algorithm promotes negative content
        # This is the Backwards Problem: surface optimization degrades deep structure
        satisfaction_decay = 0.012 + 0.002 * (1 - satisfaction)  # Accelerates as satisfaction drops
        satisfaction = max(0.25, satisfaction - satisfaction_decay + np.random.normal(0, 0.003))
        
        # Retention is driven by satisfaction + habit (habit decays over time)
        habit_factor = max(0.3, 0.9 - m * 0.015)  # Habit weakens over time
        monthly_churn = max(0.005, (1 - satisfaction) * 0.04 * (1 - habit_factor * 0.5))
        retention = max(0.35, retention * (1 - monthly_churn))
        
        # Data quality degrades as outrage interactions replace genuine preference signals
        data_quality = max(0.20, data_quality - 0.008 + np.random.normal(0, 0.003))
        
        # CPM declines due to brand safety concerns and lower targeting precision
        brand_safety_factor = 0.6 + 0.4 * satisfaction  # Lower satisfaction = more toxic = less brand safe
        targeting_factor = 0.4 + 0.6 * data_quality
        effective_cpm = base_cpm * brand_safety_factor * targeting_factor
        
        # Revenue per user = engagement * impressions_per_session * sessions * CPM / 1000
        sessions_per_day = 2.5 + engagement * 3  # 2.5-5.5 sessions/day
        impressions_per_session = 15 + engagement * 20  # 15-35 impressions
        monthly_impressions = sessions_per_day * impressions_per_session * 30
        revenue_per_user = monthly_impressions * effective_cpm / 1000
        
        # Total revenue = revenue per active user * active users
        active_users = N_USERS * retention
        total_revenue = revenue_per_user * active_users
        
        results['engagement_rate'].append(engagement)
        results['retention'].append(retention)
        results['satisfaction'].append(satisfaction)
        results['data_quality'].append(data_quality)
        results['cpm'].append(effective_cpm)
        results['revenue_per_user'].append(revenue_per_user)
        results['total_revenue'].append(total_revenue)
    
    return results


def connection_based_model(months):
    """
    Connection-based platform dynamics over time.
    
    Characteristics:
    - Lower initial engagement (less outrage-driven dopamine)
    - Initial revenue dip as algorithm transitions
    - Growing satisfaction as genuine connections form
    - Improving data quality as interactions become more authentic
    - Rising CPM as brand safety improves and targeting gets better
    - Network effects from genuine connections create retention moat
    """
    results = {
        'engagement_rate': [],
        'retention': [],
        'satisfaction': [],
        'data_quality': [],
        'cpm': [],
        'revenue_per_user': [],
        'total_revenue': [],
    }
    
    # Initial values (starts LOWER than engagement-based)
    engagement = 0.58  # Lower initial engagement (less outrage bait)
    retention = 1.0
    satisfaction = 0.65  # Same starting satisfaction
    data_quality = 0.55  # Same starting data quality
    base_cpm = 12.0
    genuine_connections = 0.0  # Accumulated genuine connections (network effect)
    
    for m in range(months):
        # Engagement grows slowly as users find genuine value
        # Connection-based content is less immediately addictive but more sustainably engaging
        engagement_growth = 0.005 + genuine_connections * 0.001
        engagement = min(0.78, engagement + engagement_growth + np.random.normal(0, 0.005))
        
        # Satisfaction grows because algorithm promotes genuinely valuable content
        satisfaction_growth = 0.015 * (1 - satisfaction) + genuine_connections * 0.003
        satisfaction = min(0.95, satisfaction + satisfaction_growth + np.random.normal(0, 0.003))
        
        # Genuine connections accumulate (logistic growth)
        connection_rate = 0.08 * satisfaction * (1 - genuine_connections / 10.0)
        genuine_connections = min(10.0, genuine_connections + connection_rate)
        
        # Retention improves because genuine connections create switching costs
        # Users with real friends on the platform do not leave
        connection_retention = min(0.04, genuine_connections * 0.004)
        monthly_churn = max(0.002, 0.025 * (1 - satisfaction) - connection_retention)
        retention = max(0.60, retention * (1 - monthly_churn))
        
        # Data quality improves as interactions become more authentic
        data_quality = min(0.92, data_quality + 0.010 + np.random.normal(0, 0.003))
        
        # CPM rises due to brand safety and superior targeting
        brand_safety_factor = 0.6 + 0.4 * satisfaction
        targeting_factor = 0.4 + 0.6 * data_quality
        effective_cpm = base_cpm * brand_safety_factor * targeting_factor
        
        # Revenue per user
        sessions_per_day = 2.0 + engagement * 2.5  # Fewer but more intentional sessions
        impressions_per_session = 12 + engagement * 15  # Fewer impressions but higher quality
        monthly_impressions = sessions_per_day * impressions_per_session * 30
        revenue_per_user = monthly_impressions * effective_cpm / 1000
        
        # Total revenue
        active_users = N_USERS * retention
        total_revenue = revenue_per_user * active_users
        
        results['engagement_rate'].append(engagement)
        results['retention'].append(retention)
        results['satisfaction'].append(satisfaction)
        results['data_quality'].append(data_quality)
        results['cpm'].append(effective_cpm)
        results['revenue_per_user'].append(revenue_per_user)
        results['total_revenue'].append(total_revenue)
    
    return results


# === RUN SIMULATION ===
print("Running engagement-based simulation (100K users, 36 months)...")
eng = engagement_based_model(N_MONTHS)
print("Running connection-based simulation (100K users, 36 months)...")
conn = connection_based_model(N_MONTHS)

months = np.arange(1, N_MONTHS + 1)

# Find crossover point
crossover_month = None
for i in range(N_MONTHS):
    if conn['total_revenue'][i] > eng['total_revenue'][i]:
        crossover_month = i + 1
        break

# === PRINT RESULTS ===
print("\n" + "="*80)
print("SIMULATION RESULTS: 36-MONTH ALGORITHM COMPARISON")
print("="*80)
print(f"Population: {N_USERS:,} user cohort")
print(f"Time horizon: {N_MONTHS} months")
if crossover_month:
    print(f"Revenue crossover point: Month {crossover_month}")

print("\n--- MONTH 1 (INITIAL STATE) ---")
print(f"{'Metric':<35} {'Engagement-Based':<20} {'Connection-Based':<20}")
print("-"*75)
print(f"{'Total Monthly Revenue':<35} ${eng['total_revenue'][0]:>14,.0f} ${conn['total_revenue'][0]:>14,.0f}")
print(f"{'Revenue/User':<35} ${eng['revenue_per_user'][0]:>14.2f} ${conn['revenue_per_user'][0]:>14.2f}")
print(f"{'Engagement Rate':<35} {eng['engagement_rate'][0]:>14.3f} {conn['engagement_rate'][0]:>14.3f}")

print(f"\n--- MONTH {N_MONTHS} (FINAL STATE) ---")
print(f"{'Metric':<35} {'Engagement-Based':<20} {'Connection-Based':<20} {'Delta':<12}")
print("-"*87)

comparisons = [
    ("Total Monthly Revenue", eng['total_revenue'][-1], conn['total_revenue'][-1], "$", True),
    ("Revenue/User/Month", eng['revenue_per_user'][-1], conn['revenue_per_user'][-1], "$", True),
    ("User Retention", eng['retention'][-1], conn['retention'][-1], "", False),
    ("User Satisfaction", eng['satisfaction'][-1], conn['satisfaction'][-1], "", False),
    ("Data Quality Index", eng['data_quality'][-1], conn['data_quality'][-1], "", False),
    ("Effective CPM", eng['cpm'][-1], conn['cpm'][-1], "$", True),
    ("Engagement Rate", eng['engagement_rate'][-1], conn['engagement_rate'][-1], "", False),
]

for name, e_val, c_val, prefix, is_money in comparisons:
    delta = ((c_val - e_val) / e_val) * 100
    if is_money:
        print(f"{name:<35} {prefix}{e_val:>13,.2f} {prefix}{c_val:>13,.2f} {delta:>+8.1f}%")
    else:
        print(f"{name:<35} {e_val:>14.4f} {c_val:>14.4f} {delta:>+8.1f}%")

# Cumulative revenue
cum_eng = sum(eng['total_revenue'])
cum_conn = sum(conn['total_revenue'])
print(f"\n{'Cumulative 36-Month Revenue':<35} ${cum_eng:>13,.0f} ${cum_conn:>13,.0f} {((cum_conn-cum_eng)/cum_eng)*100:>+8.1f}%")

# Short-term cost
if crossover_month and crossover_month > 1:
    short_term_cost = sum(eng['total_revenue'][:crossover_month-1]) - sum(conn['total_revenue'][:crossover_month-1])
    print(f"\nShort-term revenue cost (Months 1-{crossover_month-1}): ${short_term_cost:,.0f}")
    long_term_gain = sum(conn['total_revenue'][crossover_month-1:]) - sum(eng['total_revenue'][crossover_month-1:])
    print(f"Long-term revenue gain (Months {crossover_month}-36): ${long_term_gain:,.0f}")
    print(f"Net gain over 36 months: ${cum_conn - cum_eng:,.0f}")
    print(f"ROI on transition: {((cum_conn - cum_eng) / short_term_cost) * 100:.0f}%")

# === GENERATE CHARTS ===
plt.style.use('default')
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.patch.set_facecolor('#0a0a0f')
for ax in axes.flat:
    ax.set_facecolor('#0f0f18')
    ax.tick_params(colors='#b8b4a9')
    ax.xaxis.label.set_color('#b8b4a9')
    ax.yaxis.label.set_color('#b8b4a9')
    ax.title.set_color('#e8e4d9')
    for spine in ax.spines.values():
        spine.set_color('#333')

fig.suptitle("Social Media Algorithm Simulation\nEngagement-Based vs. Connection-Based (100K Users, 36 Months)", 
             fontsize=14, fontweight='bold', color='#e8e4d9', y=0.98)

colors = {'eng': '#c0392b', 'conn': '#2a9d8f'}

# 1. Total Revenue
ax = axes[0, 0]
ax.plot(months, [r/1e6 for r in eng['total_revenue']], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, [r/1e6 for r in conn['total_revenue']], color=colors['conn'], linewidth=2.5, label='Connection-Based')
if crossover_month:
    ax.axvline(x=crossover_month, color='#7c6fcd', linestyle='--', alpha=0.8, linewidth=1.5, label=f'Crossover (Month {crossover_month})')
ax.set_title('Total Monthly Revenue', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('Revenue ($M)')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

# 2. User Retention
ax = axes[0, 1]
ax.plot(months, [r*100 for r in eng['retention']], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, [r*100 for r in conn['retention']], color=colors['conn'], linewidth=2.5, label='Connection-Based')
ax.set_title('User Retention Rate', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('Retention (%)')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

# 3. User Satisfaction
ax = axes[0, 2]
ax.plot(months, eng['satisfaction'], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, conn['satisfaction'], color=colors['conn'], linewidth=2.5, label='Connection-Based')
ax.set_title('User Satisfaction', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('Satisfaction (0-1)')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

# 4. Revenue Per User
ax = axes[1, 0]
ax.plot(months, eng['revenue_per_user'], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, conn['revenue_per_user'], color=colors['conn'], linewidth=2.5, label='Connection-Based')
ax.set_title('Revenue Per Active User', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('$/user/month')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

# 5. Data Quality
ax = axes[1, 1]
ax.plot(months, eng['data_quality'], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, conn['data_quality'], color=colors['conn'], linewidth=2.5, label='Connection-Based')
ax.set_title('Behavioral Data Quality', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('Quality Index (0-1)')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

# 6. Effective CPM
ax = axes[1, 2]
ax.plot(months, eng['cpm'], color=colors['eng'], linewidth=2.5, label='Engagement-Based')
ax.plot(months, conn['cpm'], color=colors['conn'], linewidth=2.5, label='Connection-Based')
ax.set_title('Effective Advertiser CPM', fontweight='bold', fontsize=11)
ax.set_xlabel('Month')
ax.set_ylabel('CPM ($)')
ax.legend(fontsize=8, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax.grid(alpha=0.15, color='#444')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('/home/ubuntu/interaction-field-research/simulation/algorithm_comparison.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("\nChart saved: simulation/algorithm_comparison.png")

# === ERROR ACCUMULATION CHART ===
fig2, ax2 = plt.subplots(1, 1, figsize=(12, 7))
fig2.patch.set_facecolor('#0a0a0f')
ax2.set_facecolor('#0f0f18')
ax2.tick_params(colors='#b8b4a9')
for spine in ax2.spines.values():
    spine.set_color('#333')

# Cumulative error = sum of (1 - satisfaction) over time
# This represents the total divergence between what the algorithm delivers and what users actually need
eng_error = np.cumsum([1 - s for s in eng['satisfaction']])
conn_error = np.cumsum([1 - s for s in conn['satisfaction']])

ax2.plot(months, eng_error, color=colors['eng'], linewidth=3, label='Engagement-Based: Compounding Error')
ax2.plot(months, conn_error, color=colors['conn'], linewidth=3, label='Connection-Based: Controlled Error')
ax2.fill_between(months, conn_error, eng_error, alpha=0.2, color=colors['eng'])

ax2.set_title('Cumulative Error Accumulation (The Backwards Problem)\nDivergence Between Algorithm Output and User Wellbeing', 
              fontweight='bold', fontsize=13, color='#e8e4d9')
ax2.set_xlabel('Month', fontsize=12, color='#b8b4a9')
ax2.set_ylabel('Cumulative Error (lower = better)', fontsize=12, color='#b8b4a9')
ax2.legend(fontsize=11, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax2.grid(alpha=0.15, color='#444')

# Annotate the gap
gap = eng_error[-1] - conn_error[-1]
ax2.annotate(f'Error gap at Month 36:\n{gap:.1f} cumulative units\n({gap/eng_error[-1]*100:.0f}% more error)', 
             xy=(36, eng_error[-1]), xytext=(26, eng_error[-1]*0.65),
             fontsize=10, fontweight='bold', color=colors['eng'],
             arrowprops=dict(arrowstyle='->', color=colors['eng'], lw=1.5))

plt.tight_layout()
plt.savefig('/home/ubuntu/interaction-field-research/simulation/error_accumulation.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("Chart saved: simulation/error_accumulation.png")

# === CUMULATIVE REVENUE COMPARISON ===
fig3, ax3 = plt.subplots(1, 1, figsize=(12, 7))
fig3.patch.set_facecolor('#0a0a0f')
ax3.set_facecolor('#0f0f18')
ax3.tick_params(colors='#b8b4a9')
for spine in ax3.spines.values():
    spine.set_color('#333')

cum_eng_monthly = np.cumsum(eng['total_revenue']) / 1e6
cum_conn_monthly = np.cumsum(conn['total_revenue']) / 1e6

ax3.plot(months, cum_eng_monthly, color=colors['eng'], linewidth=3, label='Engagement-Based')
ax3.plot(months, cum_conn_monthly, color=colors['conn'], linewidth=3, label='Connection-Based')
ax3.fill_between(months, cum_eng_monthly, cum_conn_monthly, 
                 where=cum_conn_monthly > cum_eng_monthly, alpha=0.2, color=colors['conn'], label='Connection advantage')
ax3.fill_between(months, cum_eng_monthly, cum_conn_monthly, 
                 where=cum_conn_monthly <= cum_eng_monthly, alpha=0.2, color=colors['eng'], label='Engagement advantage')

ax3.set_title('Cumulative Revenue Over 36 Months\n(The Business Case for Reorientation)', 
              fontweight='bold', fontsize=13, color='#e8e4d9')
ax3.set_xlabel('Month', fontsize=12, color='#b8b4a9')
ax3.set_ylabel('Cumulative Revenue ($M)', fontsize=12, color='#b8b4a9')
ax3.legend(fontsize=10, facecolor='#141420', edgecolor='#333', labelcolor='#b8b4a9')
ax3.grid(alpha=0.15, color='#444')

# Annotate final values
ax3.annotate(f'${cum_conn_monthly[-1]:.1f}M', xy=(36, cum_conn_monthly[-1]), 
             xytext=(33, cum_conn_monthly[-1]+2), fontsize=11, fontweight='bold', color=colors['conn'])
ax3.annotate(f'${cum_eng_monthly[-1]:.1f}M', xy=(36, cum_eng_monthly[-1]), 
             xytext=(33, cum_eng_monthly[-1]-3), fontsize=11, fontweight='bold', color=colors['eng'])

plt.tight_layout()
plt.savefig('/home/ubuntu/interaction-field-research/simulation/cumulative_revenue.png', dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
print("Chart saved: simulation/cumulative_revenue.png")

print("\n" + "="*80)
print("SIMULATION COMPLETE")
print("="*80)
