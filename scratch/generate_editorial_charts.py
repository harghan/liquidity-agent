import matplotlib.pyplot as plt
import numpy as np

# Set high-end editorial light aesthetic (Tufte / Financial Times / Stripe Press)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Georgia', 'DejaVu Serif', 'Times New Roman']

# CHART 1: Tick-Level Price Divergence
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

seconds = np.linspace(0, 14.2, 600)
kalshi_prob = 57.6 + 4.8 / (1 + np.exp(-1.8 * (seconds - 2.5)))
poly_prob = 57.6 + 4.8 / (1 + np.exp(-0.85 * (seconds - 8.5)))

# Plot Curves
ax.plot(seconds, kalshi_prob, color='#0F172A', linewidth=2.4, label='Kalshi CLOB (Domestic CFTC Cleared)')
ax.plot(seconds, poly_prob, color='#2563EB', linewidth=2.2, linestyle='--', label='Polymarket CLOB (Offshore Polygon / UMA)')

# Shaded Discrepancy Window
ax.fill_between(seconds, kalshi_prob, poly_prob, where=(kalshi_prob > poly_prob),
                color='#3B82F6', alpha=0.14, label='Open Cross-Venue Arbitrage Window (480 bps Peak Spread)')

# Subtle event timeline lines
ax.axvline(x=2.5, color='#94A3B8', linestyle=':', linewidth=1.0)
ax.axvline(x=8.5, color='#94A3B8', linestyle=':', linewidth=1.0)

# Editorial Callouts
ax.annotate('Macro Shock Ingested\n(Kalshi re-prices in t = 2.5s)', xy=(2.5, 60.0), xytext=(0.4, 61.8),
            fontsize=8.5, color='#0F172A', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#0F172A', lw=1.0))

ax.annotate('Offshore Liquidity Catch-up Lag\n(UMA / USDC delay: 14.2s window)', xy=(8.5, 59.2), xytext=(9.0, 58.0),
            fontsize=8.5, color='#2563EB', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.0))

# Clean axes & labels
ax.set_title('Figure 1: High-Frequency Cross-Venue Price Divergence During Macro Event Shock', 
             fontsize=11.5, fontweight='bold', color='#0F172A', pad=14, loc='left')
ax.set_xlabel('Elapsed Time Post-Shock (Seconds)', fontsize=9, color='#475569')
ax.set_ylabel('Implied Probability Price (¢)', fontsize=9, color='#475569')
ax.set_ylim(56.8, 63.2)
ax.set_xlim(0, 14.2)

# Minimalist Spines (Tufte style)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#CBD5E1')
ax.spines['bottom'].set_color('#CBD5E1')
ax.grid(True, linestyle='--', alpha=0.35, color='#E2E8F0')
ax.legend(loc='lower right', frameon=False, fontsize=8.5)

plt.tight_layout()
plt.savefig('/Users/harshaghandikota/Liquidity Agent/public/chart_divergence_editorial.png', dpi=300, facecolor=fig.get_facecolor())
plt.close()

# CHART 2: Slippage & Scaling
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax1.set_facecolor('#FFFFFF')
ax2.set_facecolor('#FFFFFF')

# Left: Slippage Curves
order_sizes = np.array([25, 50, 100, 250, 500, 1000, 2500, 5000])
single_venue_slippage = np.array([18, 35, 78, 142, 215, 296, 420, 610]) # bps
prism_routed_slippage = np.array([3, 5, 11, 19, 28, 42, 65, 92])       # bps

ax1.plot(order_sizes, single_venue_slippage, color='#DC2626', marker='o', markersize=4, linewidth=2.0, label='Single-Venue Execution')
ax1.plot(order_sizes, prism_routed_slippage, color='#0F172A', marker='s', markersize=4, linewidth=2.0, label='PRISM Smart Order Router')
ax1.fill_between(order_sizes, single_venue_slippage, prism_routed_slippage, color='#10B981', alpha=0.12, label='Preserved Alpha (254 - 518 bps)')

ax1.set_xscale('log')
ax1.set_title('(A) Execution Slippage vs Order Size', fontsize=10.5, fontweight='bold', color='#0F172A', loc='left', pad=10)
ax1.set_xlabel('Notional Order Size ($k USD)', fontsize=8.5, color='#475569')
ax1.set_ylabel('Execution Slippage (Basis Points)', fontsize=8.5, color='#475569')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#CBD5E1')
ax1.spines['bottom'].set_color('#CBD5E1')
ax1.grid(True, linestyle='--', alpha=0.35, color='#E2E8F0')
ax1.legend(loc='upper left', frameon=False, fontsize=8)

# Right: Volume Scaling
years = ['2026', '2027', '2028', '2029', '2030']
market_volume = [12, 38, 85, 175, 320]
prism_volume = [0.965, 4.205, 16.848, 41.578, 82.320]

x = np.arange(len(years))
width = 0.35

ax2.bar(x - width/2, market_volume, width, label='Global Market Volume ($B)', color='#E2E8F0', edgecolor='#CBD5E1')
bars = ax2.bar(x + width/2, prism_volume, width, label='PRISM Routed Flow ($B)', color='#0F172A')

ax2.set_title('(B) Epistemic Volume Scaling Law', fontsize=10.5, fontweight='bold', color='#0F172A', loc='left', pad=10)
ax2.set_ylabel('Annual Notional ($B USD)', fontsize=8.5, color='#475569')
ax2.set_xticks(x)
ax2.set_xticklabels(years, fontsize=8.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#CBD5E1')
ax2.spines['bottom'].set_color('#CBD5E1')
ax2.grid(True, linestyle='--', alpha=0.35, color='#E2E8F0', axis='y')
ax2.legend(loc='upper left', frameon=False, fontsize=8)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 4, f'${yval:.1f}B', ha='center', va='bottom', fontsize=7.5, color='#0F172A', fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/harshaghandikota/Liquidity Agent/public/chart_slippage_and_scaling_editorial.png', dpi=300, facecolor=fig.get_facecolor())
plt.close()
print("Editorial charts successfully generated.")
