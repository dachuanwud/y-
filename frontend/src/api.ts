import axios from 'axios';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 配置 API 基础 URL
// 在开发环境中使用 Vite 代理 (/api -> http://localhost:8000/api)
// 生产环境可以通过环境变量配置
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Types
export interface SummaryData {
  market_type: string;
  latest_date: string;
  y_idx_30: MetricItem;
  y_idx_90: MetricItem;
  altcoin_30: MetricItem;
  market_30: MetricItem;
}

export interface MetricItem {
  value: number;
  change: number;
  date: string;
}

export interface ChartDataResponse {
  data: any[];
  config: any;
}

// Hooks
export const useConfig = () => {
  return useQuery({
    queryKey: ['config'],
    queryFn: async () => {
      const { data } = await api.get('/config');
      return data;
    },
  });
};

export const useSummary = (marketType: string) => {
  return useQuery({
    queryKey: ['summary', marketType],
    queryFn: async () => {
      const { data } = await api.get('/summary', {
        params: { market_type: marketType }
      });
      return data as SummaryData;
    },
  });
};

export const useChartData = (marketType: string, chartKey: string) => {
  return useQuery({
    queryKey: ['chart', marketType, chartKey],
    queryFn: async () => {
      const { data } = await api.get(`/chart/${marketType}/${chartKey}`);
      return data as ChartDataResponse;
    },
    enabled: !!marketType && !!chartKey,
  });
};

export const useRefreshData = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/refresh');
      return data;
    },
    onSuccess: () => {
      // Invalidate all queries to re-fetch fresh data
      queryClient.invalidateQueries();
    },
  });
};

