import React from 'react';
import { AlertTriangle, TrendingUp, AlertOctagon } from 'lucide-react';

export const ParityRadar: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-white/[0.08]">
          <div>
            <div className="text-base font-bold text-white tracking-tight">
              Synthetic Binary Parity & Capital Efficiency Radar
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Testing $P_{'{YES}'} + P_{'{NO}'} = 1.00$ Arbitrage vs. SOFR 4.80% Hurdle Benchmark
            </div>
          </div>
          <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full">
            SOFR Benchmark: 4.80%
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-slate-400 uppercase tracking-wider font-semibold">
                <th className="text-left py-2.5 px-3">Event Pair</th>
                <th className="py-2.5 px-3">Gross Spread</th>
                <th className="py-2.5 px-3">Annualized ROIC</th>
                <th className="py-2.5 px-3">SOFR Verdict</th>
                <th className="text-right py-2.5 px-3">Capital Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              <tr className="hover:bg-white/[0.02] transition-colors font-mono">
                <td className="text-left py-3.5 px-3 font-sans font-medium text-white">
                  Federal Reserve Rate Decision (Dec 2026)
                </td>
                <td className="py-3.5 px-3 font-bold text-emerald-400">+284.5 bps</td>
                <td className="py-3.5 px-3 font-bold text-white">14.4%</td>
                <td className="py-3.5 px-3">
                  <span className="inline-flex items-center gap-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded text-[11px] font-bold">
                    <TrendingUp className="w-3 h-3" />
                    BEATS SOFR (+9.6%)
                  </span>
                </td>
                <td className="text-right py-3.5 px-3 font-sans font-bold text-emerald-400">
                  INSTITUTIONAL ALPHA
                </td>
              </tr>

              <tr className="hover:bg-white/[0.02] transition-colors font-mono">
                <td className="text-left py-3.5 px-3 font-sans font-medium text-slate-300">
                  Vivek Ramaswamy 2028 Presidential
                </td>
                <td className="py-3.5 px-3 text-slate-400">+18.2 bps</td>
                <td className="py-3.5 px-3 text-slate-400">0.7%</td>
                <td className="py-3.5 px-3">
                  <span className="inline-flex items-center gap-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 px-2 py-0.5 rounded text-[11px] font-bold">
                    <AlertOctagon className="w-3 h-3" />
                    FAILS SOFR (-4.1%)
                  </span>
                </td>
                <td className="text-right py-3.5 px-3 font-sans font-bold text-rose-400">
                  CAPITAL DESTRUCTIVE
                </td>
              </tr>

              <tr className="hover:bg-white/[0.02] transition-colors font-mono">
                <td className="text-left py-3.5 px-3 font-sans font-medium text-slate-300">
                  US NBER Recession Before 2027
                </td>
                <td className="py-3.5 px-3 text-amber-400 font-bold">+152.0 bps</td>
                <td className="py-3.5 px-3 text-slate-300">4.0%</td>
                <td className="py-3.5 px-3">
                  <span className="inline-flex items-center gap-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 px-2 py-0.5 rounded text-[11px] font-bold">
                    <AlertTriangle className="w-3 h-3" />
                    MARGIN TRAP (-0.8%)
                  </span>
                </td>
                <td className="text-right py-3.5 px-3 font-sans font-bold text-amber-400">
                  AVOID (MARGIN TRAP)
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Institutional 200% Margin Lockup Warning Box */}
        <div className="mt-6 bg-amber-500/[0.04] border border-amber-500/20 rounded-xl p-4 flex items-start gap-3 text-xs text-amber-200/90 leading-relaxed">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-amber-300">The 200% Margin Lockup Trap:</strong> In prediction markets without cross-margining, buying YES on venue A and NO on venue B requires posting 200% gross collateral. If an event resolves in 9 months, an apparent 300 bps spread yields only ~4.1% annualized (lower than 4.80% risk-free T-bills). PRISM explicitly flags capital-destructive trades to protect fund balance sheets.
          </div>
        </div>
      </div>
    </div>
  );
};
