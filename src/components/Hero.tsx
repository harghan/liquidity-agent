import React from 'react';
import { Sparkles, ArrowRight, Gauge, Zap, Lock, DollarSign } from 'lucide-react';

interface HeroProps {
  onOpenCmd: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onOpenCmd }) => {
  return (
    <div className="text-center mb-10 md:mb-12">
      <div 
        onClick={onOpenCmd}
        className="inline-flex items-center gap-2 bg-sky-500/[0.08] hover:bg-sky-500/[0.14] border border-sky-500/25 hover:border-sky-500/40 rounded-full px-4 py-1.5 text-xs font-semibold text-sky-400 mb-6 cursor-pointer transition-all hover:-translate-y-0.5"
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span>PRISM Autonomous AI Engine v2.4 Live · Polymarket & Kalshi Synced</span>
        <ArrowRight className="w-3.5 h-3.5 opacity-70" />
      </div>

      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tighter max-w-4xl mx-auto leading-[1.1] mb-5 bg-gradient-to-b from-white via-white/90 to-slate-400 bg-clip-text text-transparent">
        Refract Institutional Size Across Fragmented Venues.
      </h1>

      <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed mb-10">
        The non-custodial Smart Order Router (SOR) and autonomous microstructure execution engine for event derivatives. Eliminates the 84x single-venue slippage cliff via discrete equal-marginal-price waterfilling.
      </p>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 max-w-3xl mx-auto text-left">
        <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3.5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400 font-medium">Ingested Depth</span>
            <DollarSign className="w-4 h-4 text-sky-400 opacity-60" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white tracking-tight">$4.8B+</div>
        </div>

        <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3.5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400 font-medium">Slippage Compression</span>
            <Gauge className="w-4 h-4 text-emerald-400 opacity-60" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white tracking-tight">84x</div>
        </div>

        <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3.5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400 font-medium">Waterfill Latency</span>
            <Zap className="w-4 h-4 text-amber-400 opacity-60" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white tracking-tight">0.34ms</div>
        </div>

        <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3.5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-400 font-medium">Custody Risk</span>
            <Lock className="w-4 h-4 text-purple-400 opacity-60" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white tracking-tight">Zero (EIP-712)</div>
        </div>
      </div>
    </div>
  );
};
