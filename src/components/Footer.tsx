import React from 'react';
import { Layers, GitBranch, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-white/[0.08] bg-[#040507]/90 py-10 px-6 md:px-8 mt-auto text-xs text-slate-500">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 rounded bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center text-white">
            <Layers className="w-3 h-3" />
          </div>
          <span className="font-extrabold text-white text-sm tracking-tight">PRISM</span>
          <span className="text-slate-600">/</span>
          <span>Institutional Liquidity Refraction Engine</span>
        </div>

        <div className="text-center md:text-left text-slate-400">
          Non-Custodial Architecture · CFTC DCM Compliant · Polygon CLOB Relayer
        </div>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com/harghan/liquidity-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors"
          >
            <GitBranch className="w-4 h-4" />
            <span>GitHub Repository</span>
            <ExternalLink className="w-3 h-3 opacity-60" />
          </a>
        </div>
      </div>
    </footer>
  );
};
