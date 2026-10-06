import React, { useState, useMemo } from 'react';
import { MarketEvent, ExecutionTranche } from '@/types';
import { ShieldCheck, ArrowRight, CheckCircle2, Search, TrendingUp, Sparkles, Activity } from 'lucide-react';

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
  isLoadingMarkets?: boolean;
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
  isLoadingMarkets = false,
}) => {
  const directions = ['BUY YES', 'BUY NO', 'SELL YES', 'SELL NO'];
  const sizePresets = [10000, 25000, 50000, 100000, 250000];

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = [
    { id: 'ALL', label: 'All Live Bets' },
    { id: 'HOT', label: '🔥 Top Volume ($20M+)' },
    { id: 'Politics & 2028', label: '🏛️ Politics & 2028' },
    { id: 'Macro & Fed', label: '🏦 Macro & Fed' },
    { id: 'Geopolitics & Defense', label: '🌐 Geopolitics' },
    { id: 'Crypto & Tech', label: '⚡ Crypto & Tech' },
  ];

  const marketList = useMemo(() => Object.entries(markets), [markets]);

  const filteredMarkets = useMemo(() => {
    return marketList.filter(([_, m]) => {
      // Category filter
      if (selectedCategory === 'HOT') {
        if ((m.volumeUsd || 0) < 20000000) return false;
      } else if (selectedCategory !== 'ALL') {
        if (m.category !== selectedCategory) return false;
      }

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesName = m.name.toLowerCase().includes(query);
        const matchesCat = m.category.toLowerCase().includes(query);
        return matchesName || matchesCat;
      }

      return true;
    });
  }, [marketList, selectedCategory, searchQuery]);

  const currentMarket = markets[selectedMarketKey] || marketList[0]?.[1] || {
    id: 'default',
    name: 'Prediction Market Contract',
    category: 'Global Events',
    polyMid: 0.5,
    kalshiMid: 0.48,
    baseVwap: 0.49,
    liquidityUsd: 5000000,
    volumeUsd: 20000000,
    spreadBps: 200,
  };

  return (
    <div className="space-y-8">
      {/* Live Market Universe Explorer Header */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-5 md:p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-white">
              Live Prediction Market Universe
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-semibold">
              {marketList.length} Live Contracts Tracked
            </span>
            {isLoadingMarkets && (
              <span className="text-[10px] text-sky-400 font-mono animate-pulse">Syncing CLOB orderbooks...</span>
            )}
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
            <span>Polymarket Gamma CLOB</span>
            <span>·</span>
            <span>Kalshi CFTC DCM</span>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === c.id
                  ? 'bg-sky-500/20 border border-sky-400/40 text-sky-300 shadow-sm'
                  : 'bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] text-slate-400 hover:text-slate-200'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        {/* Search Bar + Live Dropdown Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2 space-y-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search 60+ live bets (e.g. Iran, Fed Rate, Bitcoin, Vivek, Trump, Tariffs, Ceasefire)..."
                className="w-full bg-white/[0.03] hover:bg-white/[0.05] focus:bg-white/[0.06] border border-white/[0.08] focus:border-sky-400 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 outline-none transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-2.5 text-[11px] text-slate-400 hover:text-white px-1.5 py-0.5 rounded bg-white/[0.06]"
                >
                  Clear
                </button>
              )}
            </div>

            <div className="relative">
              <select
                value={selectedMarketKey}
                onChange={(e) => setSelectedMarketKey(e.target.value)}
                className="w-full bg-[#0b0e14] hover:bg-white/[0.05] border border-white/[0.1] focus:border-sky-400 rounded-xl px-4 py-3 text-white text-xs font-semibold outline-none cursor-pointer transition-all truncate"
              >
                {filteredMarkets.length === 0 ? (
                  <option disabled value="">No matching prediction markets found</option>
                ) : (
                  filteredMarkets.map(([key, m]) => (
                    <option key={key} value={key} className="bg-[#0b0e14] text-white py-1">
                      [{m.category}] {m.name} — Poly: ${(m.polyMid).toFixed(3)} | Kalshi: ${(m.kalshiMid).toFixed(3)} (Spread: +{m.spreadBps || 200} bps | Vol: ${((m.volumeUsd || 10000000) / 1000000).toFixed(1)}M)
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* Direction Selector */}
          <div>
            <label className="block text-[11px] uppercase font-bold tracking-wider text-slate-400 mb-1.5">
              Execution Direction
            </label>
            <div className="grid grid-cols-2 gap-1.5 bg-white/[0.03] border border-white/[0.08] rounded-xl p-1.5">
              {directions.map((d) => (
                <button
                  key={d}
                  onClick={() => setDirection(d)}
                  className={`py-2 text-xs font-bold rounded-lg transition-all ${
                    direction === d
                      ? 'bg-sky-500/20 border border-sky-400/40 text-sky-300 shadow-md shadow-black/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Live Contract Active Card */}
        <div className="bg-gradient-to-r from-sky-500/[0.05] via-purple-500/[0.03] to-transparent border border-white/[0.08] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1 max-w-xl">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/20 text-sky-400">
                {currentMarket.category}
              </span>
              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <Activity className="w-3 h-3" /> Live Cross-Venue Routing Active
              </span>
            </div>
            <div className="text-sm font-bold text-white tracking-tight">
              {currentMarket.name}
            </div>
          </div>

          <div className="flex items-center gap-4 text-right">
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400">Polymarket Mid</div>
              <div className="text-sm font-bold font-mono text-sky-400">
                ${currentMarket.polyMid.toFixed(4)}
              </div>
            </div>
            <div className="h-6 w-px bg-white/[0.08]" />
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400">Kalshi Mid</div>
              <div className="text-sm font-bold font-mono text-amber-400">
                ${currentMarket.kalshiMid.toFixed(4)}
              </div>
            </div>
            <div className="h-6 w-px bg-white/[0.08]" />
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400">24h Vol</div>
              <div className="text-sm font-bold font-mono text-white">
                ${((currentMarket.volumeUsd || 15000000) / 1000000).toFixed(1)}M
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Giant Tactical Notional Slider */}
      <div className="text-center py-6 bg-white/[0.01] border border-white/[0.05] rounded-2xl">
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
            onChange={(e) => setNotionalUsd(Number(e.target.value))}
            className="w-full accent-sky-500 cursor-pointer"
          />
        </div>

        <div className="flex flex-wrap justify-center gap-2 mt-4">
          {sizePresets.map((size) => (
            <button
              key={size}
              onClick={() => setNotionalUsd(size)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
                notionalUsd === size
                  ? 'bg-sky-500/20 border border-sky-400/40 text-sky-300'
                  : 'bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.08] text-slate-400'
              }`}
            >
              ${(size / 1000).toFixed(0)}k
            </button>
          ))}
        </div>
      </div>

      {/* Dual Allocation Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#0b0e14] border border-sky-500/20 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-sky-500/10 rounded-full blur-2xl pointer-events-none" />
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-sky-400" />
              <span className="text-sm font-bold text-white">POLYMARKET CLOB</span>
            </div>
            <span className="text-xs font-mono font-bold text-sky-400">
              {polyPct.toFixed(1)}% Allocation
            </span>
          </div>

          <div className="text-3xl font-extrabold font-mono text-white mb-1">
            ${polyAmount.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 font-mono mb-4">
            Shares: ~{Math.round(polyAmount / currentMarket.polyMid).toLocaleString()} @ Mid ${currentMarket.polyMid.toFixed(4)}
          </div>

          <div className="text-xs text-slate-400 space-y-1 border-t border-white/[0.06] pt-3">
            <div className="flex justify-between">
              <span>Resting Depth:</span>
              <span className="font-mono text-white">${(currentMarket.liquidityUsd * 0.65).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Settlement:</span>
              <span className="font-mono text-slate-300">Polygon USDC · EIP-712</span>
            </div>
          </div>
        </div>

        <div className="bg-[#0b0e14] border border-amber-500/20 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <span className="text-sm font-bold text-white">KALSHI CFTC DCM</span>
            </div>
            <span className="text-xs font-mono font-bold text-amber-400">
              {kalshiPct.toFixed(1)}% Allocation
            </span>
          </div>

          <div className="text-3xl font-extrabold font-mono text-white mb-1">
            ${kalshiAmount.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 font-mono mb-4">
            Shares: ~{Math.round(kalshiAmount / currentMarket.kalshiMid).toLocaleString()} @ Mid ${currentMarket.kalshiMid.toFixed(4)}
          </div>

          <div className="text-xs text-slate-400 space-y-1 border-t border-white/[0.06] pt-3">
            <div className="flex justify-between">
              <span>Resting Depth:</span>
              <span className="font-mono text-white">${(currentMarket.liquidityUsd * 0.35).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Settlement:</span>
              <span className="font-mono text-slate-300">CFTC Clearinghouse · USD Cash</span>
            </div>
          </div>
        </div>
      </div>

      {/* TCA Output Summary Bar */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-xs uppercase font-bold text-slate-400 mb-1">Blended Net VWAP</div>
            <div className="text-2xl font-bold font-mono text-white">${effectiveVwap}</div>
            <div className="text-[11px] text-slate-500 font-mono">Equal-marginal refactored</div>
          </div>

          <div>
            <div className="text-xs uppercase font-bold text-slate-400 mb-1">Captured Alpha</div>
            <div className="text-2xl font-bold font-mono text-emerald-400">{capturedAlpha}</div>
            <div className="text-[11px] text-slate-500 font-mono">vs single-venue sweep</div>
          </div>

          <div>
            <div className="text-xs uppercase font-bold text-slate-400 mb-1">Simulated Slippage</div>
            <div className="text-2xl font-bold font-mono text-sky-400">{slippageBps}</div>
            <div className="text-[11px] text-slate-500 font-mono">Order impact mitigation</div>
          </div>
        </div>
      </div>

      {/* Live Tranches Execution Schedule */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm font-bold text-white">Dynamic Tranches Schedule</div>
          <div className="text-xs text-slate-500 font-mono">Sorted by net marginal cost</div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-slate-400 uppercase tracking-wider font-semibold">
                <th className="text-left py-2.5 px-3">Tranche</th>
                <th className="text-left py-2.5 px-3">Venue</th>
                <th className="py-2.5 px-3">Price</th>
                <th className="py-2.5 px-3">Shares</th>
                <th className="py-2.5 px-3">Notional</th>
                <th className="py-2.5 px-3">Cum. VWAP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03] font-mono">
              {tranches.map((t, idx) => (
                <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                  <td className="text-left py-3 px-3 font-semibold text-white">{t.tranche}</td>
                  <td className="text-left py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        t.venue.includes('Polymarket')
                          ? 'bg-sky-500/10 border border-sky-500/20 text-sky-400'
                          : 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                      }`}
                    >
                      {t.venue}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-200">${t.price}</td>
                  <td className="py-3 px-3 text-slate-300">{t.shares}</td>
                  <td className="py-3 px-3 font-semibold text-white">{t.notional}</td>
                  <td className="py-3 px-3 text-emerald-400">${t.vwap}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dispatch Order Button */}
      <div className="pt-2">
        <button
          onClick={onOpenDispatch}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 via-sky-600 to-sky-500 hover:from-blue-500 hover:to-sky-400 text-white font-bold text-sm shadow-xl shadow-sky-500/20 transition-all flex items-center justify-center gap-2 hover:-translate-y-0.5"
        >
          <span>Dispatch Split Order (${notionalUsd.toLocaleString()} {direction})</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
