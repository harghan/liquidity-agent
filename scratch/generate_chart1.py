import matplotlib.pyplot as plt
import numpy as np

# Set dark luxury institutional aesthetic
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
fig.patch.set_facecolor('#0B0F19')
ax.set_facecolor('#0B0F19')

# Data: 14.2 second high-frequency event burst
seconds = np.linspace(0, 14.2, 500)
kalshi_prob = 57.6 + 4.8 / (1 + np.exp(-1.5 * (seconds - 2.5)))
poly_prob = 57.6 + 4.8 / (1 + np.exp(-0.8 * (seconds - 8.5)))

# Plot Curves
ax.plot(seconds, kalshi_prob, color='#38BDF8', linewidth=2.5, label='Kalshi CLOB (Domestic CFTC Regulated)')
ax.plot(seconds, poly_prob, color='#818CF8', linewidth=2.5, linestyle='--', label='Polymarket CLOB (Offshore Polygon / UMA)')

# Shaded Discrepancy Window (Alpha Leakage)
ax.fill_between(seconds, kalshi_prob, poly_prob, where=(kalshi_prob > poly_prob),
                color='#38BDF8', alpha=0.18, label='Arbitrage Window (480 bps Peak Spread)')

# Formatting & Annotations
ax.axvline(x=2.5, color='#38BDF8', linestyle=':', alpha=0.5)
ax.axvline(x=8.5, color='#818CF8', linestyle=':', alpha=0.5)

ax.annotate('Macro Shock Ingested\n(Kalshi Re-prices: t=2.5s)', xy=(2.5, 60.0), xytext=(0.5, 61.5),
            color='#38BDF8', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#38BDF8', lw=1.2))

ax.annotate('Offshore Liquidity Catch-up\n(UMA / USDC Lag: t=8.5s)', xy=(8.5, 59.2), xytext=(9.2, 58.0),
            color='#818CF8', fontsize=8.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#818CF8', lw=1.2))

ax.set_title('TICK-LEVEL CROSS-VENUE PRICE DIVERGENCE (MACRO EVENT SHOCK)', fontsize=12, fontweight='bold', color='#F8FAFC', pad=15)
ax.set_xlabel('Elapsed Time Post-Shock (Seconds)', fontsize=9.5, color='#94A3B8')
ax.set_ylabel('Implied Probability Price (¢)', fontsize=9.5, color='#94A3B8')
ax.set_ylim(56.5, 63.5)
ax.set_xlim(0, 14.2)
ax.grid(True, linestyle='--', alpha=0.15, color='#334155')
ax.legend(loc='lower right', frameon=True, facecolor='#1E293B', edgecolor='#334155', fontsize=8.5)

plt.tight_layout()
plt.savefig('/Users/harshaghandikota/Liquidity Agent/public/chart_divergence.png', dpi=300, facecolor=fig.get_facecolor())
plt.close()
print("Chart 1 generated successfully.")
