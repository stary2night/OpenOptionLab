/**
 * OpenOptions Lab - API 类型定义
 */

// ==================== 通用类型 ====================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  error: string;
  message: string;
}

// ==================== 行情数据类型 ====================

export interface MarketOverview {
  total_symbols: number;
  total_volume: number;
  avg_iv: number;
  iv_rise_count: number;
  iv_fall_count: number;
  high_iv_count: number;
  low_iv_count: number;
  updated_at: string;
}

export interface SymbolData {
  id: string;
  symbol: string;
  name: string;
  nameEn: string;
  exchange: string;
  category: string;
  latestPrice: number;
  priceChange: number;
  priceChangePercent: number;
  daysToExpiry: number;
  impliedVol: number;
  ivChange: number;
  ivSpeed: number;
  realizedVol: number;
  premium: number;
  skew: number;
  ivPercentile: number;
  skewPercentile: number;
  isMain: boolean;
  isForeign?: boolean;
  expiry: string;
}

export interface SymbolDetail extends SymbolData {
  historicalData?: {
    date: string;
    price: number;
    iv: number;
    rv: number;
  }[];
  optionsChain?: {
    strike: number;
    call_iv: number;
    put_iv: number;
    call_volume: number;
    put_volume: number;
  }[];
}

export interface TermStructure {
  symbol: string;
  expiry: string;
  daysToExpiry: number;
  atmIv: number;
  skew25: number;
  skew10: number;
}

export interface IvRankItem {
  symbol: string;
  name: string;
  impliedVol: number;
  ivChange: number;
  ivPercentile: number;
  category: string;
}

export interface PremiumRankItem {
  symbol: string;
  name: string;
  premium: number;
  impliedVol: number;
  realizedVol: number;
  category: string;
}

export interface PriceChangeRankItem {
  symbol: string;
  name: string;
  latestPrice: number;
  priceChange: number;
  priceChangePercent: number;
  category: string;
}

// ==================== 异动监控类型 ====================

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

// ==================== 用户认证类型 ====================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  preferences?: {
    theme: 'light' | 'dark';
    language: 'zh' | 'en';
    default_category?: string;
    notifications_enabled: boolean;
  };
}

// ==================== 用户数据类型 ====================

export interface WatchlistItem {
  id: string;
  symbol: string;
  name: string;
  category: string;
  notes?: string;
  alert_enabled: boolean;
  alert_conditions?: {
    iv_threshold?: number;
    price_threshold?: number;
  };
  added_at: string;
}

export interface Strategy {
  id: string;
  name: string;
  description?: string;
  type: 'spread' | 'iron_condor' | 'butterfly' | 'calendar' | 'custom';
  underlying: string;
  legs: StrategyLeg[];
  target_iv?: number;
  max_profit?: number;
  max_loss?: number;
  breakeven?: number[];
  created_at: string;
  updated_at: string;
}

export interface StrategyLeg {
  id: string;
  option_type: 'call' | 'put';
  side: 'buy' | 'sell';
  strike: number;
  expiry: string;
  quantity: number;
  price?: number;
}

// ==================== WebSocket 类型 ====================

export interface WebSocketMessage {
  type: 'market_update' | 'iv_update' | 'unusual_flow' | 'notification';
  data: unknown;
  timestamp: string;
}

export interface MarketUpdateMessage {
  type: 'market_update';
  data: {
    symbol: string;
    price: number;
    priceChange: number;
    priceChangePercent: number;
    volume: number;
  };
  timestamp: string;
}

export interface IvUpdateMessage {
  type: 'iv_update';
  data: {
    symbol: string;
    impliedVol: number;
    ivChange: number;
    ivRank: number;
  };
  timestamp: string;
}
