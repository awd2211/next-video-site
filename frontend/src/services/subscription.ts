/**
 * 订阅服务 API
 */

import api from './api';

export interface SubscriptionPlan {
  id: number;
  name: string;
  name_en: string;
  name_zh: string;
  description: string;
  description_en: string;
  description_zh: string;
  billing_period: 'monthly' | 'quarterly' | 'yearly' | 'lifetime';
  price_usd: string;
  price_cny: string;
  price_eur: string | null;
  trial_days: number;
  features: string[] | null;
  max_video_quality: string;
  max_concurrent_streams: number;
  allow_downloads: boolean;
  ad_free: boolean;
  is_active: boolean;
  is_popular: boolean;
  display_order: number;
  created_at: string;
  updated_at: string | null;
}

export interface UserSubscription {
  id: number;
  user_id: number;
  plan_id: number;
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'expired';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  trial_start: string | null;
  trial_end: string | null;
  payment_provider: string;
  provider_subscription_id: string | null;
  auto_renew: boolean;
  discount_amount: string;
  coupon_id: number | null;
  created_at: string;
  updated_at: string | null;
  plan?: SubscriptionPlan;
}

export interface CreateSubscriptionRequest {
  plan_id: number;
  payment_provider: 'stripe' | 'paypal' | 'alipay';
  payment_method_id?: string;
  coupon_code?: string;
  auto_renew?: boolean;
}

export interface UpdateSubscriptionRequest {
  auto_renew?: boolean;
  plan_id?: number;
}

export interface CancelSubscriptionRequest {
  immediately?: boolean;
}

/**
 * 获取所有订阅套餐
 */
export const getSubscriptionPlans = async (): Promise<{ items: SubscriptionPlan[] }> => {
  const { data } = await api.get('/subscriptions/plans');
  return data;
};

/**
 * 获取指定订阅套餐详情
 */
export const getSubscriptionPlan = async (planId: number): Promise<SubscriptionPlan> => {
  const { data } = await api.get(`/subscriptions/plans/${planId}`);
  return data;
};

/**
 * 创建订阅
 */
export const createSubscription = async (
  request: CreateSubscriptionRequest
): Promise<UserSubscription> => {
  const { data } = await api.post('/subscriptions', request);
  return data;
};

/**
 * 获取当前用户的活跃订阅
 */
export const getMyActiveSubscription = async (): Promise<UserSubscription | null> => {
  try {
    const { data } = await api.get('/subscriptions/my-subscription');
    return data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null;
    }
    throw error;
  }
};

/**
 * 获取当前用户的所有订阅
 */
export const getMySubscriptions = async (): Promise<{ items: UserSubscription[] }> => {
  const { data } = await api.get('/subscriptions/my-subscriptions');
  return data;
};

/**
 * 获取指定订阅详情
 */
export const getSubscription = async (subscriptionId: number): Promise<UserSubscription> => {
  const { data } = await api.get(`/subscriptions/${subscriptionId}`);
  return data;
};

/**
 * 更新订阅设置
 */
export const updateSubscription = async (
  subscriptionId: number,
  request: UpdateSubscriptionRequest
): Promise<UserSubscription> => {
  const { data } = await api.patch(`/subscriptions/${subscriptionId}`, request);
  return data;
};

/**
 * 取消订阅
 */
export const cancelSubscription = async (
  subscriptionId: number,
  request: CancelSubscriptionRequest = {}
): Promise<UserSubscription> => {
  const { data } = await api.post(`/subscriptions/${subscriptionId}/cancel`, request);
  return data;
};
