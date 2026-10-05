import React from 'react';
import { BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';

export const DepthVisualizer: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.08]">
          <div>
            <div className="text-base font-bold text-white tracking-tight">
              Cross-Venue Orderbook Depth & Liquidity Cliff Radar
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Comparing cumulative ask depth and marginal slippage slopes across venues
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Streaming L2/L3 Book Walker</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {/* Polymarket Card */}
          <div className="bg-sky-500/[0.03] border border-sky-500/20 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-bold text-sky-400">Polymarket CLOB (Polygon)</span>
              <span className="text-xs font-mono text-slate-400">$21.4M Volume</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Deep, continuous institutional liquidity pool with tight spreads. Low price-impact elasticity: sweeps up to $100k absorb smoothly with gradual linear impact.
            </p>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-400">
                <span>$25k Sweep VWAP</span>
                <span className="text-white font-bold">0.0493 (+24 bps)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>$100k Sweep VWAP</span>
                <span className="text-white font-bold">0.0665 (+145 bps)</span>
              </div>
            </div>
          </div>

          {/* Kalshi Card */}
          <div className="bg-amber-500/[0.03] border border-amber-500/20 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-bold text-amber-400">Kalshi CFTC DCM (Secaucus)</span>
              <span className="text-xs font-mono text-slate-400">$12.8M Volume</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Tight top-of-book pricing but exhibits severe non-linear liquidity cliffs past $15k notional (84x price blowup observed in $100k sweeps). PRISM prevents sweeping past this threshold.
            </p>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-400">
                <span>$25k Sweep VWAP</span>
                <span className="text-amber-400 font-bold">0.0843 (+320 bps)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>$100k Sweep VWAP</span>
                <span className="text-rose-400 font-bold">0.2115 (+8,360 bps CLIFF)</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-4 text-xs text-slate-400 leading-relaxed flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-sky-400 shrink-0" />
          <span>
            <strong>Smart Order Routing Alpha:</strong> By routing 69.3% to Polymarket and 30.7% to Kalshi, PRISM stops sweeping Kalshi exactly at the marginal cost intersection where Kalshi taker fees and spread blowup exceed Polymarket's deeper levels.
          </span>
        </div>
      </div>
    </div>
  );
};
