import React from 'react';
import { Layers } from 'lucide-react';

interface OpticalRefractionCanvasProps {
  notionalUsd: number;
  polyAmount: number;
  kalshiAmount: number;
  polyPct: number;
  kalshiPct: number;
}

export const OpticalRefractionCanvas: React.FC<OpticalRefractionCanvasProps> = ({
  notionalUsd,
  polyAmount,
  kalshiAmount,
  polyPct,
  kalshiPct,
}) => {
  const polyRatio = polyPct / 100;
  const kalshiRatio = kalshiPct / 100;
  const polyBeamWidth = Math.max(2, Math.min(10, polyRatio * 8));
  const kalshiBeamWidth = Math.max(2, Math.min(10, kalshiRatio * 8));

  return (
    <div className="w-full bg-black/40 border border-white/[0.08] rounded-2xl p-4 md:p-6 mb-8 relative overflow-hidden backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
          <Layers className="w-4 h-4 text-sky-400" />
          <span>Optical Liquidity Refraction Stream</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse" />
          <span>Dual-Venue CLOB Real-Time Sync</span>
        </div>
      </div>

      <div className="w-full h-36 sm:h-44 bg-black/50 border border-white/[0.06] rounded-xl flex items-center justify-center relative overflow-hidden">
        <svg className="w-full h-full" viewBox="0 0 800 160" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="beamIn" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="beamPoly" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#2563eb" stopOpacity="0.3" />
            </linearGradient>
            <linearGradient id="beamKalshi" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#d97706" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          {/* Incoming Order Ray */}
          <line
            x1="40"
            y1="80"
            x2="380"
            y2="80"
            stroke="url(#beamIn)"
            strokeWidth="6"
            strokeLinecap="round"
          />
          <circle cx="40" cy="80" r="4" fill="#38bdf8" />
          <text
            x="50"
            y="66"
            fill="#94a3b8"
            fontSize="11"
            fontFamily="'JetBrains Mono', monospace"
            fontWeight="600"
          >
            IN: ${notionalUsd.toLocaleString()} NOTIONAL
          </text>

          {/* The Optical PRISM Crystal Core */}
          <polygon
            points="400,20 440,140 360,140"
            fill="rgba(56, 189, 248, 0.12)"
            stroke="rgba(56, 189, 248, 0.6)"
            strokeWidth="2"
          />
          <circle cx="400" cy="80" r="14" fill="rgba(56, 189, 248, 0.2)" stroke="#38bdf8" strokeWidth="1.5" />
          <text
            x="400"
            y="84"
            fill="#ffffff"
            fontSize="10"
            fontFamily="'Plus Jakarta Sans', sans-serif"
            fontWeight="800"
            textAnchor="middle"
          >
            PRISM
          </text>

          {/* Refracted Polymarket Ray (Cyan) */}
          <line
            x1="410"
            y1="75"
            x2="740"
            y2="40"
            stroke="url(#beamPoly)"
            strokeWidth={polyBeamWidth}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
          <circle cx="740" cy="40" r="4" fill="#38bdf8" />
          <text
            x="745"
            y="44"
            fill="#38bdf8"
            fontSize="11"
            fontFamily="'JetBrains Mono', monospace"
            fontWeight="700"
          >
            POLYMARKET {polyPct.toFixed(1)}% (${polyAmount.toLocaleString()})
          </text>

          {/* Refracted Kalshi Ray (Amber) */}
          <line
            x1="410"
            y1="85"
            x2="740"
            y2="120"
            stroke="url(#beamKalshi)"
            strokeWidth={kalshiBeamWidth}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
          <circle cx="740" cy="120" r="4" fill="#f59e0b" />
          <text
            x="745"
            y="124"
            fill="#f59e0b"
            fontSize="11"
            fontFamily="'JetBrains Mono', monospace"
            fontWeight="700"
          >
            KALSHI {kalshiPct.toFixed(1)}% (${kalshiAmount.toLocaleString()})
          </text>
        </svg>
      </div>
    </div>
  );
};
