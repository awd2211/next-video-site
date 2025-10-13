import axios from '@/utils/axios';

export interface AIProvider {
  id: number;
  name: string;
  provider_type: 'openai' | 'grok' | 'google';
  description?: string;
  api_key: string;
  base_url?: string;
  model_name: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  settings?: Record<string, any>;
  enabled: boolean;
  is_default: boolean;
  total_requests: number;
  total_tokens: number;
  last_used_at?: string;
  last_test_at?: string;
  last_test_status?: string;
  last_test_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AIProviderCreate {
  name: string;
  provider_type: 'openai' | 'grok' | 'google';
  description?: string;
  api_key: string;
  base_url?: string;
  model_name: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  settings?: Record<string, any>;
  enabled?: boolean;
  is_default?: boolean;
}

export interface AIProviderUpdate {
  name?: string;
  description?: string;
  api_key?: string;
  base_url?: string;
  model_name?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  settings?: Record<string, any>;
  enabled?: boolean;
  is_default?: boolean;
}

export interface AIModelInfo {
  id: string;
  name: string;
  description?: string;
  context_window?: number;
  max_output_tokens?: number;
}

export interface AITestRequest {
  message: string;
  stream?: boolean;
}

export interface AITestResponse {
  success: boolean;
  response?: string;
  error?: string;
  tokens_used?: number;
  latency_ms?: number;
}

export interface AIChatRequest {
  provider_id: number;
  messages: Array<{ role: string; content: string }>;
  stream?: boolean;
}

export interface AIChatResponse {
  success: boolean;
  response?: string;
  error?: string;
  tokens_used?: number;
  latency_ms?: number;
  model?: string;
}

export interface AIUsageStats {
  provider_id: number;
  provider_name: string;
  provider_type: string;
  total_requests: number;
  total_tokens: number;
  last_used_at?: string;
  enabled: boolean;
}

// Get all AI providers
export const getAIProviders = async (params?: {
  skip?: number;
  limit?: number;
  provider_type?: string;
  enabled?: boolean;
}): Promise<{ total: number; items: AIProvider[] }> => {
  const response = await axios.get('/api/v1/admin/ai/providers', { params });
  return response.data;
};

// Get single AI provider
export const getAIProvider = async (id: number): Promise<AIProvider> => {
  const response = await axios.get(`/api/v1/admin/ai/providers/${id}`);
  return response.data;
};

// Create AI provider
export const createAIProvider = async (data: AIProviderCreate): Promise<AIProvider> => {
  const response = await axios.post('/api/v1/admin/ai/providers', data);
  return response.data;
};

// Update AI provider
export const updateAIProvider = async (
  id: number,
  data: AIProviderUpdate
): Promise<AIProvider> => {
  const response = await axios.put(`/api/v1/admin/ai/providers/${id}`, data);
  return response.data;
};

// Delete AI provider
export const deleteAIProvider = async (id: number): Promise<void> => {
  await axios.delete(`/api/v1/admin/ai/providers/${id}`);
};

// Test AI provider connection
export const testAIProvider = async (
  id: number,
  data: AITestRequest
): Promise<AITestResponse> => {
  const response = await axios.post(`/api/v1/admin/ai/providers/${id}/test`, data);
  return response.data;
};

// Chat with AI
export const chatWithAI = async (data: AIChatRequest): Promise<AIChatResponse> => {
  const response = await axios.post('/api/v1/admin/ai/chat', data);
  return response.data;
};

// Get available models for a provider type
export const getAvailableModels = async (
  providerType: string
): Promise<{ provider_type: string; models: AIModelInfo[] }> => {
  const response = await axios.get(`/api/v1/admin/ai/models/${providerType}`);
  return response.data;
};

// Get usage statistics
export const getAIUsageStats = async (): Promise<{
  stats: AIUsageStats[];
  total_requests: number;
  total_tokens: number;
}> => {
  const response = await axios.get('/api/v1/admin/ai/usage');
  return response.data;
};
