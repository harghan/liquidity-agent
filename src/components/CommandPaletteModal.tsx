import React, { useEffect, useRef, useState } from 'react';
import { Sparkles, Command, ArrowRight, ShieldCheck, BarChart3, Terminal } from 'lucide-react';

interface CommandPaletteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPrompt: (prompt: string) => void;
  onSelectTab: (tabId: string) => void;
}

export const CommandPaletteModal: React.FC<CommandPaletteModalProps> = ({
  isOpen,
  onClose,
  onSelectPrompt,
  onSelectTab,
}) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const items = [
    {
      title: 'Refract $50,000 into Vivek Ramaswamy 2028',
      type: 'AI Mandate',
      action: () => {
        onSelectPrompt('Deploy $50k on Vivek Ramaswamy with < 15 bps slippage');
        onClose();
      },
    },
    {
      title: 'Sweep $75,000 into FOMC Rate Decision',
      type: 'AI Mandate',
      action: () => {
        onSelectPrompt('Sweep $75k into FOMC July Rate Decision immediately');
        onClose();
      },
    },
    {
      title: 'Fade US Recession 2026 ($35k Iceberg)',
      type: 'AI Mandate',
      action: () => {
        onSelectPrompt('Fade US Recession 2026 with $35k staggered iceberg cadence');
        onClose();
      },
    },
    {
      title: 'Deploy $100,000 into Tim Walz 2028',
      type: 'AI Mandate',
      action: () => {
        onSelectPrompt('Deploy $100k on Tim Walz 2028 with maximum 20 bps slippage');
        onClose();
      },
    },
    {
      title: 'Navigate to Flagship Overview',
      type: 'Navigation',
      action: () => {
        onSelectTab('overview');
        onClose();
      },
    },
    {
      title: 'Launch Terminal (SOR Workstation · 60+ Live Bets)',
      type: 'Navigation',
      action: () => {
        onSelectTab('terminal');
        onClose();
      },
    },
    {
      title: 'Navigate to Synthetic Parity Radar vs SOFR',
      type: 'Navigation',
      action: () => {
        onSelectTab('parity');
        onClose();
      },
    },
    {
      title: 'Navigate to Oracle Resolution Auditor & Conflict Guard',
      type: 'Navigation',
      action: () => {
        onSelectTab('auditor');
        onClose();
      },
    },
    {
      title: 'Inspect Cross-Venue Microstructure Depth (L2/L3)',
      type: 'Navigation',
      action: () => {
        onSelectTab('depth');
        onClose();
      },
    },
    {
      title: 'Open Pre-Trade TCA Shortfall Analytics',
      type: 'Navigation',
      action: () => {
        onSelectTab('analytics');
        onClose();
      },
    },
    {
      title: 'View Institutional Commercial Pricing Tiers',
      type: 'Navigation',
      action: () => {
        onSelectTab('pricing');
        onClose();
      },
    },
    {
      title: 'Inspect Developer API & Non-Custodial SDK',
      type: 'Navigation',
      action: () => {
        onSelectTab('api');
        onClose();
      },
    },
  ];

  const filtered = items.filter((item) =>
    item.title.toLowerCase().includes(query.toLowerCase()) ||
    item.type.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#0d1118] border border-white/[0.16] rounded-2xl w-full max-w-xl shadow-2xl shadow-black/90 overflow-hidden">
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/[0.08]">
          <Sparkles className="w-5 h-5 text-sky-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') onClose();
              if (e.key === 'Enter' && filtered.length > 0) {
                filtered[0].action();
              }
            }}
            placeholder="Type an AI trading mandate or navigation command..."
            className="flex-1 bg-transparent text-white placeholder-slate-500 text-sm outline-none font-medium"
          />
          <kbd className="bg-white/[0.08] border border-white/[0.12] px-2 py-0.5 rounded text-[10px] font-mono font-bold text-slate-300">
            ESC
          </kbd>
        </div>

        {/* Action Results */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500 font-mono">
              Press Enter to run mandate: "{query}"
            </div>
          ) : (
            filtered.map((item, idx) => (
              <div
                key={idx}
                onClick={item.action}
                className="flex items-center justify-between px-3.5 py-2.5 rounded-xl hover:bg-white/[0.08] text-slate-300 hover:text-white cursor-pointer transition-colors group"
              >
                <div className="flex items-center gap-2.5 text-xs font-medium">
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 transition-colors" />
                  <span>{item.title}</span>
                </div>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-white/[0.04] text-slate-400">
                  {item.type}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
