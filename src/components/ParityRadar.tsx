import React from 'react';
import { MarketEvent } from '@/types';
import { AlertTriangle, TrendingUp, AlertOctagon, ShieldCheck } from 'lucide-react';

interface ParityRadarProps {
  markets?: Record<string, MarketEvent>;
}

export const ParityRadar: React.FC<ParityRadarProps> = ({ markets = {} }) => {
  const marketList = Object.values(markets);

  // Generate real arbitrage radar opportunities for each live contract
  const opportunities = marketList.map((m) => {
    const spreadBps = m.spreadBps || Math.round(Math.abs(m.polyMid - m.kalshiMid) * 10000);
    // Annualized ROIC assuming 180 day mean resolution
    const roic = ((spreadBps / 10000) * (365 / 180) * 100).toFixed(1);
    const beatsSofr = parseFloat(roic) >= 4.80;
    const sofrDelta = (parseFloat(roic) - 4.80).toFixed(1);

    return {
      id: m.id,
      pair: m.name,
      category: m.category,
      polyMid: m.polyMid,
      kalshiMid: m.kalshiMid,
      grossSpread: `+${spreadBps.toFixed(1)} bps`,
      roic: `${roic}%`,
      beatsSofr,
      sofrDelta: beatsSofr ? `+${sofrDelta}%` : `${sofrDelta}%`,
      action: beatsSofr ? 'INSTITUTIONAL ALPHA' : 'CAPITAL DESTRUCTIVE',
      strategy: m.polyMid > m.kalshiMid ? 'DISCOUNT_KALSHI_ARB' : 'DISCOUNT_POLY_ARB',
    };
  }).sort((a, b) => parseFloat(b.roic) - parseFloat(a.roic));

  return (
    <div className="space-y-6">
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-white/[0.08]">
          <div>
            <div className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Synthetic Binary Parity & Capital Efficiency Radar
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Live arbitrage scan across {marketList.length} active contracts vs. SOFR 4.80% Hurdle Benchmark
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold px-3 py-1 rounded-full">
              {opportunities.filter((o) => o.beatsSofr).length} Alpha Pairs Found
            </span>
            <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full">
              SOFR Benchmark: 4.80%
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-slate-400 uppercase tracking-wider font-semibold">
                <th className="text-left py-2.5 px-3">Live Prediction Contract</th>
                <th className="text-left py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Poly vs Kalshi</th>
                <th className="py-2.5 px-3">Gross Spread</th>
                <th className="py-2.5 px-3">Ann. ROIC</th>
                <th className="py-2.5 px-3">SOFR Verdict</th>
                <th className="text-right py-2.5 px-3">Capital Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {opportunities.slice(0, 15).map((op) => (
                <tr key={op.id} className="hover:bg-white/[0.02] transition-colors font-mono">
                  <td className="text-left py-3.5 px-3 font-sans font-medium text-white max-w-xs truncate">
                    {op.pair}
                  </td>
                  <td className="text-left py-3.5 px-3 font-sans">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-white/[0.04] text-slate-400">
                      {op.category}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 text-slate-300">
                    ${op.polyMid.toFixed(3)} / ${op.kalshiMid.toFixed(3)}
                  </td>
                  <td className={`py-3.5 px-3 font-bold ${op.beatsSofr ? 'text-emerald-400' : 'text-slate-400'}`}>
                    {op.grossSpread}
                  </td>
                  <td className={`py-3.5 px-3 font-bold ${op.beatsSofr ? 'text-white' : 'text-slate-400'}`}>
                    {op.roic}
                  </td>
                  <td className="py-3.5 px-3">
                    {op.beatsSofr ? (
                      <span className="inline-flex items-center gap-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded text-[11px] font-bold">
                        <TrendingUp className="w-3 h-3" />
                        BEATS SOFR ({op.sofrDelta})
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 px-2 py-0.5 rounded text-[11px] font-bold">
                        <AlertOctagon className="w-3 h-3" />
                        FAILS SOFR ({op.sofrDelta})
                      </span>
                    )}
                  </td>
                  <td className={`text-right py-3.5 px-3 font-sans font-bold ${
                    op.beatsSofr ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {op.action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-5 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <div className="font-bold text-amber-300">Institutional Capital Lockup Notice</div>
          <p className="leading-relaxed text-slate-400">
            In binary event markets, completing cross-venue synthetic parity requires simultaneously purchasing both legs (P(YES) + P(NO) ≤ 1.00). Without portfolio cross-margining, taking both sides requires locking 200% gross margin until official oracle determination. PRISM automatically flags any spread yielding less than the risk-free SOFR benchmark (4.80%) as capital-destructive.
          </p>
        </div>
      </div>
    </div>
  );
};
