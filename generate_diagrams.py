"""
Generate all diagrams for the Exchange Is the Equation website.
Produces PNG files with East Asian-influenced minimalist design.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/assets/diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BG = "#0a0a0f"
FG = "#e8e4d9"
GOLD = "#c9a84c"
RUST = "#c0392b"
TEAL = "#2a9d8f"
MUTED = "#5a5a6a"
ACCENT = "#7c6fcd"

def fig_base(w=10, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
        spine.set_linewidth(0.5)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    return fig, ax

# ── Diagram A: Pyramid Error Accumulation ─────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.patch.set_facecolor(BG)

for ax in axes:
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
        spine.set_linewidth(0.4)

# Left: bottom-up pyramid with error arrows
ax = axes[0]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Bottom-Up Construction\nError Accumulates", color=RUST, fontsize=12, pad=10, fontfamily='monospace')

# Draw pyramid courses with slight angular offset
courses = 8
for i in range(courses):
    y0 = i * 1.0
    y1 = y0 + 0.85
    offset = i * 0.08  # cumulative error
    x_left = 1.0 + i * 0.5 - offset
    x_right = 9.0 - i * 0.5 + offset * 0.5
    rect = plt.Polygon([[x_left, y0], [x_right, y0], [x_right - 0.2, y1], [x_left + 0.2, y1]],
                       closed=True, facecolor=f"#{int(40 + i*8):02x}{int(40 + i*6):02x}{int(55 + i*5):02x}",
                       edgecolor=MUTED, linewidth=0.4)
    ax.add_patch(rect)

# Error arrow at apex
ax.annotate('', xy=(5.5 + courses*0.08, courses*1.0 + 0.5),
            xytext=(5.0, courses*1.0 + 0.5),
            arrowprops=dict(arrowstyle='->', color=RUST, lw=1.5))
ax.text(5.6 + courses*0.08, courses*1.0 + 0.5, 'σ error', color=RUST, fontsize=9, va='center', fontfamily='monospace')

# Error formula
ax.text(5, 0.3, r'$\sigma_{apex} \propto \sqrt{H}$', color=RUST, fontsize=11, ha='center', fontfamily='monospace')

# Right: top-down pyramid, no error
ax = axes[1]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Top-Down Construction\nError Eliminated", color=TEAL, fontsize=12, pad=10, fontfamily='monospace')

for i in range(courses):
    y0 = i * 1.0
    y1 = y0 + 0.85
    x_left = 1.0 + i * 0.5
    x_right = 9.0 - i * 0.5
    rect = plt.Polygon([[x_left, y0], [x_right, y0], [x_right - 0.2, y1], [x_left + 0.2, y1]],
                       closed=True, facecolor=f"#{int(30 + i*5):02x}{int(55 + i*8):02x}{int(60 + i*7):02x}",
                       edgecolor=MUTED, linewidth=0.4)
    ax.add_patch(rect)

# Capstone marker
ax.plot([4.8, 5.2], [courses*1.0 + 0.2, courses*1.0 + 0.2], color=GOLD, lw=2)
ax.text(5, courses*1.0 + 0.5, 'FIXED APEX', color=GOLD, fontsize=8, ha='center', fontfamily='monospace')
ax.text(5, 0.3, r'$\sigma_{course} = \sigma_0$ (constant)', color=TEAL, fontsize=11, ha='center', fontfamily='monospace')

fig.text(0.5, 0.02, 'The Pyramid Orientation Problem', color=MUTED, fontsize=9, ha='center', fontfamily='monospace')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_A_pyramid.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("A done")

# ── Diagram B: Interaction Field Logistic Curve ────────────────────────────────
fig, ax = fig_base(12, 7)

n = np.linspace(0, 100, 500)
k = 0.12
n_c = 50
V_max = 1.0
I = V_max / (1 + np.exp(-k * (n - n_c)))

ax.plot(n, I, color=GOLD, lw=2.5, label='I(n) = V_max / (1 + e^{-k(n-n_c)})')

# Shade phases
ax.axvspan(0, 30, alpha=0.07, color=RUST, label='Phase 1: Thin market (noisy)')
ax.axvspan(35, 65, alpha=0.1, color=GOLD, label='Phase 2: Inflection zone (optimal)')
ax.axvspan(70, 100, alpha=0.07, color=TEAL, label='Phase 3: Saturated (efficient)')

# Inflection point
ax.axvline(n_c, color=GOLD, lw=0.8, linestyle='--', alpha=0.6)
ax.plot(n_c, 0.5, 'o', color=GOLD, markersize=8, zorder=5)
ax.annotate('n_c\n(inflection point)', xy=(n_c, 0.5), xytext=(n_c + 8, 0.38),
            color=GOLD, fontsize=9, fontfamily='monospace',
            arrowprops=dict(arrowstyle='->', color=GOLD, lw=1))

ax.axhline(V_max, color=TEAL, lw=0.6, linestyle=':', alpha=0.5)
ax.text(95, V_max + 0.02, 'V_max', color=TEAL, fontsize=9, ha='right', fontfamily='monospace')

ax.set_xlabel('n  (genuine transaction count)', fontsize=11, fontfamily='monospace')
ax.set_ylabel('I(n)  (interaction field value)', fontsize=11, fontfamily='monospace')
ax.set_title('The Interaction Field Equation', color=FG, fontsize=14, pad=15, fontfamily='monospace')

legend = ax.legend(loc='upper left', fontsize=8, framealpha=0.15, labelcolor=FG)
legend.get_frame().set_facecolor(BG)

ax.text(15, 0.12, 'Arbitrage-rich\nbut noisy', color=RUST, fontsize=8, ha='center', fontfamily='monospace', alpha=0.8)
ax.text(50, 0.08, 'Optimal\nentry zone', color=GOLD, fontsize=8, ha='center', fontfamily='monospace', alpha=0.9)
ax.text(85, 0.12, 'Efficient\nmarket', color=TEAL, fontsize=8, ha='center', fontfamily='monospace', alpha=0.8)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_B_interaction_field.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("B done")

# ── Diagram C: Isomorphism Table ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis('off')
ax.set_title('The Structural Isomorphism', color=FG, fontsize=14, pad=15, fontfamily='monospace')

rows = [
    ("Pyramid Construction", "Market Value Formation"),
    ("Physical height  h", "Transaction count  n"),
    ("Angular error per stone", "Price uncertainty per trade"),
    ("Total apex displacement", "Total price uncertainty"),
    ("Bottom-up construction", "Price-first analysis"),
    ("Top-down construction", "Interaction-first analysis"),
    ("Fixed capstone (invariant)", "Interaction field (invariant)"),
    ("σ_apex = σ₀ · √h", "σ_p = σ_v / √n"),
]

col_positions = [0.05, 0.52]
row_height = 0.11
start_y = 0.88

# Header
for j, (col, txt) in enumerate(zip(col_positions, rows[0])):
    ax.text(col, start_y, txt, color=GOLD, fontsize=11, fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes)

# Divider
ax.plot([0.02, 0.98], [start_y - 0.04, start_y - 0.04], color=GOLD, lw=0.8, transform=ax.transAxes)

# Center equals column
ax.text(0.49, start_y, '≅', color=ACCENT, fontsize=14, ha='center', transform=ax.transAxes)

for i, (left, right) in enumerate(rows[1:]):
    y = start_y - (i + 1) * row_height
    color = FG if i % 2 == 0 else "#b8b4a9"
    ax.text(col_positions[0], y, left, color=color, fontsize=10, fontfamily='monospace', transform=ax.transAxes)
    ax.text(col_positions[1], y, right, color=color, fontsize=10, fontfamily='monospace', transform=ax.transAxes)
    ax.text(0.49, y, '↔', color=ACCENT, fontsize=11, ha='center', transform=ax.transAxes)
    if i < len(rows) - 2:
        ax.plot([0.02, 0.98], [y - 0.035, y - 0.035], color=MUTED, lw=0.3, alpha=0.4, transform=ax.transAxes)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_C_isomorphism.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("C done")

# ── Diagram D: Error Accumulation Comparison ───────────────────────────────────
fig, ax = fig_base(11, 6)

steps = np.linspace(1, 20, 200)
bottom_up_error = steps**2 * 0.05
top_down_error = steps * 0.05

ax.plot(steps, bottom_up_error, color=RUST, lw=2.5, label='Bottom-up: error ∝ k² (quadratic)')
ax.plot(steps, top_down_error, color=TEAL, lw=2.5, label='Top-down: error ∝ k (linear)')
ax.fill_between(steps, top_down_error, bottom_up_error, alpha=0.08, color=RUST, label='Wasted analytical effort')

ax.set_xlabel('Inference steps k', fontsize=11, fontfamily='monospace')
ax.set_ylabel('Accumulated error', fontsize=11, fontfamily='monospace')
ax.set_title('Error Accumulation: Wrong Direction vs. Correct Direction', color=FG, fontsize=13, pad=15, fontfamily='monospace')

legend = ax.legend(loc='upper left', fontsize=9, framealpha=0.15, labelcolor=FG)
legend.get_frame().set_facecolor(BG)

ax.text(18, bottom_up_error[-1] + 0.3, 'Surface-first\n(wrong direction)', color=RUST, fontsize=9,
        ha='right', fontfamily='monospace')
ax.text(18, top_down_error[-1] + 0.3, 'Structure-first\n(correct direction)', color=TEAL, fontsize=9,
        ha='right', fontfamily='monospace')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_D_error_curves.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("D done")

# ── Diagram E: Nine Domains Radial ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-1.6, 1.6)
ax.set_ylim(-1.6, 1.6)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Nine Domains of Application', color=FG, fontsize=14, pad=15, fontfamily='monospace')

domains = [
    "Trading Cards", "Drug Discovery", "Venture Capital",
    "Urban Planning", "Education", "Supply Chain",
    "Social Media", "Medicine", "Real Estate"
]
colors = [GOLD, TEAL, RUST, ACCENT, "#e76f51", "#264653", "#2a9d8f", "#e9c46a", "#f4a261"]

# Center circle
center = plt.Circle((0, 0), 0.28, color=ACCENT, alpha=0.15, zorder=2)
ax.add_patch(center)
ax.text(0, 0.05, 'Interaction', color=FG, fontsize=9, ha='center', fontfamily='monospace', zorder=3)
ax.text(0, -0.08, 'Field', color=FG, fontsize=9, ha='center', fontfamily='monospace', zorder=3)
ax.text(0, -0.2, 'Equation', color=GOLD, fontsize=8, ha='center', fontfamily='monospace', zorder=3)

for i, (domain, color) in enumerate(zip(domains, colors)):
    angle = 2 * np.pi * i / len(domains) - np.pi / 2
    x = np.cos(angle)
    y = np.sin(angle)
    # Spoke
    ax.plot([0.28 * np.cos(angle), 0.78 * np.cos(angle)],
            [0.28 * np.sin(angle), 0.78 * np.sin(angle)],
            color=color, lw=0.8, alpha=0.5)
    # Node
    circle = plt.Circle((x, y), 0.18, color=color, alpha=0.18, zorder=2)
    ax.add_patch(circle)
    circle_border = plt.Circle((x, y), 0.18, color=color, fill=False, lw=1.2, zorder=3)
    ax.add_patch(circle_border)
    # Label
    words = domain.split()
    if len(words) == 1:
        ax.text(x, y, domain, color=FG, fontsize=8.5, ha='center', va='center',
                fontfamily='monospace', zorder=4)
    else:
        ax.text(x, y + 0.04, words[0], color=FG, fontsize=8, ha='center', va='center',
                fontfamily='monospace', zorder=4)
        ax.text(x, y - 0.06, ' '.join(words[1:]), color=FG, fontsize=8, ha='center', va='center',
                fontfamily='monospace', zorder=4)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_E_domains.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("E done")

# ── Diagram F: Orientation Theorem Summary ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis('off')
ax.set_title('The Orientation Theorem', color=FG, fontsize=14, pad=15, fontfamily='monospace')

# Two columns: wrong direction / correct direction
for col_x, title, color, items in [
    (0.05, "WRONG DIRECTION (surface first)", RUST, [
        "Start: observable price / symptom / listing",
        "Infer: underlying value / cause / structure",
        "Error: accumulates as O(k²)",
        "Result: systematic underperformance",
        "Examples: symptom-first diagnosis,",
        "  comparable-sales valuation,",
        "  bottom-up pyramid construction",
    ]),
    (0.55, "CORRECT DIRECTION (structure first)", TEAL, [
        "Start: invariant deep structure / interaction field",
        "Derive: surface variables as emergent properties",
        "Error: eliminated at each step",
        "Result: systematic outperformance",
        "Examples: systems medicine,",
        "  neighborhood interaction metrics,",
        "  top-down pyramid construction",
    ]),
]:
    ax.text(col_x, 0.92, title, color=color, fontsize=10, fontfamily='monospace',
            fontweight='bold', transform=ax.transAxes)
    ax.plot([col_x - 0.02, col_x + 0.42], [0.87, 0.87], color=color, lw=0.7, alpha=0.6, transform=ax.transAxes)
    for j, item in enumerate(items):
        ax.text(col_x, 0.80 - j * 0.10, item, color=FG if j < 4 else MUTED,
                fontsize=9, fontfamily='monospace', transform=ax.transAxes,
                alpha=1.0 if j < 4 else 0.7)

# Center divider
ax.plot([0.5, 0.5], [0.05, 0.95], color=MUTED, lw=0.5, alpha=0.4, transform=ax.transAxes)
ax.text(0.5, 0.5, 'vs', color=MUTED, fontsize=12, ha='center', va='center',
        transform=ax.transAxes, fontfamily='monospace')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/diag_F_orientation.png", dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("F done")

print("All diagrams generated successfully.")
