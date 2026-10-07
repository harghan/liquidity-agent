import React, { useState } from 'react';
import { 
  Layers, 
  Activity, 
  Terminal, 
  ShieldCheck, 
  BarChart3, 
  Code2, 
  Command, 
  LogOut, 
  Sparkles, 
  Scale, 
  DollarSign, 
  Menu, 
  X,
  ChevronRight
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenCmd: () => void;
  authenticatedDesk?: string | null;
  onLogout?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenCmd,
  authenticatedDesk,
  onLogout,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Sparkles },
    { id: 'terminal', label: 'Terminal (SOR)', icon: Terminal, badge: 'LIVE' },
    { id: 'parity', label: 'Parity Radar', icon: ShieldCheck },
    { id: 'auditor', label: 'Oracle Auditor', icon: Scale },
    { id: 'depth', label: 'Depth L2', icon: BarChart3 },
    { id: 'analytics', label: 'TCA Analytics', icon: Activity },
    { id: 'pricing', label: 'Pricing', icon: DollarSign },
    { id: 'api', label: 'API & Docs', icon: Code2 },
  ];

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-50 backdrop-blur-2xl bg-[#060709]/85 border-b border-white/[0.08] px-4 sm:px-6 md:px-8 h-16 flex items-center justify-between transition-colors">
        {/* Brand Logo */}
        <div 
          className="flex items-center gap-3 cursor-pointer group"
          onClick={() => handleTabClick('overview')}
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

        {/* Desktop Navigation Tabs */}
        <nav className="hidden xl:flex items-center bg-white/[0.03] border border-white/[0.08] rounded-xl p-1 gap-0.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all relative ${
                  isActive
                    ? 'bg-white/[0.1] text-white shadow-sm shadow-black/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-400 font-mono font-bold">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Medium Screen Compact Navigation */}
        <nav className="hidden md:flex xl:hidden items-center bg-white/[0.03] border border-white/[0.08] rounded-xl p-1 gap-0.5 overflow-x-auto max-w-[480px]">
          {tabs.slice(0, 5).map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-white/[0.1] text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label.split(' ')[0]}</span>
              </button>
            );
          })}
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="text-xs text-sky-400 font-semibold px-2 py-1 hover:text-sky-300"
          >
            More...
          </button>
        </nav>

        {/* Actions & Clearance */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="hidden lg:flex items-center gap-2 text-xs text-slate-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse" />
            <span>0.34ms Waterfill</span>
          </div>

          <button
            onClick={onOpenCmd}
            className="flex items-center gap-1.5 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.16] text-slate-300 text-xs px-2.5 sm:px-3 py-1.5 rounded-lg transition-all"
          >
            <Command className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Mandate</span>
            <kbd className="bg-white/[0.08] border border-white/[0.12] px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-slate-200">
              ⌘K
            </kbd>
          </button>

          {authenticatedDesk && (
            <div className="flex items-center gap-2 pl-2 sm:pl-3 border-l border-white/[0.1]">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-[11px] font-semibold text-white leading-tight max-w-[120px] md:max-w-[150px] truncate">
                  {authenticatedDesk}
                </span>
                <span className="text-[9px] font-mono text-emerald-400">Desk Cleared</span>
              </div>
              {onLogout && (
                <button
                  onClick={onLogout}
                  title="Lock Desk / Sign Out"
                  className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-rose-500/20 text-slate-400 hover:text-rose-300 border border-white/[0.08] hover:border-rose-500/30 transition-all flex items-center justify-center"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}

          {/* Mobile Hamburger Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-2 rounded-lg bg-white/[0.04] text-slate-300 hover:text-white border border-white/[0.08]"
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="xl:hidden fixed inset-0 top-16 z-40 bg-black/80 backdrop-blur-xl animate-in fade-in duration-150">
          <div className="bg-[#0b0e14] border-b border-white/[0.08] p-5 space-y-2">
            <div className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-500 px-3 mb-2">
              PRISM Institutional Workstation Suite
            </div>
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabClick(tab.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-white/[0.03]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 opacity-40" />
                </button>
              );
            })}

            <div className="pt-4 border-t border-white/[0.06] flex items-center justify-between text-xs text-slate-400 px-3">
              <span className="font-mono text-emerald-400">0.34ms NY4 Cross-Connect</span>
              <span className="font-mono">FIPS 140-2 Level 3</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
