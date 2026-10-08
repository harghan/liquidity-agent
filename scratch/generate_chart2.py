import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
fig.patch.set_facecolor('#0B0F19')
ax1.set_facecolor('#0B0F19')
ax2.set_facecolor('#0B0F19')

# Chart 2A: Slippage Curve by Order Size ($k)
order_sizes = np.array([25, 50, 100, 250, 500, 1000, 2500, 5000])
single_venue_slippage = np.array([18, 35, 78, 142, 215, 296, 420, 610]) # bps
prism_routed_slippage = np.array([3, 5, 11, 19, 28, 42, 65, 92])       # bps

ax1.plot(order_sizes, single_venue_slippage, color='#F43F5E', marker='o', linewidth=2.2, label='Single Venue Execution (Kalshi or Poly)')
ax1.plot(order_sizes, prism_routed_slippage, color='#10B981', marker='s', linewidth=2.2, label='PRISM Smart Order Router (Atomic Split)')
ax1.fill_between(order_sizes, single_venue_slippage, prism_routed_slippage, color='#10B981', alpha=0.15, label='Alpha Preserved: 254 - 518 bps')

ax1.set_xscale('log')
ax1.set_title('EXECUTION SLIPPAGE VS NOTIONAL ORDER SIZE', fontsize=11, fontweight='bold', color='#F8FAFC', pad=12)
ax1.set_xlabel('Notional Order Size ($k USD)', fontsize=9, color='#94A3B8')
ax1.set_ylabel('Execution Slippage (Basis Points)', fontsize=9, color='#94A3B8')
ax1.grid(True, linestyle='--', alpha=0.15, color='#334155')
ax1.legend(loc='upper left', frameon=True, facecolor='#1E293B', edgecolor='#334155', fontsize=8)

# Chart 2B: Global Volume Scaling Projection (Amodei / Leopold Law)
years = ['2026', '2027', '2028', '2029', '2030']
market_volume = [12, 38, 85, 175, 320] # $B
prism_volume = [0.965, 4.205, 16.848, 41.578, 82.320] # $B

x = np.arange(len(years))
width = 0.35

rects1 = ax2.bar(x - width/2, market_volume, width, label='Global Prediction Volume ($B)', color='#334155')
rects2 = ax2.bar(x + width/2, prism_volume, width, label='PRISM Routed Flow ($B)', color='#38BDF8')

ax2.set_title('EPISTEMIC VOLUME SCALING LAW (2026 - 2030)', fontsize=11, fontweight='bold', color='#F8FAFC', pad=12)
ax2.set_ylabel('Annual Notional Volume ($B USD)', fontsize=9, color='#94A3B8')
ax2.set_xticks(x)
ax2.set_xticklabels(years)
ax2.grid(True, linestyle='--', alpha=0.15, color='#334155', axis='y')
ax2.legend(loc='upper left', frameon=True, facecolor='#1E293B', edgecolor='#334155', fontsize=8)

for bar in rects2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f'${yval:.1f}B', ha='center', va='bottom', fontsize=7.5, color='#38BDF8', fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/harshaghandikota/Liquidity Agent/public/chart_slippage_and_scaling.png', dpi=300, facecolor=fig.get_facecolor())
plt.close()
print("Chart 2 generated successfully.")
