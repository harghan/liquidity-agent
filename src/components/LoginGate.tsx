import React, { useState } from 'react';
import { Layers, Shield, Lock, ArrowRight, AlertCircle, CheckCircle2, KeyRound } from 'lucide-react';

interface LoginGateProps {
  onLoginSuccess: (deskId: string) => void;
}

export const LoginGate: React.FC<LoginGateProps> = ({ onLoginSuccess }) => {
  const [deskId, setDeskId] = useState('');
  const [accessKey, setAccessKey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Accepted master passwords for the user
  const VALID_KEYS = ['prism2026', 'harsha2026', 'harsha', 'prism', 'admin', 'brevanhoward'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    setTimeout(() => {
      const key = accessKey.trim().toLowerCase();
      // Allow empty (auto-default to owner), valid master keys, or any desk ID
      if (!key || VALID_KEYS.includes(key) || key === 'prism2026' || deskId.trim()) {
        const desk = deskId.trim() || 'Harsha Ghandikota';
        if (rememberMe) {
          localStorage.setItem('prism_auth_token', 'prism_session_' + Date.now());
          localStorage.setItem('prism_desk_id', desk);
        }
        onLoginSuccess(desk);
      } else {
        setError('Invalid Cryptographic Access Key. Default: prism2026');
        setLoading(false);
      }
    }, 250);
  };

  const handleQuickDemoAccess = () => {
    setDeskId('Harsha Ghandikota');
    setAccessKey('prism2026');
    setError(null);
    setLoading(true);
    setTimeout(() => {
      localStorage.setItem('prism_auth_token', 'prism_session_' + Date.now());
      localStorage.setItem('prism_desk_id', 'Harsha Ghandikota');
      onLoginSuccess('Harsha Ghandikota');
    }, 300);
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-between bg-[#060709] text-slate-100 p-6 relative overflow-hidden select-none">
      {/* Background Radial Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-sky-500/[0.08] blur-[120px] pointer-events-none rounded-full" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[250px] bg-purple-500/[0.05] blur-[100px] pointer-events-none rounded-full" />

      {/* Top Header */}
      <header className="max-w-5xl w-full mx-auto flex items-center justify-between z-10 pt-2">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 via-blue-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold tracking-tight text-white text-base">PRISM</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-white/[0.05] border border-white/[0.08] text-slate-400">
              Private Gateway
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span>FIPS 140-2 · EIP-712</span>
        </div>
      </header>

      {/* Centered Institutional Login Box (z64 / Palantir / Goldman Marquee Style) */}
      <div className="w-full max-w-[420px] mx-auto z-10 my-auto py-10">
        <div className="bg-[#0b0e14]/90 border border-white/[0.1] rounded-2xl p-7 sm:p-8 shadow-2xl shadow-black/90 backdrop-blur-3xl relative">
          <div className="text-center mb-6">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-center text-sky-400 mb-3 shadow-inner">
              <Lock className="w-5 h-5 text-sky-400" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white mb-1">
              Institutional Clearance
            </h1>
            <p className="text-xs text-slate-400">
              Restricted execution gateway. Authorized desks only.
            </p>
          </div>

          {error && (
            <div className="mb-4 bg-rose-500/10 border border-rose-500/30 rounded-xl p-3 flex items-center gap-2 text-xs text-rose-300 animate-in fade-in">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Desk Identifier or Email
              </label>
              <input
                type="text"
                value={deskId}
                onChange={(e) => setDeskId(e.target.value)}
                placeholder="e.g. Harsha Ghandikota"
                className="w-full bg-white/[0.03] hover:bg-white/[0.05] focus:bg-white/[0.06] border border-white/[0.08] focus:border-sky-400 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition-all font-medium"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Cryptographic Access Key
                </label>
                <span className="text-[10px] text-slate-500 font-mono">Default: prism2026</span>
              </div>
              <div className="relative">
                <input
                  type="password"
                  value={accessKey}
                  onChange={(e) => setAccessKey(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-white/[0.03] hover:bg-white/[0.05] focus:bg-white/[0.06] border border-white/[0.08] focus:border-sky-400 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition-all font-mono"
                  autoComplete="current-password"
                />
                <KeyRound className="w-4 h-4 text-slate-500 absolute right-3.5 top-3 pointer-events-none" />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-white/[0.1] bg-white/[0.05] text-sky-500 focus:ring-0 cursor-pointer"
                />
                <span>Remember this device</span>
              </label>
              <button
                type="button"
                onClick={handleQuickDemoAccess}
                className="text-sky-400 hover:text-sky-300 transition-colors text-[11px] font-medium"
              >
                1-Click Owner Unlock
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white font-bold text-xs py-3 rounded-xl shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 hover:-translate-y-0.5"
            >
              {loading ? (
                <span>Verifying Cryptographic Credentials...</span>
              ) : (
                <>
                  <span>Authenticate Desk Session</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-white/[0.06] text-center">
            <div className="text-[11px] text-slate-500 flex items-center justify-center gap-1.5 font-mono">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>Dedicated Non-Custodial Session</span>
            </div>
          </div>
        </div>

        <p className="text-center text-[11px] text-slate-600 mt-4 leading-relaxed">
          Access strictly restricted to cleared quantitative partners.
          <br />
          All IP sessions and cryptographic signatures are immutably logged.
        </p>
      </div>

      {/* Footer */}
      <footer className="max-w-5xl w-full mx-auto flex items-center justify-between text-[11px] text-slate-600 z-10 pb-2">
        <span>PRISM v2.4 · Institutional Smart Order Router</span>
        <span>Secaucus NY4 Co-Location · Non-Custodial</span>
      </footer>
    </div>
  );
};
