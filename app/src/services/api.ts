/**
 * OpenOptions Lab - API Service Layer
 * 统一封装后端 API 调用
 */
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import type {
  MarketOverview,
  SymbolData,
  SymbolDetail,
  TermStructure,
  IvRankItem,
  PremiumRankItem,
  PriceChangeRankItem,
  PaginatedResponse,
  WatchlistItem,
  Strategy,
  UserProfile,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  UnusualFlow,
} from '@/types/api';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证 Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Token 过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}${API_VERSION}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除登录状态
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // 统一错误处理
    const errorMessage = (error.response?.data as { message?: string })?.message || '请求失败';
    console.error('API Error:', errorMessage);
    
    return Promise.reject(error);
  }
);

// ==================== 行情数据 API ====================

/**
 * 获取市场概览统计
 */
export const getMarketOverview = async (): Promise<MarketOverview> => {
  const response = await apiClient.get('/market/overview');
  return response.data;
};

/**
 * 获取品种列表
 */
export const getSymbols = async (
  category?: string,
  exchange?: string,
  search?: string,
  page: number = 1,
  pageSize: number = 50
): Promise<PaginatedResponse<SymbolData>> => {
  const params = new URLSearchParams();
  if (category && category !== 'all') params.append('category', category);
  if (exchange && exchange !== 'all') params.append('exchange', exchange);
  if (search) params.append('search', search);
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());

  const response = await apiClient.get(`/market/symbols?${params.toString()}`);
  return response.data;
};

/**
 * 获取单个品种详情
 */
export const getSymbolDetail = async (symbol: string): Promise<SymbolDetail> => {
  const response = await apiClient.get(`/market/symbols/${symbol}`);
  return response.data;
};

/**
 * 获取 IV 排名
 */
export const getIvRank = async (limit: number = 20): Promise<IvRankItem[]> => {
  const response = await apiClient.get(`/market/iv-rank?limit=${limit}`);
  return response.data;
};

/**
 * 获取溢价排名
 */
export const getPremiumRank = async (limit: number = 20): Promise<PremiumRankItem[]> => {
  const response = await apiClient.get(`/market/premium-rank?limit=${limit}`);
  return response.data;
};

/**
 * 获取价格变动排名
 */
export const getPriceChangeRank = async (limit: number = 20): Promise<PriceChangeRankItem[]> => {
  const response = await apiClient.get(`/market/price-change?limit=${limit}`);
  return response.data;
};

/**
 * 获取期限结构数据
 */
export const getTermStructure = async (symbol: string): Promise<TermStructure[]> => {
  const response = await apiClient.get(`/market/term-structure?symbol=${symbol}`);
  return response.data;
};

// ==================== 认证 API ====================

/**
 * 用户登录
 */
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post('/auth/login', data);
  const { access_token, refresh_token } = response.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
  return response.data;
};

/**
 * 用户注册
 */
export const register = async (data: RegisterRequest): Promise<LoginResponse> => {
  const response = await apiClient.post('/auth/register', data);
  const { access_token, refresh_token } = response.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
  return response.data;
};

/**
 * 用户登出
 */
export const logout = async (): Promise<void> => {
  try {
    await apiClient.post('/auth/logout');
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async (): Promise<UserProfile> => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

// ==================== 用户数据 API ====================

/**
 * 获取自选股列表
 */
export const getWatchlist = async (): Promise<WatchlistItem[]> => {
  const response = await apiClient.get('/user/watchlist');
  return response.data;
};

/**
 * 添加自选股
 */
export const addToWatchlist = async (symbol: string, notes?: string): Promise<WatchlistItem> => {
  const response = await apiClient.post('/user/watchlist', { symbol, notes });
  return response.data;
};

/**
 * 删除自选股
 */
export const removeFromWatchlist = async (symbol: string): Promise<void> => {
  await apiClient.delete(`/user/watchlist/${symbol}`);
};

/**
 * 获取策略列表
 */
export const getStrategies = async (): Promise<Strategy[]> => {
  const response = await apiClient.get('/user/strategies');
  return response.data;
};

/**
 * 保存策略
 */
export const saveStrategy = async (strategy: Omit<Strategy, 'id' | 'created_at' | 'updated_at'>): Promise<Strategy> => {
  const response = await apiClient.post('/user/strategies', strategy);
  return response.data;
};

/**
 * 删除策略
 */
export const deleteStrategy = async (strategyId: string): Promise<void> => {
  await apiClient.delete(`/user/strategies/${strategyId}`);
};

// ==================== 异动监控 API ====================

/**
 * 获取异动数据（使用静态数据，后续可替换为 API）
 */
export const getUnusualFlows = async (): Promise<UnusualFlow[]> => {
  // 暂时返回静态数据，后续可替换为真实 API
  const { unusualFlows } = await import('@/data/marketData');
  return unusualFlows;
};

// ==================== 健康检查 ====================

/**
 * API 健康检查
 */
export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await axios.get(`${API_BASE_URL}${API_VERSION}/health/`);
  return response.data;
};

export default apiClient;
