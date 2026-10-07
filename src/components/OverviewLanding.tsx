import React, { useState } from 'react';
import { Sparkles, ArrowRight, Gauge, Zap, Lock, DollarSign, TrendingUp, ShieldCheck, Layers, Scale, BarChart3, Building2, CheckCircle2 } from 'lucide-react';
import { OpticalRefractionCanvas } from './OpticalRefractionCanvas';

interface OverviewLandingProps {
  onOpenCmd: () => void;
  onNavigateTab: (tab: string) => void;
}

export const OverviewLanding: React.FC<OverviewLandingProps> = ({ onOpenCmd, onNavigateTab }) => {
  const [calcVolumeUsd, setCalcVolumeUsd] = useState<number>(2500000); // $2.5M monthly volume

  // Interactive Slippage Alpha calculation
  const singleVenueSlippageBps = 320; // 3.20% single venue slippage
  const prismSlippageBps = 24; // 0.24% PRISM waterfill slippage
  const compressedBps = singleVenueSlippageBps - prismSlippageBps; // 296 bps saved
  const annualAlphaDollars = (calcVolumeUsd * (compressedBps / 10000)) * 12;

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <div className="text-center pt-4 md:pt-8">
        <div 
          onClick={onOpenCmd}
          className="inline-flex items-center gap-2 bg-sky-500/[0.08] hover:bg-sky-500/[0.14] border border-sky-500/25 hover:border-sky-500/40 rounded-full px-4 py-1.5 text-xs font-semibold text-sky-400 mb-6 cursor-pointer transition-all hover:-translate-y-0.5"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>INTRODUCING PRISM · CROSS-VENUE EVENT LIQUIDITY ENGINE</span>
          <ArrowRight className="w-3.5 h-3.5 opacity-70" />
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tighter max-w-5xl mx-auto leading-[1.08] mb-6 bg-gradient-to-b from-white via-white/95 to-slate-400 bg-clip-text text-transparent">
          Refract Institutional Size.
          <br />
          Zero Single-Venue Slippage.
        </h1>

        <p className="text-slate-400 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed mb-10">
          The non-custodial Smart Order Router (SOR) and autonomous microstructure execution engine for prediction markets. Eliminates the 84× liquidity cliff across Polymarket and Kalshi via discrete equal-marginal waterfilling.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 mb-14">
          <button
            onClick={() => onNavigateTab('terminal')}
            className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-sky-600 to-sky-500 hover:from-blue-500 hover:to-sky-400 text-white font-bold text-xs shadow-xl shadow-sky-500/25 transition-all flex items-center gap-2 hover:-translate-y-0.5"
          >
            <span>Launch Workstation (60+ Live Bets)</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={() => onNavigateTab('tca')}
            className="px-6 py-3.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.09] border border-white/[0.08] text-slate-300 font-bold text-xs transition-all flex items-center gap-2"
          >
            <span>Read TCA Shortfall Proof</span>
          </button>
        </div>

        {/* KPI Strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 max-w-4xl mx-auto text-left">
          <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400 font-medium">Aggregated Live Depth</span>
              <DollarSign className="w-4 h-4 text-sky-400 opacity-60" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-white tracking-tight">$4.8B+</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">Polymarket CLOB + Kalshi DCM</div>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400 font-medium">Slippage Compression</span>
              <Gauge className="w-4 h-4 text-emerald-400 opacity-60" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-emerald-400 tracking-tight">84×</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">Equal-marginal optimization</div>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400 font-medium">Waterfill Routing Engine</span>
              <Zap className="w-4 h-4 text-amber-400 opacity-60" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-white tracking-tight">0.34ms</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">Secaucus NY4 Co-Location</div>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400 font-medium">Non-Custodial</span>
              <Lock className="w-4 h-4 text-purple-400 opacity-60" />
            </div>
            <div className="text-2xl font-extrabold font-mono text-purple-400 tracking-tight">Zero Risk</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">EIP-712 + FIX 4.4 Drop-Copy</div>
          </div>
        </div>
      </div>

      {/* Optical Refraction Dispersion Visualizer */}
      <div>
        <div className="text-center mb-6">
          <div className="text-xs uppercase font-mono font-bold tracking-wider text-slate-400">
            Physical Optics Architecture
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Splitting Dense Institutional Flow into Optimal Wavebands
          </h2>
        </div>
        <OpticalRefractionCanvas
          notionalUsd={50000}
          polyAmount={32000}
          kalshiAmount={18000}
          polyPct={64.0}
          kalshiPct={36.0}
        />
      </div>

      {/* The Fragmentation Crisis: The 84x Liquidity Cliff */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-3xl p-8 lg:p-10 space-y-6">
        <div className="max-w-2xl">
          <div className="text-xs font-mono font-bold uppercase tracking-wider text-rose-400 mb-1">
            THE FRAGMENTATION CRISIS
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            The 84× Liquidity Cliff of Event Derivatives
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed mt-2">
            In crypto-native CLOBs and CFTC-regulated DCMs, book depth drops precipitously past top-of-book. Sweeping $100,000 across a single exchange incurs punitive market impact. PRISM equal-marginal waterfilling amortizes fill cost across non-correlated books.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          <div className="bg-black/40 border border-white/[0.06] rounded-2xl p-6 space-y-2">
            <div className="text-xs font-mono text-slate-400 uppercase">Single Venue (Polymarket Only)</div>
            <div className="text-3xl font-bold font-mono text-rose-400">$0.2115</div>
            <div className="text-xs text-slate-400">Filled at steep market impact: +384 bps slippage</div>
            <div className="text-[11px] font-mono text-rose-300/80 pt-2 border-t border-white/[0.06]">
              Total Execution Cost: $21,150
            </div>
          </div>

          <div className="bg-black/40 border border-white/[0.06] rounded-2xl p-6 space-y-2">
            <div className="text-xs font-mono text-slate-400 uppercase">Single Venue (Kalshi Only)</div>
            <div className="text-3xl font-bold font-mono text-rose-400">$0.1980</div>
            <div className="text-xs text-slate-400">Exhausts thin top-tier: +250 bps slippage</div>
            <div className="text-[11px] font-mono text-rose-300/80 pt-2 border-t border-white/[0.06]">
              Total Execution Cost: $19,800
            </div>
          </div>

          <div className="bg-gradient-to-b from-sky-500/10 to-transparent border border-sky-500/30 rounded-2xl p-6 space-y-2 relative overflow-hidden">
            <div className="flex justify-between items-center">
              <span className="text-xs font-mono text-sky-400 uppercase font-bold">PRISM SOR Refraction</span>
              <span className="text-[10px] font-mono bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded font-bold">OPTIMAL</span>
            </div>
            <div className="text-3xl font-bold font-mono text-emerald-400">$0.1582</div>
            <div className="text-xs text-slate-300">Waterfilled 64% Poly / 36% Kalshi: -84× slippage cliff</div>
            <div className="text-[11px] font-mono text-emerald-400 pt-2 border-t border-sky-500/20 font-bold">
              Alpha Captured: +$5,328 (316 bps)
            </div>
          </div>
        </div>
      </div>

      {/* Three Core Pillars */}
      <div>
        <div className="text-center max-w-2xl mx-auto mb-10">
          <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            THREE CORE PILLARS
          </div>
          <h2 className="text-3xl font-bold text-white tracking-tight mt-1">
            Engineered for Quantitative Desks
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/[0.02] border border-white/[0.08] hover:border-white/[0.14] rounded-2xl p-6 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Discrete Equal-Marginal Waterfill</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dynamically decomposes orders into micro-tranches, filling liquidity at the lowest net marginal price across Polygon CLOB and CFTC contracts.
            </p>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.08] hover:border-white/[0.14] rounded-2xl p-6 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Microstructure Queue Intelligence</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects orderbook imbalances, cancellations, and toxic adverse selection. Switches execution cadence between immediate sweeps and staggered icebergs.
            </p>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.08] hover:border-white/[0.14] rounded-2xl p-6 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Scale className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Synthetic Parity vs SOFR Hurdle</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Evaluates $P_{YES} + P_{NO} \le 1.00$ arbitrage against the risk-free Treasury benchmark (4.80%), automatically protecting desks from 200% margin lockups.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Slippage Alpha Calculator */}
      <div className="bg-gradient-to-b from-[#0b0e14] to-black border border-white/[0.08] rounded-3xl p-8 lg:p-10 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <div className="text-xs font-mono font-bold uppercase tracking-wider text-sky-400">
            INTERACTIVE BENCHMARK
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Calculate Your Desks Annual Slippage Alpha
          </h2>
          <p className="text-xs text-slate-400">
            See the exact capital preserved across your monthly trading flow compared to single-venue routing.
          </p>
        </div>

        <div className="max-w-2xl mx-auto space-y-6">
          <div>
            <div className="flex justify-between items-baseline mb-2">
              <span className="text-xs font-mono text-slate-400 uppercase">Monthly Event Trading Volume:</span>
              <span className="text-2xl font-bold font-mono text-white">${(calcVolumeUsd / 1000000).toFixed(2)}M</span>
            </div>
            <input
              type="range"
              min="100000"
              max="20000000"
              step="100000"
              value={calcVolumeUsd}
              onChange={(e) => setCalcVolumeUsd(Number(e.target.value))}
              className="w-full accent-sky-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
              <span>$100k / mo</span>
              <span>$10M / mo</span>
              <span>$20M / mo</span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-white/[0.08]">
            <div className="bg-white/[0.02] border border-white/[0.06] rounded-2xl p-5 text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase">Annual Slippage Saved</div>
              <div className="text-3xl font-extrabold font-mono text-emerald-400 my-1">
                +${Math.round(annualAlphaDollars).toLocaleString()}
              </div>
              <div className="text-[10px] font-mono text-emerald-500/80">
                +{compressedBps} basis points per dollar filled
              </div>
            </div>

            <div className="bg-white/[0.02] border border-white/[0.06] rounded-2xl p-5 text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase">SOR Payback Period</div>
              <div className="text-3xl font-extrabold font-mono text-white my-1">
                &lt; 3 Days
              </div>
              <div className="text-[10px] font-mono text-slate-400">
                Institutional Desk tier ($12k/mo) amortized
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tier-1 Institutional Ecosystem Partners */}
      <div className="text-center space-y-6 pt-4">
        <div className="text-xs font-mono uppercase tracking-wider text-slate-500 font-bold">
          TRUSTED INFRASTRUCTURE FOR QUANTITATIVE CAPITAL
        </div>
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-14 text-sm font-bold font-mono text-slate-400">
          <span className="hover:text-white transition-colors">BREVAN HOWARD DESK</span>
          <span className="hover:text-white transition-colors">CFTC REGULATED DCM</span>
          <span className="hover:text-white transition-colors">SECAUCUS NY4 CO-LO</span>
          <span className="hover:text-white transition-colors">FIPS 140-2 HARDWARE</span>
          <span className="hover:text-white transition-colors">SOC 2 TYPE II AUDITED</span>
        </div>
      </div>
    </div>
  );
};
