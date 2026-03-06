/**
 * OpenOptions Lab - 用户数据 Hooks
 * 自选股、策略等用户相关数据
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  getStrategies,
  saveStrategy,
  deleteStrategy,
} from '@/services/api';
import type { Strategy } from '@/types/api';

// Query Keys
export const userDataKeys = {
  all: ['userData'] as const,
  watchlist: () => [...userDataKeys.all, 'watchlist'] as const,
  strategies: () => [...userDataKeys.all, 'strategies'] as const,
};

// ==================== Watchlist ====================

/**
 * 获取自选股列表
 */
export const useWatchlist = () => {
  return useQuery({
    queryKey: userDataKeys.watchlist(),
    queryFn: getWatchlist,
    enabled: !!localStorage.getItem('access_token'),
    staleTime: 60000,
  });
};

/**
 * 添加自选股
 */
export const useAddToWatchlist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ symbol, notes }: { symbol: string; notes?: string }) =>
      addToWatchlist(symbol, notes),
    onSuccess: () => {
      // 刷新自选股列表
      queryClient.invalidateQueries({ queryKey: userDataKeys.watchlist() });
    },
  });
};

/**
 * 删除自选股
 */
export const useRemoveFromWatchlist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (symbol: string) => removeFromWatchlist(symbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userDataKeys.watchlist() });
    },
  });
};

/**
 * 检查品种是否在自选股中
 */
export const useIsInWatchlist = (symbol: string) => {
  const { data: watchlist } = useWatchlist();
  return watchlist?.some((item) => item.symbol === symbol) ?? false;
};

// ==================== Strategies ====================

/**
 * 获取策略列表
 */
export const useStrategies = () => {
  return useQuery({
    queryKey: userDataKeys.strategies(),
    queryFn: getStrategies,
    enabled: !!localStorage.getItem('access_token'),
    staleTime: 60000,
  });
};

/**
 * 保存策略
 */
export const useSaveStrategy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (strategy: Omit<Strategy, 'id' | 'created_at' | 'updated_at'>) =>
      saveStrategy(strategy),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userDataKeys.strategies() });
    },
  });
};

/**
 * 删除策略
 */
export const useDeleteStrategy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (strategyId: string) => deleteStrategy(strategyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userDataKeys.strategies() });
    },
  });
};
