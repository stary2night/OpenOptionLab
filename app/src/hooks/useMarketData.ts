/**
 * OpenOptions Lab - 行情数据 Hooks
 * 使用 React Query 实现数据获取和缓存
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMarketOverview,
  getSymbols,
  getSymbolDetail,
  getIvRank,
  getPremiumRank,
  getPriceChangeRank,
  getTermStructure,
  getUnusualFlows,
} from '@/services/api';
import type { SymbolData } from '@/types/api';

// Query Keys
export const marketKeys = {
  all: ['market'] as const,
  overview: () => [...marketKeys.all, 'overview'] as const,
  symbols: (filters: { category?: string; exchange?: string; search?: string }) =>
    [...marketKeys.all, 'symbols', filters] as const,
  symbolDetail: (symbol: string) => [...marketKeys.all, 'symbol', symbol] as const,
  ivRank: () => [...marketKeys.all, 'ivRank'] as const,
  premiumRank: () => [...marketKeys.all, 'premiumRank'] as const,
  priceChange: () => [...marketKeys.all, 'priceChange'] as const,
  termStructure: (symbol: string) => [...marketKeys.all, 'termStructure', symbol] as const,
  unusualFlows: () => [...marketKeys.all, 'unusualFlows'] as const,
};

// ==================== Market Overview ====================

/**
 * 获取市场概览数据
 * 自动刷新：每 30 秒
 */
export const useMarketOverview = () => {
  return useQuery({
    queryKey: marketKeys.overview(),
    queryFn: getMarketOverview,
    refetchInterval: 30000, // 30 秒自动刷新
    staleTime: 15000, // 15 秒内视为新鲜数据
  });
};

// ==================== Symbols ====================

interface UseSymbolsOptions {
  category?: string;
  exchange?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

/**
 * 获取品种列表
 * 支持分页、筛选、搜索
 */
export const useSymbols = (options: UseSymbolsOptions = {}) => {
  const { category, exchange, search, page = 1, pageSize = 50 } = options;

  return useQuery({
    queryKey: marketKeys.symbols({ category, exchange, search }),
    queryFn: () => getSymbols(category, exchange, search, page, pageSize),
    staleTime: 10000, // 10 秒内视为新鲜数据
  });
};

/**
 * 获取单个品种详情
 */
export const useSymbolDetail = (symbol: string) => {
  return useQuery({
    queryKey: marketKeys.symbolDetail(symbol),
    queryFn: () => getSymbolDetail(symbol),
    enabled: !!symbol, // 只有 symbol 存在时才查询
    staleTime: 30000,
  });
};

// ==================== Rankings ====================

/**
 * 获取 IV 排名
 * 自动刷新：每 60 秒
 */
export const useIvRank = (limit: number = 20) => {
  return useQuery({
    queryKey: [...marketKeys.ivRank(), limit],
    queryFn: () => getIvRank(limit),
    refetchInterval: 60000, // 60 秒自动刷新
  });
};

/**
 * 获取溢价排名
 */
export const usePremiumRank = (limit: number = 20) => {
  return useQuery({
    queryKey: [...marketKeys.premiumRank(), limit],
    queryFn: () => getPremiumRank(limit),
    refetchInterval: 60000,
  });
};

/**
 * 获取价格变动排名
 */
export const usePriceChangeRank = (limit: number = 20) => {
  return useQuery({
    queryKey: [...marketKeys.priceChange(), limit],
    queryFn: () => getPriceChangeRank(limit),
    refetchInterval: 30000, // 30 秒刷新（价格变动更频繁）
  });
};

// ==================== Term Structure ====================

/**
 * 获取期限结构数据
 */
export const useTermStructure = (symbol: string) => {
  return useQuery({
    queryKey: marketKeys.termStructure(symbol),
    queryFn: () => getTermStructure(symbol),
    enabled: !!symbol,
    staleTime: 60000,
  });
};

// ==================== Unusual Flows ====================

/**
 * 获取异动监控数据
 * 自动刷新：每 15 秒
 */
export const useUnusualFlows = () => {
  return useQuery({
    queryKey: marketKeys.unusualFlows(),
    queryFn: getUnusualFlows,
    refetchInterval: 15000, // 15 秒刷新
  });
};

// ==================== Mutations ====================

/**
 * 刷新市场数据
 */
export const useRefreshMarketData = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      // 并行刷新所有市场相关查询
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: marketKeys.overview() }),
        queryClient.invalidateQueries({ queryKey: marketKeys.all }),
      ]);
    },
  });
};

// ==================== Helper Hooks ====================

/**
 * 获取分类统计数据
 */
export const useCategoryStats = (symbols: SymbolData[] = []) => {
  return useQuery({
    queryKey: [...marketKeys.all, 'categoryStats'],
    queryFn: async () => {
      const stats = {
        index: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        metal: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        energy: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        agri: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        black: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        chemical: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
        new: { count: 0, avgIv: 0, symbols: [] as SymbolData[] },
      };

      symbols.forEach((s) => {
        const category = s.category as keyof typeof stats;
        if (stats[category]) {
          stats[category].count++;
          stats[category].symbols.push(s);
        }
      });

      // 计算平均 IV
      Object.keys(stats).forEach((key) => {
        const category = key as keyof typeof stats;
        const categorySymbols = stats[category].symbols;
        if (categorySymbols.length > 0) {
          stats[category].avgIv =
            categorySymbols.reduce((sum, s) => sum + (s.impliedVol || 0), 0) /
            categorySymbols.length;
        }
      });

      return stats;
    },
    enabled: symbols.length > 0,
  });
};
