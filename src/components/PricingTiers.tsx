import React from 'react';
import { Check, ShieldCheck, Zap, Server, Building2, ArrowRight, Lock } from 'lucide-react';

export const PricingTiers: React.FC = () => {
  const tiers = [
    {
      name: 'CORE QUANT API',
      price: '$2,500',
      period: '/ month',
      description: 'Programmatic algorithmic execution for systematic quant funds and proprietary trading groups.',
      badge: null,
      features: [
        'Full REST & WebSocket L2 Streaming',
        'Polymarket CLOB & Kalshi CFTC Unified Feed',
        'Equal-Marginal Cost Waterfill Engine',
        'Sub-50ms Routing Optimization',
        'Up to 100 requests / second throughput',
        'Community & Discord Developer Support',
      ],
      cta: 'Subscribe via API Key',
      highlighted: false,
    },
    {
      name: 'INSTITUTIONAL DESK',
      price: '$12,000',
      period: '/ month',
      description: 'Turnkey execution workstation for prime brokerage desks, macro hedge funds, and market makers.',
      badge: 'MOST POPULAR',
      features: [
        'Everything in Core Quant API',
        'Full Multi-Seat PRISM Terminal Access',
        'Non-Custodial EIP-712 & CFTC FIX Signing',
        'Automated Parity & SOFR Arbitrage Radar',
        'Oracle Resolution Conflict Guard & NLP Audits',
        'Historical TCA & Implementation Shortfall Analytics',
        '99.95% Execution SLA Guarantee',
        'Dedicated Technical Account Manager',
      ],
      cta: 'Deploy Desk Workstation',
      highlighted: true,
    },
    {
      name: 'PRIME DIRECT',
      price: '$35,000',
      period: '/ month',
      description: 'Ultra-low latency infrastructure with direct exchange connectivity and custom orderbook dark pools.',
      badge: 'ENTERPRISE',
      features: [
        'Everything in Institutional Desk',
        'Direct FIX 4.4 & 5.0 Drop-Copy Sessions',
        'Secaucus NY4 Co-Location Cross-Connect (0.34ms)',
        'Custom Legal Horizon Monitoring & Alerting',
        'Dedicated Private Serverless VPC Instance',
        'Bespoke Iceberg & TWAP Execution Algos',
        'FIPS 140-2 Level 3 Hardware Security Module',
        '24/7 Phone & Red Phone Desk Bridge',
      ],
      cta: 'Request Prime Direct Clearance',
      highlighted: false,
    },
  ];

  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono font-bold uppercase tracking-wider">
          <ShieldCheck className="w-3.5 h-3.5" /> Commercial Clearance Tiers
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          Engineered for Capital That Cannot Afford Slippage
        </h1>
        <p className="text-sm text-slate-400 leading-relaxed">
          Predictable flat-fee institutional access. Non-custodial routing with zero basis point take-rate on order volume.
        </p>
      </div>

      {/* Tier Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {tiers.map((t, idx) => (
          <div
            key={idx}
            className={`rounded-3xl p-8 flex flex-col justify-between transition-all relative ${
              t.highlighted
                ? 'bg-[#0b0e14] border-2 border-sky-500/50 shadow-2xl shadow-sky-500/10 scale-105 z-10'
                : 'bg-white/[0.02] border border-white/[0.08] hover:border-white/[0.14]'
            }`}
          >
            {t.badge && (
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-sky-400 to-blue-600 text-white font-mono text-[10px] font-extrabold uppercase px-3 py-1 rounded-full tracking-wider shadow-md">
                {t.badge}
              </div>
            )}

            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 mb-2">
                {t.name}
              </div>
              <div className="flex items-baseline gap-1 my-3">
                <span className="text-4xl sm:text-5xl font-extrabold font-mono text-white tracking-tight">
                  {t.price}
                </span>
                <span className="text-xs text-slate-400 font-mono">{t.period}</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                {t.description}
              </p>

              <div className="space-y-3 border-t border-white/[0.06] pt-6 mb-8">
                {t.features.map((f, fIdx) => (
                  <div key={fIdx} className="flex items-start gap-2.5 text-xs text-slate-300">
                    <Check className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              className={`w-full py-3.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                t.highlighted
                  ? 'bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white shadow-lg shadow-sky-500/25'
                  : 'bg-white/[0.05] hover:bg-white/[0.09] text-white border border-white/[0.08]'
              }`}
            >
              <span>{t.cta}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      {/* Sovereign Co-Location Banner */}
      <div className="bg-gradient-to-r from-sky-500/[0.06] via-purple-500/[0.04] to-transparent border border-white/[0.08] rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 font-bold uppercase">
            <Server className="w-4 h-4" /> Secaucus Equinix NY4 Co-Location
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Sovereign & Tier-1 Prime Brokerage Infrastructure
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Need bespoke sub-millisecond FPGA matching, dark pool liquidity internalization, or custom CFTC clearinghouse settlement integrations? Our sovereign team deploys dedicated on-premise hardware inside your datacenter.
          </p>
        </div>

        <button className="px-6 py-3.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-white text-xs font-bold border border-white/[0.1] shrink-0 transition-all flex items-center gap-2">
          <span>Inquire Sovereign SLA</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
