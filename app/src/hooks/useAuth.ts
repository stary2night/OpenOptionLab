/**
 * OpenOptions Lab - 用户认证 Hooks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { login, register, logout, getCurrentUser } from '@/services/api';
import type { LoginRequest, RegisterRequest } from '@/types/api';

// Query Keys
export const authKeys = {
  all: ['auth'] as const,
  user: () => [...authKeys.all, 'user'] as const,
};

// ==================== Auth State ====================

/**
 * 获取当前登录用户
 */
export const useCurrentUser = () => {
  return useQuery({
    queryKey: authKeys.user(),
    queryFn: getCurrentUser,
    enabled: !!localStorage.getItem('access_token'), // 只有存在 token 时才查询
    retry: false, // 失败不重试（可能是 token 无效）
    staleTime: 5 * 60 * 1000, // 5 分钟内视为新鲜数据
  });
};

/**
 * 检查用户是否已登录
 */
export const useIsAuthenticated = () => {
  const { data: user, isLoading } = useCurrentUser();
  return {
    isAuthenticated: !!user,
    isLoading,
    user,
  };
};

// ==================== Mutations ====================

/**
 * 登录
 */
export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) => login(data),
    onSuccess: (data) => {
      // 登录成功后，缓存用户信息
      queryClient.setQueryData(authKeys.user(), data.user);
    },
  });
};

/**
 * 注册
 */
export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegisterRequest) => register(data),
    onSuccess: (data) => {
      queryClient.setQueryData(authKeys.user(), data.user);
    },
  });
};

/**
 * 登出
 */
export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      // 清除所有缓存数据
      queryClient.clear();
      // 清除用户信息
      queryClient.removeQueries({ queryKey: authKeys.all });
    },
  });
};
