import React from 'react';
import { MarketEvent, ExecutionTranche } from '@/types';
import { ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';

interface SorTerminalProps {
  markets: Record<string, MarketEvent>;
  selectedMarketKey: string;
  setSelectedMarketKey: (key: string) => void;
  direction: string;
  setDirection: (dir: string) => void;
  notionalUsd: number;
  setNotionalUsd: (size: number) => void;
  polyAmount: number;
  kalshiAmount: number;
  polyPct: number;
  kalshiPct: number;
  effectiveVwap: string;
  capturedAlpha: string;
  slippageBps: string;
  tranches: ExecutionTranche[];
  onOpenDispatch: () => void;
}

export const SorTerminal: React.FC<SorTerminalProps> = ({
  markets,
  selectedMarketKey,
  setSelectedMarketKey,
  direction,
  setDirection,
  notionalUsd,
  setNotionalUsd,
  polyAmount,
  kalshiAmount,
  polyPct,
  kalshiPct,
  effectiveVwap,
  capturedAlpha,
  slippageBps,
  tranches,
  onOpenDispatch,
}) => {
  const directions = ['BUY YES', 'BUY NO', 'SELL YES', 'SELL NO'];
  const sizePresets = [10000, 25000, 50000, 100000, 250000];

  return (
    <div className="space-y-8">
      {/* Top Configuration Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="md:col-span-2">
          <label className="block text-xs uppercase font-bold tracking-wider text-slate-400 mb-2">
            Target Event Contract
          </label>
          <select
            value={selectedMarketKey}
            onChange={(e) => setSelectedMarketKey(e.target.value)}
            className="w-full bg-white/[0.03] hover:bg-white/[0.05] border border-white/[0.08] focus:border-sky-400 rounded-xl px-4 py-3 text-white text-sm font-semibold outline-none cursor-pointer transition-all"
          >
            {Object.entries(markets).map(([key, m]) => (
              <option key={key} value={key} className="bg-[#0b0e14] text-white">
                {m.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs uppercase font-bold tracking-wider text-slate-400 mb-2">
            Direction
          </label>
          <div className="grid grid-cols-2 gap-1.5 bg-white/[0.03] border border-white/[0.08] rounded-xl p-1.5">
            {directions.map((d) => (
              <button
                key={d}
                onClick={() => setDirection(d)}
                className={`py-2 text-xs font-bold rounded-lg transition-all ${
                  direction === d
                    ? 'bg-white/[0.12] text-white shadow-md shadow-black/40'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Giant Tactical Slider */}
      <div className="text-center py-6">
        <span className="text-xs uppercase font-bold tracking-wider text-slate-500">
          Target Notional Order Size
        </span>
        <div className="text-5xl sm:text-6xl font-extrabold font-mono tracking-tight bg-gradient-to-b from-white via-white/95 to-slate-400 bg-clip-text text-transparent my-3">
          ${notionalUsd.toLocaleString()}
        </div>

        <div className="max-w-xl mx-auto px-4">
          <input
            type="range"
            min="2000"
            max="250000"
            step="1000"
            value={notionalUsd}
            onChange={(e) => setNotionalUsd(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-white/[0.1] rounded-lg appearance-none cursor-pointer accent-sky-400 outline-none"
          />
        </div>

        <div className="flex justify-center gap-2 mt-4">
          {sizePresets.map((size) => (
            <button
              key={size}
              onClick={() => setNotionalUsd(size)}
              className="px-3.5 py-1.5 rounded-full text-xs font-mono font-semibold bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.16] text-slate-300 hover:text-white transition-all"
            >
              ${size >= 1000 ? `${size / 1000}k` : size}
            </button>
          ))}
        </div>
      </div>

      {/* Refraction Allocation & TCA Performance */}
      <div className="bg-black/35 border border-white/[0.08] rounded-2xl p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-3 text-sm font-semibold">
          <div className="flex items-center gap-2 text-sky-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-sky-400 shadow-sm shadow-sky-400" />
            <span>Polymarket CLOB:</span>
            <strong className="font-mono text-white font-bold">
              ${polyAmount.toLocaleString()} ({polyPct.toFixed(1)}%)
            </strong>
          </div>
          <div className="flex items-center gap-2 text-amber-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-400 shadow-sm shadow-amber-400" />
            <span>Kalshi CFTC DCM:</span>
            <strong className="font-mono text-white font-bold">
              ${kalshiAmount.toLocaleString()} ({kalshiPct.toFixed(1)}%)
            </strong>
          </div>
        </div>

        <div className="h-3.5 rounded-lg bg-white/[0.05] overflow-hidden flex p-0.5 gap-0.5 mb-6">
          <div
            className="h-full bg-gradient-to-r from-sky-400 to-blue-600 rounded-l-md transition-all duration-300 shadow-md shadow-sky-500/20"
            style={{ width: `${polyPct}%` }}
          />
          <div
            className="h-full bg-gradient-to-r from-amber-400 to-amber-600 rounded-r-md transition-all duration-300 shadow-md shadow-amber-500/20"
            style={{ width: `${kalshiPct}%` }}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-5 border-t border-white/[0.08] text-center">
          <div>
            <div className="text-[11px] uppercase font-bold tracking-wider text-slate-500 mb-1">
              All-In Effective VWAP
            </div>
            <div className="text-2xl font-extrabold font-mono text-white tracking-tight">
              {effectiveVwap}
            </div>
          </div>
          <div>
            <div className="text-[11px] uppercase font-bold tracking-wider text-slate-500 mb-1">
              Captured Execution Alpha
            </div>
            <div className="text-2xl font-extrabold font-mono text-emerald-400 tracking-tight">
              {capturedAlpha}
            </div>
          </div>
          <div>
            <div className="text-[11px] uppercase font-bold tracking-wider text-slate-500 mb-1">
              Slippage Compression
            </div>
            <div className="text-2xl font-extrabold font-mono text-sky-400 tracking-tight">
              {slippageBps}
            </div>
          </div>
        </div>
      </div>

      {/* Execution Tranches Ledger */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.08]">
          <div className="text-sm font-bold text-white tracking-tight">
            Equal-Marginal-Price Waterfill Execution Schedule
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Optimal Sub-Penny Queue Fill</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-slate-400 uppercase tracking-wider font-semibold">
                <th className="text-left py-2.5 px-3">Tranche</th>
                <th className="text-left py-2.5 px-3">Venue</th>
                <th className="py-2.5 px-3">Price</th>
                <th className="py-2.5 px-3">Volume (Shares)</th>
                <th className="py-2.5 px-3">Notional Fill</th>
                <th className="py-2.5 px-3">Marginal VWAP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {tranches.map((t, idx) => (
                <tr key={idx} className="hover:bg-white/[0.02] font-mono transition-colors">
                  <td className="text-left py-3 px-3 text-slate-300 font-sans font-medium">{t.tranche}</td>
                  <td className="text-left py-3 px-3 font-sans font-bold">
                    <span className={t.venue.includes('Polymarket') ? 'text-sky-400' : 'text-amber-400'}>
                      {t.venue}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-300">{t.price}</td>
                  <td className="py-3 px-3 text-slate-300">{t.shares}</td>
                  <td className="py-3 px-3 text-slate-300">{t.notional}</td>
                  <td className="py-3 px-3 text-white font-bold">{t.vwap}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Non-Custodial Dispatch Trigger */}
      <button
        onClick={onOpenDispatch}
        className="w-full bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white font-bold text-sm sm:text-base py-4 rounded-xl shadow-xl shadow-blue-500/25 transition-all flex items-center justify-center gap-2 hover:-translate-y-0.5"
      >
        <ShieldCheck className="w-5 h-5" />
        <span>Review Pre-Signed Cryptographic Dispatch</span>
        <span className="text-xs opacity-75 font-normal">(EIP-712 & CFTC DCM)</span>
        <ArrowRight className="w-4 h-4 ml-1 opacity-80" />
      </button>
    </div>
  );
};
