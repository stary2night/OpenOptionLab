/**
 * OpenOptions Lab - WebSocket Hook
 * 实时数据推送连接管理
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import type { WebSocketMessage, MarketUpdateMessage, IvUpdateMessage } from '@/types/api';

interface UseWebSocketOptions {
  onMarketUpdate?: (data: MarketUpdateMessage['data']) => void;
  onIvUpdate?: (data: IvUpdateMessage['data']) => void;
  onUnusualFlow?: (data: unknown) => void;
  onNotification?: (data: unknown) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: WebSocketMessage | null;
  reconnectAttempts: number;
}

/**
 * WebSocket Hook
 * 管理实时数据连接
 */
export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    onMarketUpdate,
    onIvUpdate,
    onUnusualFlow,
    onNotification,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    lastMessage: null,
    reconnectAttempts: 0,
  });

  // 获取 WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = baseUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/ws/market`;
  }, []);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState((prev) => ({ ...prev, isConnecting: true }));

    try {
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setState({
          isConnected: true,
          isConnecting: false,
          lastMessage: null,
          reconnectAttempts: 0,
        });
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setState((prev) => ({ ...prev, lastMessage: message }));

          // 根据消息类型分发处理
          switch (message.type) {
            case 'market_update':
              onMarketUpdate?.((message as MarketUpdateMessage).data);
              break;
            case 'iv_update':
              onIvUpdate?.((message as IvUpdateMessage).data);
              break;
            case 'unusual_flow':
              onUnusualFlow?.(message.data);
              break;
            case 'notification':
              onNotification?.(message.data);
              break;
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));
        onDisconnect?.();

        // 自动重连
        if (state.reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setState((prev) => ({
              ...prev,
              reconnectAttempts: prev.reconnectAttempts + 1,
            }));
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setState((prev) => ({ ...prev, isConnecting: false }));
    }
  }, [
    getWebSocketUrl,
    onMarketUpdate,
    onIvUpdate,
    onUnusualFlow,
    onNotification,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval,
    maxReconnectAttempts,
    state.reconnectAttempts,
  ]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState({
      isConnected: false,
      isConnecting: false,
      lastMessage: null,
      reconnectAttempts: 0,
    });
  }, []);

  // 发送消息
  const sendMessage = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);

  // 订阅特定品种
  const subscribeSymbol = useCallback(
    (symbol: string) => {
      return sendMessage({
        action: 'subscribe',
        symbol,
      });
    },
    [sendMessage]
  );

  // 取消订阅
  const unsubscribeSymbol = useCallback(
    (symbol: string) => {
      return sendMessage({
        action: 'unsubscribe',
        symbol,
      });
    },
    [sendMessage]
  );

  // 组件挂载时自动连接
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
    subscribeSymbol,
    unsubscribeSymbol,
  };
};

export default useWebSocket;
