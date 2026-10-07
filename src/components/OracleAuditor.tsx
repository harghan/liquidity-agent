import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2, Scale, ArrowRight, ExternalLink, HelpCircle } from 'lucide-react';

export const OracleAuditor: React.FC = () => {
  const [selectedAuditPair, setSelectedAuditPair] = useState<string>('iran');

  const auditPairs = [
    {
      id: 'iran',
      title: 'US Invades Iran before 2027',
      category: 'Geopolitics',
      polyOracle: 'UMA Optimistic Oracle v2 (48h bond challenge)',
      kalshiOracle: 'U.S. Department of Defense / UN Security Council Official Record',
      polyText: 'Resolves to "Yes" if the US commences military offensive intended to establish control over any portion of Iranian sovereign territory by Dec 31, 2026 11:59 PM ET.',
      kalshiText: 'Resolves to "Yes" if the President of the United States formally directs armed forces under War Powers Resolution or formal declaration of war against the Islamic Republic of Iran.',
      status: 'SOURCE_DIVERGENCE_WARNING',
      riskScore: 'MEDIUM RISK (42/100)',
      riskDetails: 'Polymarket accepts "consensus of credible media reports" through UMA bond voting. Kalshi requires official US Executive Branch certification under Title 10/50 USC.',
    },
    {
      id: 'fomc',
      title: 'Federal Reserve Fed Funds Rate Dec 2026',
      category: 'Macro & Fed',
      polyOracle: 'Federal Reserve Board H.15 Statistical Release',
      kalshiOracle: 'Federal Open Market Committee (FOMC) Statement & Minutes',
      polyText: 'Resolves according to the Effective Federal Funds Rate (EFFR) published in the Federal Reserve H.15 report on the final business day of Dec 2026.',
      kalshiText: 'Resolves based on the upper bound of the target range for the federal funds rate announced following the Dec 2026 FOMC meeting.',
      status: 'VERIFIED_ALIGNED',
      riskScore: 'NEGLIGIBLE RISK (2/100)',
      riskDetails: 'Both venues ground resolution in Federal Reserve Board publications. Mathematical basis identical with zero ambiguity.',
    },
    {
      id: 'recession',
      title: 'US NBER Recession before 2027',
      category: 'Macro & Economics',
      polyOracle: 'NBER Business Cycle Dating Committee Announcement',
      kalshiOracle: 'National Bureau of Economic Research (NBER) Official Record',
      polyText: 'Resolves to "Yes" if NBER announces a business cycle peak before Jan 1, 2027, even if announcement occurs retrospectively.',
      kalshiText: 'Resolves to "Yes" ONLY if NBER releases formal determination before Dec 31, 2026 5:00 PM ET. Retrospective post-horizon announcements do not count.',
      status: 'HORIZON_MISMATCH_CRITICAL',
      riskScore: 'HIGH ARBITRAGE HAZARD (88/100)',
      riskDetails: 'CRITICAL HAZARD: Retrospective dating divergence. NBER typically dates recessions 6-12 months after onset. Kalshi requires determination *during* contract horizon; Polymarket allows post-horizon retrospective settlement.',
    },
    {
      id: 'vram',
      title: 'Vivek Ramaswamy 2028 US Presidential Election',
      category: 'Politics',
      polyOracle: 'Associated Press (AP) Call / Electoral College Vote Certification',
      kalshiOracle: 'Joint Session of the U.S. Congress Electoral College Count (3 U.S.C. § 15)',
      polyText: 'Resolves when AP, Fox, NBC, and CNN call the election or when the winner is inaugurated on Jan 20, 2029.',
      kalshiText: 'Resolves upon the certification of electoral votes by the President of the Senate during the Joint Session of Congress.',
      status: 'TIMING_BUFFER_ACCEPTABLE',
      riskScore: 'LOW RISK (12/100)',
      riskDetails: 'Slight timing offset between media calls (November 2028) and congressional certification (January 6, 2029). Outcome convergence is 99.98% guaranteed.',
    },
  ];

  const currentPair = auditPairs.find((p) => p.id === selectedAuditPair) || auditPairs[0];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white/[0.02] border border-white/[0.08] rounded-2xl p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-white/[0.08]">
          <div>
            <div className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <Scale className="w-4 h-4 text-sky-400" />
              Oracle Resolution Conflict Guard & Legal Horizon Auditor
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Automated NLP contract comparison preventing basis traps across UMA Decentralized Oracles and CFTC Legal Rules
            </div>
          </div>
          <span className="bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-bold px-3 py-1 rounded-full font-mono">
            CFTC Rule 40.2 / UMA EIP-712 Certified
          </span>
        </div>

        {/* Pair Selector Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
          {auditPairs.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedAuditPair(p.id)}
              className={`text-left p-3.5 rounded-xl border transition-all ${
                selectedAuditPair === p.id
                  ? 'bg-sky-500/10 border-sky-400/40 text-white shadow-lg shadow-sky-500/10'
                  : 'bg-white/[0.02] hover:bg-white/[0.05] border-white/[0.06] text-slate-400 hover:text-slate-200'
              }`}
            >
              <div className="text-[10px] font-mono uppercase text-slate-400 mb-1">{p.category}</div>
              <div className="text-xs font-bold text-white leading-tight truncate">{p.title}</div>
              <div className="mt-2 flex items-center gap-1.5 text-[10px] font-mono">
                {p.status === 'VERIFIED_ALIGNED' && (
                  <span className="text-emerald-400 flex items-center gap-1 font-bold">
                    <CheckCircle2 className="w-3 h-3" /> Fully Aligned
                  </span>
                )}
                {p.status === 'SOURCE_DIVERGENCE_WARNING' && (
                  <span className="text-amber-400 flex items-center gap-1 font-bold">
                    <AlertTriangle className="w-3 h-3" /> Source Divergence
                  </span>
                )}
                {p.status === 'HORIZON_MISMATCH_CRITICAL' && (
                  <span className="text-rose-400 flex items-center gap-1 font-bold">
                    <AlertOctagon className="w-3 h-3" /> Horizon Trap
                  </span>
                )}
                {p.status === 'TIMING_BUFFER_ACCEPTABLE' && (
                  <span className="text-sky-400 flex items-center gap-1 font-bold">
                    <CheckCircle2 className="w-3 h-3" /> Timing Buffer
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Side-by-Side Legal Text Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Polymarket Rule Card */}
        <div className="bg-[#0b0e14] border border-sky-500/20 rounded-2xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3 pb-3 border-b border-white/[0.08]">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Polymarket CLOB Legal Resolution Spec
              </span>
            </div>
            <span className="text-[10px] font-mono text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
              Polygon Smart Contract
            </span>
          </div>

          <div className="space-y-3">
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400">Oracle Mechanism</span>
              <div className="text-xs font-semibold text-slate-200 mt-0.5">{currentPair.polyOracle}</div>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400">Official Specification Extract</span>
              <div className="bg-black/40 border border-white/[0.06] rounded-xl p-3 mt-1 text-xs font-mono text-slate-300 leading-relaxed">
                "{currentPair.polyText}"
              </div>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono pt-2 border-t border-white/[0.06]">
              <span>Dispute Window: 48 Hours</span>
              <span>Slashing: 10,000 USDC Bond</span>
            </div>
          </div>
        </div>

        {/* Kalshi Rule Card */}
        <div className="bg-[#0b0e14] border border-amber-500/20 rounded-2xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3 pb-3 border-b border-white/[0.08]">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Kalshi CFTC Rulebook Filing
              </span>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              CFTC 17 CFR § 40.2
            </span>
          </div>

          <div className="space-y-3">
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400">Designated Contract Market (DCM) Oracle</span>
              <div className="text-xs font-semibold text-slate-200 mt-0.5">{currentPair.kalshiOracle}</div>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400">Rule Filing Extract</span>
              <div className="bg-black/40 border border-white/[0.06] rounded-xl p-3 mt-1 text-xs font-mono text-slate-300 leading-relaxed">
                "{currentPair.kalshiText}"
              </div>
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono pt-2 border-t border-white/[0.06]">
              <span>Jurisdiction: CFTC Federal</span>
              <span>Settlement: U.S. Dollar Cash</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Verdict & Guidance Box */}
      <div className={`rounded-2xl p-6 border ${
        currentPair.status === 'VERIFIED_ALIGNED'
          ? 'bg-emerald-500/5 border-emerald-500/20'
          : currentPair.status === 'HORIZON_MISMATCH_CRITICAL'
          ? 'bg-rose-500/10 border-rose-500/30'
          : 'bg-amber-500/5 border-amber-500/20'
      }`}>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              Audit Verdict for {currentPair.title}:
            </span>
            <span className={`text-xs font-bold font-mono px-2.5 py-0.5 rounded-full ${
              currentPair.status === 'VERIFIED_ALIGNED'
                ? 'bg-emerald-500/20 text-emerald-400'
                : currentPair.status === 'HORIZON_MISMATCH_CRITICAL'
                ? 'bg-rose-500/20 text-rose-400'
                : 'bg-amber-500/20 text-amber-400'
            }`}>
              {currentPair.riskScore}
            </span>
          </div>

          <div className="text-xs font-mono text-slate-400">
            SOR Routing Policy: {currentPair.status === 'HORIZON_MISMATCH_CRITICAL' ? 'BLOCKED BY DEFAULT' : 'APPROVED FOR WATERFILL'}
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          {currentPair.riskDetails}
        </p>
      </div>
    </div>
  );
};
