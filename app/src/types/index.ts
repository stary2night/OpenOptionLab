// Market data types
export interface MarketData {
  id: string;
  symbol: string;
  name: string;
  nameEn?: string;
  exchange?: string;
  category?: string;
  latestPrice: number;
  priceChange: number;
  priceChangePercent: number;
  daysToExpiry: number;
  impliedVol: number | null;
  ivChange: number | null;
  ivSpeed: number | null;
  realizedVol: number | null;
  premium: number | null;
  skew: number | null;
  ivPercentile: number | null;
  skewPercentile: number | null;
  isForeign?: boolean;
  isMain?: boolean;
  expiry?: string;
}

export interface VolatilityData {
  symbol: string;
  strike: number;
  callIv: number;
  putIv: number;
  callVolume: number;
  putVolume: number;
}

export interface TermStructure {
  symbol: string;
  expiry: string;
  daysToExpiry: number;
  atmIv: number;
  skew25: number;
  skew10: number;
}

export interface UnusualFlow {
  id: string;
  symbol: string;
  optionType: 'call' | 'put';
  strike: number;
  expiry: string;
  volume: number;
  openInterest: number;
  premium: number;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  timestamp: string;
}

export interface Strategy {
  id: string;
  name: string;
  type: 'spread' | 'iron' | 'butterfly' | 'calendar' | 'custom';
  legs: StrategyLeg[];
  maxProfit?: number;
  maxLoss?: number;
  breakeven: number[];
  probability?: number;
}

export interface StrategyLeg {
  id: string;
  side: 'buy' | 'sell';
  optionType: 'call' | 'put' | 'stock';
  strike: number;
  expiry: string;
  quantity: number;
  price: number;
}

export interface ChartData {
  time: string;
  price: number;
  iv: number;
  rv: number;
}

export type TabType = 'market' | 'volatility' | 'flow' | 'strategy' | 'trade';

export interface Category {
  id: string;
  name: string;
  icon: string;
}

export interface Exchange {
  id: string;
  name: string;
}
