import React, { useState } from 'react';
import { Sparkles, CornerDownLeft, Zap, Landmark, TrendingDown, Target, ShieldCheck, Loader2 } from 'lucide-react';
import { MicrostructureSignals } from '@/types';

interface AiMandateBarProps {
  onExecutePrompt: (prompt: string) => Promise<void>;
  signals: MicrostructureSignals | null;
  rationale: string | null;
  preSignedHash: string | null;
  loading: boolean;
}

export const AiMandateBar: React.FC<AiMandateBarProps> = ({
  onExecutePrompt,
  signals,
  rationale,
  preSignedHash,
  loading,
}) => {
  const [inputVal, setInputVal] = useState('');

  const presets = [
    { label: '$50k Vivek Sweep', prompt: 'Deploy $50k on Vivek Ramaswamy with < 15 bps slippage', icon: Zap },
    { label: '$75k FOMC Sweep', prompt: 'Sweep $75k into FOMC July Rate Decision immediately', icon: Landmark },
    { label: '$35k Fade Recession', prompt: 'Fade US Recession 2026 with $35k staggered iceberg cadence', icon: TrendingDown },
    { label: '$100k Tim Walz', prompt: 'Deploy $100k on Tim Walz 2028 with maximum 20 bps slippage', icon: Target },
  ];

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (inputVal.trim()) {
      onExecutePrompt(inputVal.trim());
    }
  };

  const handlePresetClick = (prompt: string) => {
    setInputVal(prompt);
    onExecutePrompt(prompt);
  };

  return (
    <div className="mb-8">
      {/* Spotlight Mandate Bar */}
      <form
        onSubmit={handleSubmit}
        className="relative flex items-center gap-3 bg-gradient-to-r from-white/[0.08] to-white/[0.02] border border-white/[0.16] focus-within:border-sky-400/60 rounded-2xl px-4 py-2.5 shadow-2xl shadow-black/80 backdrop-blur-2xl transition-all hover:border-white/[0.24]"
      >
        <Sparkles className="w-5 h-5 text-sky-400 shrink-0 animate-pulse" />
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Instruct PRISM AI: e.g. 'Deploy $75k into Vivek 2028 with < 15 bps slippage' (or press ⌘K)"
          className="flex-1 bg-transparent text-white placeholder-slate-500 text-sm md:text-base outline-none font-medium"
        />
        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-1.5 bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-all shadow-md shadow-blue-500/20 disabled:opacity-50 shrink-0"
        >
          {loading ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <>
              <span>Refract with AI</span>
              <CornerDownLeft className="w-3 h-3 opacity-70" />
            </>
          )}
        </button>
      </form>

      {/* Quick Prompt Presets */}
      <div className="flex flex-wrap items-center gap-2 mt-3 text-xs">
        <span className="text-[11px] font-bold tracking-wider uppercase text-slate-500 mr-1">PRESETS:</span>
        {presets.map((p, i) => {
          const Icon = p.icon;
          return (
            <button
              key={i}
              onClick={() => handlePresetClick(p.prompt)}
              className="flex items-center gap-1.5 bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.08] hover:border-sky-400/30 text-slate-400 hover:text-white px-3 py-1.5 rounded-full font-mono transition-all"
            >
              <Icon className="w-3 h-3 text-sky-400 opacity-70" />
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Autonomous AI Telemetry Drawer */}
      {(rationale || signals) && (
        <div className="mt-5 bg-[#0e121b]/90 border border-sky-400/30 rounded-2xl p-5 md:p-6 backdrop-blur-2xl shadow-xl shadow-black/60 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-white/[0.08]">
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-sky-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-sky-100">
                PRISM AI Microstructure Intelligence
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                ACTIVE MANDATE
              </span>
            </div>
            {preSignedHash && (
              <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
                <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
                <span>HASH: {preSignedHash.slice(0, 16)}...</span>
              </div>
            )}
          </div>

          {rationale && (
            <div className="bg-black/30 border border-white/[0.08] rounded-xl p-4 text-slate-200 text-sm leading-relaxed mb-4 font-normal">
              {rationale}
            </div>
          )}

          {signals && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3">
                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1">
                  Order Book Imbalance (OBI)
                </div>
                <div className={`text-base font-bold font-mono ${signals.orderBookImbalance >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {signals.orderBookImbalance >= 0 ? `+${signals.orderBookImbalance}` : signals.orderBookImbalance}
                </div>
              </div>

              <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3">
                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1">
                  Microprice Drift
                </div>
                <div className="text-base font-bold font-mono text-slate-200">
                  {signals.micropriceDriftBps >= 0 ? `+${signals.micropriceDriftBps}` : signals.micropriceDriftBps} bps
                </div>
              </div>

              <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3">
                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1">
                  Kyle's λ Impact
                </div>
                <div className="text-base font-bold font-mono text-sky-400">
                  {signals.predictedImpactBps} bps
                </div>
              </div>

              <div className="bg-white/[0.02] border border-white/[0.08] rounded-xl p-3">
                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1">
                  Execution Cadence
                </div>
                <div className="text-base font-bold font-mono text-amber-400">
                  {signals.recommendedCadence}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
