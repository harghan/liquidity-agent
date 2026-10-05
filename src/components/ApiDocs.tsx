import React, { useState } from 'react';
import { Code2, Copy, Check } from 'lucide-react';

export const ApiDocs: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const curlExample = `curl -X POST https://liquidity-agent.vercel.app/api/ai/plan \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Deploy $75k into Vivek 2028 with < 15 bps slippage"
  }'`;

  const handleCopy = () => {
    navigator.clipboard.writeText(curlExample);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.08]">
          <div>
            <div className="text-base font-bold text-white tracking-tight">
              B2B Institutional Execution & Serverless API
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Direct JSON endpoints for algorithmic trading desks and order execution management systems (OEMS)
            </div>
          </div>
          <span className="bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold px-3 py-1 rounded-full">
            v2.1.0 JSON Serverless
          </span>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold text-slate-300">Autonomous AI Mandate Endpoint (cURL)</span>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs text-sky-400 hover:text-sky-300 bg-white/[0.04] px-2.5 py-1 rounded-lg border border-white/[0.08] transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <pre className="bg-[#040507] border border-white/[0.08] rounded-xl p-4 font-mono text-xs text-sky-300 overflow-x-auto leading-relaxed">
            {curlExample}
          </pre>

          <div className="text-xs text-slate-400 leading-relaxed pt-2">
            Returns full discrete execution schedules, Order Book Imbalance (OBI), Kyle's $\lambda$ impact, recommended execution cadence, and pre-signed cryptographic transaction tickets.
          </div>
        </div>
      </div>
    </div>
  );
};
