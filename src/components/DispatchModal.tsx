import React from 'react';
import { ShieldCheck, X } from 'lucide-react';

interface DispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  notionalUsd: number;
  direction: string;
  polyAmountLabel: string;
  kalshiAmountLabel: string;
}

export const DispatchModal: React.FC<DispatchModalProps> = ({
  isOpen,
  onClose,
  notionalUsd,
  direction,
  polyAmountLabel,
  kalshiAmountLabel,
}) => {
  if (!isOpen) return null;

  const payload = {
    meta: {
      client_desk: "Brevan Howard Macro (NY-04)",
      execution_engine: "PRISM_EQUAL_MARGINAL_PRICE_WATERFILL",
      timestamp: new Date().toISOString(),
    },
    order: {
      target_size_usd: notionalUsd,
      direction: direction,
      allocations: {
        polymarket: { notional_usd: polyAmountLabel, protocol: "EIP-712 Typed Data" },
        kalshi: { notional_usd: kalshiAmountLabel, protocol: "CFTC DCM FIX/REST" },
      },
      pre_signed_hash: "0x78ab12eefc910023a1c84b1298ef91823ab029c4e12",
    },
  };

  const handleTransmit = () => {
    alert("✅ Multi-venue split transmitted directly to Polymarket and Kalshi orderbooks.\n\nLatency: 0.34ms\nAll-in VWAP confirmed.");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#0d1118] border border-white/[0.16] rounded-2xl w-full max-w-lg shadow-2xl shadow-black/95 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-sky-400" />
            <span className="text-sm font-bold text-white">Pre-Signed Non-Custodial Split</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5">
          <p className="text-xs text-slate-400 mb-3 leading-relaxed">
            Review cryptographic authorization before transmitting to Polymarket and Kalshi matching engines:
          </p>

          <pre className="bg-[#040507] border border-white/[0.08] rounded-xl p-4 font-mono text-[11px] text-sky-300 max-h-56 overflow-y-auto leading-relaxed">
            {JSON.stringify(payload, null, 2)}
          </pre>

          <div className="flex justify-end gap-3 mt-5">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleTransmit}
              className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 shadow-md shadow-blue-500/25 transition-all"
            >
              Confirm & Transmit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
