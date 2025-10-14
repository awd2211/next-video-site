import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface AIRequestLog {
  id: number;
  provider_id?: number;
  provider_type: string;
  model: string;
  request_type: string;
  prompt?: string;
  response?: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  response_time: number;
  status: string;
  error_message?: string;
  estimated_cost: number;
  user_id?: number;
  admin_user_id?: number;
  request_metadata?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface AIUsageStats {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  avg_response_time: number;
  success_rate: number;
  requests_by_provider: Record<string, number>;
  tokens_by_provider: Record<string, number>;
  cost_by_provider: Record<string, number>;
  requests_by_model: Record<string, number>;
  avg_response_time_by_provider: Record<string, number>;
}

export interface AICostStats {
  today_cost: number;
  this_month_cost: number;
  cost_trend: Array<{ date: string; cost: number; requests: number }>;
  projected_monthly_cost: number;
  cost_by_model: Record<string, number>;
  top_cost_users: Array<{ user_id: number; username: string; cost: number }>;
}

export interface AIQuota {
  id: number;
  quota_type: string;
  target_id?: number;
  daily_request_limit?: number;
  monthly_request_limit?: number;
  daily_token_limit?: number;
  monthly_token_limit?: number;
  daily_cost_limit?: number;
  monthly_cost_limit?: number;
  daily_requests_used: number;
  daily_tokens_used: number;
  daily_cost_used: number;
  monthly_requests_used: number;
  monthly_tokens_used: number;
  monthly_cost_used: number;
  rate_limit_per_minute?: number;
  rate_limit_per_hour?: number;
  is_active: boolean;
  last_daily_reset?: string;
  last_monthly_reset?: string;
  created_at: string;
  updated_at: string;
}

export interface AIQuotaStatus {
  has_quota: boolean;
  quota?: AIQuota;
  daily_remaining_requests?: number;
  monthly_remaining_requests?: number;
  daily_remaining_tokens?: number;
  monthly_remaining_tokens?: number;
  daily_remaining_cost?: number;
  monthly_remaining_cost?: number;
  is_limited: boolean;
  limit_reason?: string;
}

export interface AITemplate {
  id: number;
  name: string;
  category: string;
  description?: string;
  prompt_template: string;
  variables: string[];
  example_variables?: Record<string, any>;
  recommended_provider?: string;
  recommended_model?: string;
  recommended_params?: Record<string, any>;
  is_active: boolean;
  usage_count: number;
  tags?: string[];
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface RequestLogsParams {
  skip?: number;
  limit?: number;
  provider_type?: string;
  model?: string;
  status?: string;
  user_id?: number;
  admin_user_id?: number;
  start_date?: string;
  end_date?: string;
  min_cost?: number;
  max_cost?: number;
}

export interface UsageStatsParams {
  start_date?: string;
  end_date?: string;
  provider_type?: string;
  model?: string;
}

export interface QuotaCreate {
  quota_type: string;
  target_id?: number;
  daily_request_limit?: number;
  monthly_request_limit?: number;
  daily_token_limit?: number;
  monthly_token_limit?: number;
  daily_cost_limit?: number;
  monthly_cost_limit?: number;
  rate_limit_per_minute?: number;
  rate_limit_per_hour?: number;
  is_active?: boolean;
}

export interface TemplateCreate {
  name: string;
  category: string;
  description?: string;
  prompt_template: string;
  variables?: string[];
  example_variables?: Record<string, any>;
  recommended_provider?: string;
  recommended_model?: string;
  recommended_params?: Record<string, any>;
  tags?: string[];
}

// Request Logs
export const getRequestLogs = async (params?: RequestLogsParams) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/request-logs`, { params });
  return response.data;
};

export const getRequestLog = async (logId: number) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/request-logs/${logId}`);
  return response.data;
};

export const deleteRequestLog = async (logId: number) => {
  const response = await axios.delete(`${API_BASE_URL}/api/v1/admin/ai-logs/request-logs/${logId}`);
  return response.data;
};

// Stats
export const getUsageStats = async (params?: UsageStatsParams) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/stats/usage`, { params });
  return response.data;
};

export const getCostStats = async (params?: { days?: number }) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/stats/cost`, { params });
  return response.data;
};

// Quotas
export const getQuotas = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/quotas`);
  return response.data;
};

export const createQuota = async (data: QuotaCreate) => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/admin/ai-logs/quotas`, data);
  return response.data;
};

export const updateQuota = async (quotaId: number, data: Partial<QuotaCreate>) => {
  const response = await axios.put(`${API_BASE_URL}/api/v1/admin/ai-logs/quotas/${quotaId}`, data);
  return response.data;
};

export const deleteQuota = async (quotaId: number) => {
  const response = await axios.delete(`${API_BASE_URL}/api/v1/admin/ai-logs/quotas/${quotaId}`);
  return response.data;
};

export const getGlobalQuotaStatus = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/quotas/status/global`);
  return response.data;
};

// Templates
export const getTemplates = async (params?: { category?: string; is_active?: boolean }) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/admin/ai-logs/templates`, { params });
  return response.data;
};

export const createTemplate = async (data: TemplateCreate) => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/admin/ai-logs/templates`, data);
  return response.data;
};

export const updateTemplate = async (templateId: number, data: Partial<TemplateCreate>) => {
  const response = await axios.put(`${API_BASE_URL}/api/v1/admin/ai-logs/templates/${templateId}`, data);
  return response.data;
};

export const deleteTemplate = async (templateId: number) => {
  const response = await axios.delete(`${API_BASE_URL}/api/v1/admin/ai-logs/templates/${templateId}`);
  return response.data;
};
