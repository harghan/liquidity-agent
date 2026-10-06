export interface MarketEvent {
  id: string;
  name: string;
  category: string;
  polyMid: number;
  kalshiMid: number;
  baseVwap: number;
  liquidityUsd: number;
  volumeUsd?: number;
  spreadBps?: number;
  description?: string;
}

export interface MicrostructureSignals {
  orderBookImbalance: number;
  micropriceDriftBps: number;
  predictedImpactBps: number;
  recommendedCadence: 'IMMEDIATE_SWEEP' | 'STAGGERED_ICEBERG' | 'WAIT_FOR_REPLENISHMENT';
  confidenceScore: number;
}

export interface ParsedIntent {
  targetSizeUsd: number;
  side: 'buy' | 'sell';
  outcomeTarget: 'Yes' | 'No';
  maxSlippageBps: number;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH';
  executionStyle: 'WATERFILL_OPTIMAL' | 'PASSIVE_PEG' | 'TWAP';
  keywords: string[];
}

export interface ExecutionTranche {
  tranche: string;
  venue: string;
  price: string;
  shares: string;
  notional: string;
  vwap: string;
}

export interface VenueAllocation {
  notionalUsd: number;
  shares: number;
  vwap: number;
  effectiveVwap: number;
  totalFeeUsd: number;
  pctOfTotalOrder: number;
}
