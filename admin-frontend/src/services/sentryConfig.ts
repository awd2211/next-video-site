/**
 * Sentry 配置管理服务
 */

import axios from '@/utils/axios';

export interface SentryConfig {
  id: number;
  dsn: string;
  environment: string;
  frontend_enabled: boolean;
  admin_frontend_enabled: boolean;
  traces_sample_rate: string;
  replays_session_sample_rate: string;
  replays_on_error_sample_rate: string;
  ignore_errors?: string;
  allowed_urls?: string;
  denied_urls?: string;
  release_version?: string;
  debug_mode: boolean;
  attach_stacktrace: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
}

export interface SentryConfigCreate {
  dsn: string;
  environment?: string;
  frontend_enabled?: boolean;
  admin_frontend_enabled?: boolean;
  traces_sample_rate?: string;
  replays_session_sample_rate?: string;
  replays_on_error_sample_rate?: string;
  ignore_errors?: string;
  allowed_urls?: string;
  denied_urls?: string;
  release_version?: string;
  debug_mode?: boolean;
  attach_stacktrace?: boolean;
  description?: string;
}

export interface SentryConfigUpdate {
  dsn?: string;
  environment?: string;
  frontend_enabled?: boolean;
  admin_frontend_enabled?: boolean;
  traces_sample_rate?: string;
  replays_session_sample_rate?: string;
  replays_on_error_sample_rate?: string;
  ignore_errors?: string;
  allowed_urls?: string;
  denied_urls?: string;
  release_version?: string;
  debug_mode?: boolean;
  attach_stacktrace?: boolean;
  description?: string;
}

// 获取所有配置
export const getSentryConfigs = async (): Promise<SentryConfig[]> => {
  const response = await axios.get('/api/v1/admin/sentry-config/');
  return response.data;
};

// 获取单个配置
export const getSentryConfig = async (id: number): Promise<SentryConfig> => {
  const response = await axios.get(`/api/v1/admin/sentry-config/${id}`);
  return response.data;
};

// 获取当前激活的配置
export const getActiveSentryConfig = async (): Promise<SentryConfig> => {
  const response = await axios.get('/api/v1/admin/sentry-config/active/current');
  return response.data;
};

// 创建配置
export const createSentryConfig = async (data: SentryConfigCreate): Promise<SentryConfig> => {
  const response = await axios.post('/api/v1/admin/sentry-config/', data);
  return response.data;
};

// 更新配置
export const updateSentryConfig = async (
  id: number,
  data: SentryConfigUpdate
): Promise<SentryConfig> => {
  const response = await axios.put(`/api/v1/admin/sentry-config/${id}`, data);
  return response.data;
};

// 删除配置
export const deleteSentryConfig = async (id: number): Promise<void> => {
  await axios.delete(`/api/v1/admin/sentry-config/${id}`);
};
