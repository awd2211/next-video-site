/**
 * 优惠券服务 API
 */

import api from './api';

export interface Coupon {
  id: number;
  code: string;
  discount_type: 'percentage' | 'fixed_amount' | 'free_trial';
  discount_value: string;
  max_discount_amount: string | null;
  usage_limit: number | null;
  usage_count: number;
  usage_limit_per_user: number;
  minimum_amount: string | null;
  applicable_plans: string | null;
  valid_from: string;
  valid_until: string | null;
  status: 'active' | 'expired' | 'disabled';
  is_first_purchase_only: boolean;
  description: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface CouponValidateRequest {
  code: string;
  plan_id?: number;
  amount: string;
}

export interface CouponValidateResponse {
  valid: boolean;
  discount_amount: number;
  final_amount: number;
  error_message?: string;
}

/**
 * 验证优惠券
 */
export const validateCoupon = async (
  request: CouponValidateRequest
): Promise<CouponValidateResponse> => {
  const { data } = await api.post('/coupons/validate', request);
  return data;
};

/**
 * 获取可用优惠券列表
 */
export const getAvailableCoupons = async (params?: {
  skip?: number;
  limit?: number;
}): Promise<{ items: Coupon[]; total: number; skip: number; limit: number }> => {
  const { data } = await api.get('/coupons/available', { params });
  return data;
};

/**
 * 根据代码获取优惠券
 */
export const getCouponByCode = async (code: string): Promise<Coupon> => {
  const { data } = await api.get(`/coupons/code/${code}`);
  return data;
};
