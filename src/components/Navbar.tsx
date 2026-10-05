import React from 'react';
import { Layers, Activity, Terminal, ShieldCheck, BarChart3, Code2, Command } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenCmd: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onOpenCmd }) => {
  const tabs = [
    { id: 'terminal', label: 'Terminal (SOR)', icon: Terminal },
    { id: 'parity', label: 'Parity Radar', icon: ShieldCheck },
    { id: 'depth', label: 'Microstructure Depth', icon: BarChart3 },
    { id: 'analytics', label: 'TCA Analytics', icon: Activity },
    { id: 'api', label: 'Developer API', icon: Code2 },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-2xl bg-[#060709]/80 border-b border-white/[0.08] px-6 md:px-8 h-16 flex items-center justify-between transition-colors">
      <div 
        className="flex items-center gap-3 cursor-pointer group"
        onClick={() => setActiveTab('terminal')}
      >
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-400 via-blue-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
          <Layers className="w-4 h-4" />
        </div>
        <div className="flex items-center gap-2">
          <span className="font-extrabold tracking-tight text-white text-base">PRISM</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-white/[0.05] border border-white/[0.08] text-slate-400">
            v2.4 Pro
          </span>
        </div>
      </div>

      <nav className="hidden lg:flex items-center bg-white/[0.03] border border-white/[0.08] rounded-xl p-1 gap-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-white/[0.1] text-white shadow-sm shadow-black/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse" />
          <span>0.34ms Waterfill</span>
        </div>

        <button
          onClick={onOpenCmd}
          className="flex items-center gap-2 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.16] text-slate-300 text-xs px-3 py-1.5 rounded-lg transition-all"
        >
          <Command className="w-3.5 h-3.5 text-slate-400" />
          <span className="hidden sm:inline">Mandate</span>
          <kbd className="bg-white/[0.08] border border-white/[0.12] px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-slate-200">
            ⌘K
          </kbd>
        </button>
      </div>
    </header>
  );
};
