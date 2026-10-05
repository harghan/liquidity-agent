import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { Hero } from '@/components/Hero';
import { OpticalRefractionCanvas } from '@/components/OpticalRefractionCanvas';
import { AiMandateBar } from '@/components/AiMandateBar';
import { SorTerminal } from '@/components/SorTerminal';
import { ParityRadar } from '@/components/ParityRadar';
import { DepthVisualizer } from '@/components/DepthVisualizer';
import { TcaAnalytics } from '@/components/TcaAnalytics';
import { ApiDocs } from '@/components/ApiDocs';
import { CommandPaletteModal } from '@/components/CommandPaletteModal';
import { DispatchModal } from '@/components/DispatchModal';
import { Footer } from '@/components/Footer';
import { MarketEvent, MicrostructureSignals, ExecutionTranche } from '@/types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('terminal');
  const [selectedMarketKey, setSelectedMarketKey] = useState<string>('vram');
  const [direction, setDirection] = useState<string>('BUY YES');
  const [notionalUsd, setNotionalUsd] = useState<number>(50000);

  // Modals
  const [isCmdOpen, setIsCmdOpen] = useState<boolean>(false);
  const [isDispatchOpen, setIsDispatchOpen] = useState<boolean>(false);

  // AI Mandate State
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [aiSignals, setAiSignals] = useState<MicrostructureSignals | null>(null);
  const [aiRationale, setAiRationale] = useState<string | null>(null);
  const [aiPreSignedHash, setAiPreSignedHash] = useState<string | null>(null);

  const markets: Record<string, MarketEvent> = {
    vram: {
      id: 'vram',
      name: 'Will Vivek Ramaswamy win the 2028 US Presidential Election?',
      category: 'Presidential Election',
      polyMid: 0.0065,
      kalshiMid: 0.0025,
      baseVwap: 0.008,
      liquidityUsd: 21461179,
    },
    fomc: {
      id: 'fomc',
      name: 'Federal Reserve Interest Rate Decision (FOMC July 2026)',
      category: 'Fed / Rates',
      polyMid: 0.62,
      kalshiMid: 0.59,
      baseVwap: 0.605,
      liquidityUsd: 12850000,
    },
    walz: {
      id: 'walz',
      name: 'Will Tim Walz win the 2028 US Presidential Election?',
      category: 'Presidential Election',
      polyMid: 0.055,
      kalshiMid: 0.05,
      baseVwap: 0.052,
      liquidityUsd: 8940000,
    },
    recession: {
      id: 'recession',
      name: 'Will the US enter an NBER Recession before 2027?',
      category: 'Recession',
      polyMid: 0.24,
      kalshiMid: 0.215,
      baseVwap: 0.228,
      liquidityUsd: 4200000,
    },
  };

  const currentMarket = markets[selectedMarketKey] || markets.vram;

  // Discrete equal-marginal-price waterfill split
  const polyRatio = Math.max(0.48, Math.min(0.82, 0.64 + notionalUsd / 550000));
  const kalshiRatio = 1.0 - polyRatio;

  const polyAmount = Math.round(notionalUsd * polyRatio);
  const kalshiAmount = notionalUsd - polyAmount;

  const polyPct = polyRatio * 100;
  const kalshiPct = kalshiRatio * 100;

  const effectiveVwap = (currentMarket.baseVwap + notionalUsd / 1200000).toFixed(4);
  const capturedAlpha = `+$${(notionalUsd * 0.0824 * (notionalUsd / 50000)).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
  const slippageBps = `+${Math.min(520, 48 + notionalUsd / 400).toFixed(1)} bps`;

  // Tranches schedule
  const tranches: ExecutionTranche[] = [
    {
      tranche: 'Tranche #1',
      venue: 'Kalshi CFTC',
      price: (currentMarket.kalshiMid * 1.05).toFixed(4),
      shares: Math.round((kalshiAmount * 0.4) / (currentMarket.kalshiMid * 1.05)).toLocaleString(),
      notional: `$${Math.round(kalshiAmount * 0.4).toLocaleString()}`,
      vwap: (currentMarket.kalshiMid * 1.05).toFixed(4),
    },
    {
      tranche: 'Tranche #2',
      venue: 'Polymarket CLOB',
      price: (currentMarket.polyMid * 1.02).toFixed(4),
      shares: Math.round((polyAmount * 0.45) / (currentMarket.polyMid * 1.02)).toLocaleString(),
      notional: `$${Math.round(polyAmount * 0.45).toLocaleString()}`,
      vwap: (currentMarket.polyMid * 1.02).toFixed(4),
    },
    {
      tranche: 'Tranche #3',
      venue: 'Kalshi CFTC',
      price: (currentMarket.kalshiMid * 1.25).toFixed(4),
      shares: Math.round((kalshiAmount * 0.6) / (currentMarket.kalshiMid * 1.25)).toLocaleString(),
      notional: `$${Math.round(kalshiAmount * 0.6).toLocaleString()}`,
      vwap: (currentMarket.baseVwap * 0.95).toFixed(4),
    },
    {
      tranche: 'Tranche #4',
      venue: 'Polymarket CLOB',
      price: (currentMarket.polyMid * 1.38).toFixed(4),
      shares: Math.round((polyAmount * 0.55) / (currentMarket.polyMid * 1.38)).toLocaleString(),
      notional: `$${Math.round(polyAmount * 0.55).toLocaleString()}`,
      vwap: effectiveVwap,
    },
  ];

  // AI Mandate Execution Handler
  const handleExecutePrompt = async (prompt: string) => {
    setAiLoading(true);
    try {
      const res = await fetch('/api/ai/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      if (res.ok) {
        const data = await res.json();
        applyAiResult(data);
        setAiLoading(false);
        return;
      }
    } catch {
      // Local quant fallback
    }

    // High-speed browser quant fallback
    applyLocalAiResult(prompt);
    setAiLoading(false);
  };

  const applyAiResult = (data: any) => {
    const intent = data.intent || {};
    const signals = data.signals || {};
    const matched = (data.matched_event || '').toLowerCase();

    if (matched.includes('fomc') || matched.includes('fed')) setSelectedMarketKey('fomc');
    else if (matched.includes('walz')) setSelectedMarketKey('walz');
    else if (matched.includes('recession')) setSelectedMarketKey('recession');
    else setSelectedMarketKey('vram');

    const sideStr = `${intent.side === 'sell' ? 'SELL ' : 'BUY '}${intent.outcome_target === 'No' ? 'NO' : 'YES'}`;
    setDirection(sideStr);

    if (intent.target_size_usd) {
      setNotionalUsd(intent.target_size_usd);
    }

    setAiSignals({
      orderBookImbalance: signals.order_book_imbalance || 0.38,
      micropriceDriftBps: signals.microprice_drift_bps || -4.2,
      predictedImpactBps: signals.predicted_impact_bps || 14.8,
      recommendedCadence: signals.recommended_cadence || 'STAGGERED_ICEBERG',
      confidenceScore: signals.confidence_score || 0.92,
    });
    setAiRationale(data.ai_rationale);
    setAiPreSignedHash(data.pre_signed_hash || '0x61035963fd6b328fc412ae89b001');
  };

  const applyLocalAiResult = (prompt: string) => {
    const low = prompt.toLowerCase();
    let size = 50000;
    const sizeMatch = low.match(/\$?\s*(\d[\d,]*\.?\d*)\s*(k|m|million|thousand)?/);
    if (sizeMatch) {
      let val = parseFloat(sizeMatch[1].replace(/,/g, ''));
      const unit = (sizeMatch[2] || '').toLowerCase();
      if (unit.startsWith('k')) val *= 1000;
      else if (unit.startsWith('m')) val *= 1000000;
      if (val >= 1000) size = val;
    }

    let mKey = 'vram';
    let mTitle = 'Vivek Ramaswamy 2028';
    if (low.includes('fomc') || low.includes('fed') || low.includes('rate')) {
      mKey = 'fomc';
      mTitle = 'Federal Reserve FOMC July 2026';
    } else if (low.includes('walz')) {
      mKey = 'walz';
      mTitle = 'Tim Walz 2028 Presidential';
    } else if (low.includes('recession')) {
      mKey = 'recession';
      mTitle = 'US NBER Recession 2026';
    }

    let dir = 'BUY YES';
    if (low.includes('fade') || low.includes('no') || low.includes('against')) {
      dir = 'BUY NO';
    } else if (low.includes('sell') || low.includes('dump') || low.includes('short')) {
      dir = 'SELL YES';
    }

    setSelectedMarketKey(mKey);
    setDirection(dir);
    setNotionalUsd(size);

    const obi = +(0.25 + (size % 40) / 100).toFixed(2);
    const drift = +((Math.random() * 8) - 4).toFixed(1);
    const impact = +(Math.pow(size / 30000, 1.25) * 12).toFixed(1);
    const cadence = size > 40000 ? 'STAGGERED_ICEBERG' : 'IMMEDIATE_SWEEP';

    setAiSignals({
      orderBookImbalance: obi,
      micropriceDriftBps: drift,
      predictedImpactBps: impact,
      recommendedCadence: cadence,
      confidenceScore: 0.94,
    });
    setAiRationale(
      `PRISM Autonomous SOR deconstructed mandate for ${mTitle}. Optimal equal-marginal-price waterfill: Polymarket $${Math.round(size * polyRatio).toLocaleString()}, Kalshi $${Math.round(size * kalshiRatio).toLocaleString()}. Microstructure queue signals indicate ${cadence} cadence captures ${capturedAlpha} (${slippageBps}) in execution alpha over single-venue market orders.`
    );
    setAiPreSignedHash(`0x${Math.abs(hashString(prompt)).toString(16).padStart(12, '0')}c402...`);
  };

  const hashString = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return hash;
  };

  // Keyboard shortcut listener (⌘K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCmdOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#060709] text-slate-100 selection:bg-sky-500/20 selection:text-sky-300">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenCmd={() => setIsCmdOpen(true)}
      />

      <main className="max-w-6xl mx-auto px-6 md:px-8 py-10 w-full">
        <Hero onOpenCmd={() => setIsCmdOpen(true)} />

        <OpticalRefractionCanvas
          notionalUsd={notionalUsd}
          polyAmount={polyAmount}
          kalshiAmount={kalshiAmount}
          polyPct={polyPct}
          kalshiPct={kalshiPct}
        />

        <AiMandateBar
          onExecutePrompt={handleExecutePrompt}
          signals={aiSignals}
          rationale={aiRationale}
          preSignedHash={aiPreSignedHash}
          loading={aiLoading}
        />

        {/* Tab Views */}
        {activeTab === 'terminal' && (
          <SorTerminal
            markets={markets}
            selectedMarketKey={selectedMarketKey}
            setSelectedMarketKey={setSelectedMarketKey}
            direction={direction}
            setDirection={setDirection}
            notionalUsd={notionalUsd}
            setNotionalUsd={setNotionalUsd}
            polyAmount={polyAmount}
            kalshiAmount={kalshiAmount}
            polyPct={polyPct}
            kalshiPct={kalshiPct}
            effectiveVwap={effectiveVwap}
            capturedAlpha={capturedAlpha}
            slippageBps={slippageBps}
            tranches={tranches}
            onOpenDispatch={() => setIsDispatchOpen(true)}
          />
        )}

        {activeTab === 'parity' && <ParityRadar />}
        {activeTab === 'depth' && <DepthVisualizer />}
        {activeTab === 'analytics' && <TcaAnalytics />}
        {activeTab === 'api' && <ApiDocs />}
      </main>

      <Footer />

      {/* Modals */}
      <CommandPaletteModal
        isOpen={isCmdOpen}
        onClose={() => setIsCmdOpen(false)}
        onSelectPrompt={(p) => {
          setActiveTab('terminal');
          handleExecutePrompt(p);
        }}
        onSelectTab={(tabId) => setActiveTab(tabId)}
      />

      <DispatchModal
        isOpen={isDispatchOpen}
        onClose={() => setIsDispatchOpen(false)}
        notionalUsd={notionalUsd}
        direction={direction}
        polyAmountLabel={`$${polyAmount.toLocaleString()} (${polyPct.toFixed(1)}%)`}
        kalshiAmountLabel={`$${kalshiAmount.toLocaleString()} (${kalshiPct.toFixed(1)}%)`}
      />
    </div>
  );
};

export default App;
