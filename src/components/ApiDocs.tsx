import React, { useState } from 'react';
import { Code2, Copy, Check, Terminal, ShieldCheck, Cpu, ArrowRight, ExternalLink, Zap } from 'lucide-react';

export const ApiDocs: React.FC = () => {
  const [activeEndpoint, setActiveEndpoint] = useState<'ai_plan' | 'markets' | 'waterfill' | 'parity' | 'oracle'>('ai_plan');
  const [activeLanguage, setActiveLanguage] = useState<'curl' | 'python' | 'ts'>('curl');
  const [copied, setCopied] = useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const codeSnippets: Record<string, Record<string, string>> = {
    ai_plan: {
      curl: `curl -X POST https://liquidity-agent.vercel.app/api/ai/plan \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer prism_live_k7x992..." \\
  -d '{
    "prompt": "Deploy $100k into Iran invasion before 2027 with < 15 bps slippage",
    "risk_tolerance": "INSTITUTIONAL_LOW"
  }'`,
      python: `import httpx

client = httpx.Client(base_url="https://liquidity-agent.vercel.app/api")
headers = {"Authorization": "Bearer prism_live_k7x992..."}

mandate = client.post("/ai/plan", json={
    "prompt": "Deploy $100k into Iran invasion before 2027 with < 15 bps slippage",
    "risk_tolerance": "INSTITUTIONAL_LOW"
}, headers=headers).json()

print(f"Optimal Split: {mandate['intent']['target_size_usd']} USD")
print(f"Pre-Signed Hash: {mandate['pre_signed_hash']}")
print(f"AI Rationale: {mandate['ai_rationale']}")`,
      ts: `import { PrismClient } from '@prism/sdk';

const prism = new PrismClient({ apiKey: process.env.PRISM_API_KEY });

const plan = await prism.ai.plan({
  prompt: 'Deploy $100k into Iran invasion before 2027 with < 15 bps slippage',
  riskTolerance: 'INSTITUTIONAL_LOW',
});

console.log('Discrete Waterfill Schedule:', plan.tranches);
console.log('Captured Slippage Alpha:', plan.signals.predicted_impact_bps);`,
    },
    markets: {
      curl: `curl -X GET "https://liquidity-agent.vercel.app/api/markets?category=ALL&limit=60" \\
  -H "Authorization: Bearer prism_live_k7x992..."`,
      python: `import httpx

client = httpx.Client(base_url="https://liquidity-agent.vercel.app/api")
markets = client.get("/markets", params={"category": "ALL", "limit": 60}).json()

for market_id, contract in markets["markets"].items():
    print(f"[{contract['category']}] {contract['name']} | Poly: {contract['polyMid']} | Kalshi: {contract['kalshiMid']}")`,
      ts: `import { PrismClient } from '@prism/sdk';

const prism = new PrismClient({ apiKey: process.env.PRISM_API_KEY });
const markets = await prism.markets.list({ limit: 60 });

console.log(\`Loaded \${Object.keys(markets).length} unified live prediction contracts.\`);`,
    },
    waterfill: {
      curl: `curl -X POST https://liquidity-agent.vercel.app/api/execute/waterfill \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer prism_live_k7x992..." \\
  -d '{
    "market_key": "iran_invasion",
    "side": "BUY_YES",
    "notional_usd": 100000,
    "max_slippage_bps": 25,
    "cadence": "STAGGERED_ICEBERG"
  }'`,
      python: `import httpx

client = httpx.Client(base_url="https://liquidity-agent.vercel.app/api")
execution = client.post("/execute/waterfill", json={
    "market_key": "iran_invasion",
    "side": "BUY_YES",
    "notional_usd": 100000,
    "max_slippage_bps": 25,
    "cadence": "STAGGERED_ICEBERG"
}).json()

print(f"Executed VWAP: {execution['effective_vwap']}")
print(f"Polymarket Tranche: \${execution['venues']['polymarket']['amount']}")
print(f"Kalshi Tranche: \${execution['venues']['kalshi']['amount']}")`,
      ts: `import { PrismClient } from '@prism/sdk';

const prism = new PrismClient({ apiKey: process.env.PRISM_API_KEY });

const dispatch = await prism.sor.executeWaterfill({
  marketKey: 'iran_invasion',
  side: 'BUY_YES',
  notionalUsd: 100000,
  maxSlippageBps: 25,
  cadence: 'STAGGERED_ICEBERG',
});

console.log('Dispatch Tickets:', dispatch.tickets);`,
    },
    parity: {
      curl: `curl -X GET "https://liquidity-agent.vercel.app/api/parity/radar?hurdle_sofr=0.048" \\
  -H "Authorization: Bearer prism_live_k7x992..."`,
      python: `import httpx

client = httpx.Client(base_url="https://liquidity-agent.vercel.app/api")
radar = client.get("/parity/radar", params={"hurdle_sofr": 0.048}).json()

for arb in radar["opportunities"]:
    if arb["beats_sofr"]:
        print(f"Alpha Pair: {arb['pair']} | Ann ROIC: {arb['annualized_roic']}% (SOFR +{arb['sofr_delta']}%)")`,
      ts: `import { PrismClient } from '@prism/sdk';

const prism = new PrismClient({ apiKey: process.env.PRISM_API_KEY });
const radar = await prism.parity.scan({ hurdleSofr: 0.048 });

console.log('SOFR-beating opportunities:', radar.filter(o => o.beatsSofr));`,
    },
    oracle: {
      curl: `curl -X POST https://liquidity-agent.vercel.app/api/oracle/audit \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer prism_live_k7x992..." \\
  -d '{
    "pair_id": "iran_invasion",
    "inspect_legal_rules": true
  }'`,
      python: `import httpx

client = httpx.Client(base_url="https://liquidity-agent.vercel.app/api")
audit = client.post("/oracle/audit", json={
    "pair_id": "iran_invasion",
    "inspect_legal_rules": True
}).json()

print(f"Risk Score: {audit['risk_score']} ({audit['divergence_status']})")
print(f"Dispute Details: {audit['risk_details']}")`,
      ts: `import { PrismClient } from '@prism/sdk';

const prism = new PrismClient({ apiKey: process.env.PRISM_API_KEY });
const audit = await prism.oracle.auditPair('iran_invasion');

console.log('Oracle Divergence Alert:', audit.divergenceStatus);`,
    },
  };

  const sampleResponses: Record<string, string> = {
    ai_plan: `{
  "status": "SUCCESS",
  "matched_event": "US Invades Iran before 2027",
  "intent": {
    "side": "buy",
    "outcome_target": "Yes",
    "target_size_usd": 100000,
    "max_slippage_bps": 15
  },
  "signals": {
    "order_book_imbalance": 0.38,
    "microprice_drift_bps": -4.2,
    "predicted_impact_bps": 14.8,
    "recommended_cadence": "STAGGERED_ICEBERG",
    "confidence_score": 0.94
  },
  "waterfill_split": {
    "polymarket_clob": { "amount_usd": 68000, "ratio": 0.68, "vwap": 0.1540 },
    "kalshi_cftc": { "amount_usd": 32000, "ratio": 0.32, "vwap": 0.1610 }
  },
  "pre_signed_hash": "0x61035963fd6b328fc412ae89b001c402e88a38b29",
  "ai_rationale": "PRISM deconstructed mandate for US Invades Iran. Discrete waterfill amortizes flow across Polygon CLOB ($68k) and CFTC ($32k), capturing +$8,240 (316 bps) over single-venue execution."
}`,
    markets: `{
  "status": "SUCCESS",
  "total_active_markets": 69,
  "sources": ["Polymarket Gamma CLOB", "Kalshi CFTC DCM"],
  "markets": {
    "iran_invasion": {
      "id": "iran_invasion",
      "name": "US Invades Iran before 2027",
      "category": "Geopolitics & Defense",
      "polyMid": 0.154,
      "kalshiMid": 0.161,
      "baseVwap": 0.158,
      "liquidityUsd": 8400000,
      "volumeUsd": 38400000
    }
  }
}`,
    waterfill: `{
  "status": "DISPATCH_AUTHORIZED",
  "execution_id": "exec_8f99c20a11e",
  "effective_vwap": 0.1582,
  "slippage_bps": 24.1,
  "venues": {
    "polymarket": { "amount": 64000, "shares": 404551, "hash": "0x4e21a..." },
    "kalshi": { "amount": 36000, "shares": 227560, "order_id": "ord_cftc_9981" }
  },
  "non_custodial_receipt": "0x9812df...fips140_verified"
}`,
    parity: `{
  "status": "SUCCESS",
  "hurdle_sofr": 0.048,
  "opportunities": [
    {
      "pair": "US Invades Iran before 2027",
      "gross_spread_bps": 70.0,
      "annualized_roic": 14.2,
      "beats_sofr": true,
      "sofr_delta": 9.4,
      "strategy": "DISCOUNT_POLY_ARB"
    }
  ]
}`,
    oracle: `{
  "status": "AUDIT_COMPLETED",
  "pair_id": "iran_invasion",
  "divergence_status": "SOURCE_DIVERGENCE_WARNING",
  "risk_score": "MEDIUM RISK (42/100)",
  "polymarket_oracle": "UMA Optimistic Oracle v2 (48h bond challenge)",
  "kalshi_oracle": "U.S. Department of Defense / UN Official Record",
  "risk_details": "Polymarket accepts consensus of credible media reports through UMA bond voting. Kalshi requires official US Executive Branch certification under Title 10/50 USC."
}`,
  };

  const endpoints = [
    { id: 'ai_plan', label: 'POST /api/ai/plan', tag: 'AI Mandate' },
    { id: 'markets', label: 'GET /api/markets', tag: 'Live 60+ Feed' },
    { id: 'waterfill', label: 'POST /api/execute/waterfill', tag: 'SOR Waterfill' },
    { id: 'parity', label: 'GET /api/parity/radar', tag: 'Parity Radar' },
    { id: 'oracle', label: 'POST /api/oracle/audit', tag: 'Oracle Auditor' },
  ];

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-3xl p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-6 border-b border-white/[0.08]">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono font-bold uppercase tracking-wider">
              <Code2 className="w-3.5 h-3.5" /> B2B Institutional API & SDK
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Programmatic Execution & Non-Custodial Gateway
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
              Integrate PRISM's equal-marginal waterfill router, live orderbooks, and autonomous mandate solver into proprietary algorithms, OEMS, and prime desks.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <span className="bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-mono font-bold px-3 py-1.5 rounded-xl">
              OpenAPI 3.1 Spec
            </span>
            <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold px-3 py-1.5 rounded-xl flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> FIPS 140-2 Level 3
            </span>
          </div>
        </div>

        {/* Endpoint Selector Bar */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          {endpoints.map((ep) => (
            <button
              key={ep.id}
              onClick={() => setActiveEndpoint(ep.id as any)}
              className={`px-3.5 py-2 rounded-xl text-xs font-mono font-semibold transition-all flex items-center gap-2 ${
                activeEndpoint === ep.id
                  ? 'bg-sky-500/15 border border-sky-500/40 text-sky-300 shadow-sm'
                  : 'bg-white/[0.03] border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:bg-white/[0.06]'
              }`}
            >
              <span>{ep.label}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/40 text-slate-300 font-sans">
                {ep.tag}
              </span>
            </button>
          ))}
        </div>

        {/* Language Tabs & Code Viewer */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center bg-black/40 border border-white/[0.08] rounded-xl p-1 gap-1">
              {(['curl', 'python', 'ts'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setActiveLanguage(lang)}
                  className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all ${
                    activeLanguage === lang
                      ? 'bg-white/[0.12] text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {lang === 'curl' ? 'cURL' : lang === 'python' ? 'Python SDK' : 'TypeScript'}
                </button>
              ))}
            </div>

            <button
              onClick={() => handleCopy(codeSnippets[activeEndpoint][activeLanguage], 'req')}
              className="flex items-center gap-1.5 text-xs text-sky-400 hover:text-sky-300 bg-white/[0.04] px-3 py-1.5 rounded-lg border border-white/[0.08] transition-all"
            >
              {copied === 'req' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied === 'req' ? 'Copied' : 'Copy Code'}</span>
            </button>
          </div>

          <pre className="bg-[#050608] border border-white/[0.08] rounded-2xl p-5 font-mono text-xs text-sky-300 overflow-x-auto leading-relaxed shadow-inner">
            {codeSnippets[activeEndpoint][activeLanguage]}
          </pre>
        </div>

        {/* Response Sample Viewer */}
        <div className="mt-8 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              Sample JSON Response (200 OK)
            </span>
            <button
              onClick={() => handleCopy(sampleResponses[activeEndpoint], 'res')}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-300 transition-colors"
            >
              {copied === 'res' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>Copy JSON</span>
            </button>
          </div>

          <pre className="bg-[#030406] border border-white/[0.06] rounded-2xl p-5 font-mono text-xs text-slate-300 overflow-x-auto leading-relaxed max-h-96">
            {sampleResponses[activeEndpoint]}
          </pre>
        </div>
      </div>

      {/* Non-Custodial Architecture & Security Specifications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Non-Custodial Architecture</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            PRISM acts exclusively as an algorithmic matchmaker and router. Private keys and exchange API secrets reside in memory on client hardware or AWS KMS. Orders are signed using EIP-712 typed structs for Polymarket and TLS FIX 4.4 sessions for Kalshi DCM.
          </p>
        </div>

        <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Rate Limits & Secaucus NY4 Cross-Connect</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Direct REST endpoints sustain 100 requests/sec with burst buffers up to 250 requests/sec. Institutional desk tiers connect via low-latency WebSocket L2 delta streams with ping intervals of 250ms and sub-millisecond execution dispatch.
          </p>
        </div>
      </div>
    </div>
  );
};
