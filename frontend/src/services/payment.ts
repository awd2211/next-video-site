/**
 * 支付服务 API
 */

import api from './api';

export interface Payment {
  id: number;
  user_id: number;
  subscription_id: number | null;
  amount: string;
  currency: string;
  status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'canceled' | 'refunded';
  payment_provider: 'stripe' | 'paypal' | 'alipay';
  provider_payment_id: string | null;
  payment_method: string | null;
  refund_amount: string;
  refund_reason: string | null;
  error_message: string | null;
  metadata: Record<string, any> | null;
  paid_at: string | null;
  refunded_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface PaymentMethod {
  id: number;
  user_id: number;
  payment_provider: 'stripe' | 'paypal' | 'alipay';
  provider_method_id: string;
  method_type: string;
  last4: string | null;
  brand: string | null;
  expiry_month: number | null;
  expiry_year: number | null;
  is_default: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface PaymentIntentRequest {
  amount: string;
  currency: string;
  provider: 'stripe' | 'paypal' | 'alipay';
  payment_method_id?: string;
  subscription_id?: number;
  metadata?: Record<string, any>;
}

export interface PaymentIntentResponse {
  success: boolean;
  payment_id: number;
  client_secret?: string;
  payment_url?: string;
  error_message?: string;
}

export interface PaymentConfirmRequest {
  provider_payment_id: string;
  payment_method_id?: string;
}

export interface RefundRequest {
  amount?: string;
  reason?: string;
}

export interface AddPaymentMethodRequest {
  provider: 'stripe' | 'paypal' | 'alipay';
  provider_method_id: string;
  method_type: string;
  last4?: string;
  brand?: string;
  expiry_month?: number;
  expiry_year?: number;
}

/**
 * 创建支付意图
 */
export const createPaymentIntent = async (
  request: PaymentIntentRequest
): Promise<PaymentIntentResponse> => {
  const { data } = await api.post('/payments/intent', request);
  return data;
};

/**
 * 确认支付
 */
export const confirmPayment = async (
  paymentId: number,
  request: PaymentConfirmRequest
): Promise<Payment> => {
  const { data } = await api.post(`/payments/${paymentId}/confirm`, request);
  return data;
};

/**
 * 获取支付列表
 */
export const getPayments = async (params?: {
  skip?: number;
  limit?: number;
}): Promise<{ items: Payment[]; total: number; skip: number; limit: number }> => {
  const { data } = await api.get('/payments', { params });
  return data;
};

/**
 * 获取支付详情
 */
export const getPayment = async (paymentId: number): Promise<Payment> => {
  const { data } = await api.get(`/payments/${paymentId}`);
  return data;
};

/**
 * 申请退款
 */
export const requestRefund = async (
  paymentId: number,
  request: RefundRequest = {}
): Promise<Payment> => {
  const { data } = await api.post(`/payments/${paymentId}/refund`, request);
  return data;
};

/**
 * 获取支付方式列表
 */
export const getPaymentMethods = async (): Promise<{ items: PaymentMethod[] }> => {
  const { data } = await api.get('/payments/methods');
  return data;
};

/**
 * 添加支付方式
 */
export const addPaymentMethod = async (
  request: AddPaymentMethodRequest
): Promise<PaymentMethod> => {
  const { data } = await api.post('/payments/methods', request);
  return data;
};

/**
 * 设置默认支付方式
 */
export const setDefaultPaymentMethod = async (methodId: number): Promise<PaymentMethod> => {
  const { data } = await api.post(`/payments/methods/${methodId}/set-default`);
  return data;
};

/**
 * 删除支付方式
 */
export const deletePaymentMethod = async (methodId: number): Promise<void> => {
  await api.delete(`/payments/methods/${methodId}`);
};
