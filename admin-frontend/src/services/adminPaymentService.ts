import api from '../utils/axios';

export interface SubscriptionPlan {
  id: number;
  name_en: string;
  name_zh: string;
  description_en?: string;
  description_zh?: string;
  billing_period: 'monthly' | 'quarterly' | 'yearly' | 'lifetime';
  price_usd: string;
  price_cny?: string;
  price_eur?: string;
  max_video_quality: string;
  max_concurrent_streams: number;
  allow_downloads: boolean;
  allow_offline: boolean;
  ads_free: boolean;
  max_devices: number;
  trial_days?: number;
  is_active: boolean;
  is_popular: boolean;
  features_en?: string;
  features_zh?: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: number;
  user_id: number;
  subscription_id?: number;
  amount: string;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'refunded' | 'canceled';
  payment_method?: string;
  payment_provider: 'stripe' | 'paypal' | 'alipay';
  provider_payment_id?: string;
  provider_customer_id?: string;
  error_code?: string;
  error_message?: string;
  metadata?: string;
  paid_at?: string;
  refunded_at?: string;
  refund_amount?: string;
  refund_reason?: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    username: string;
    email: string;
  };
}

export interface Coupon {
  id: number;
  code: string;
  description: string;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: string;
  min_purchase_amount?: string;
  max_discount_amount?: string;
  usage_limit?: number;
  usage_count: number;
  usage_limit_per_user?: number;
  applicable_plans?: string;
  valid_from: string;
  valid_until?: string;
  status: 'active' | 'inactive' | 'expired';
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  user_id: number;
  subscription_id?: number;
  invoice_number: string;
  status: 'draft' | 'pending' | 'paid' | 'void' | 'uncollectible';
  currency: string;
  subtotal: string;
  tax: string;
  discount: string;
  total: string;
  amount_paid: string;
  amount_due: string;
  billing_name?: string;
  billing_email: string;
  billing_address?: string;
  line_items?: string;
  payment_due_date?: string;
  paid_at?: string;
  voided_at?: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    username: string;
    email: string;
  };
}

export interface UserSubscription {
  id: number;
  user_id: number;
  plan_id: number;
  status: 'active' | 'canceled' | 'past_due' | 'trialing' | 'expired';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  canceled_at?: string;
  trial_start?: string;
  trial_end?: string;
  auto_renew: boolean;
  payment_provider?: string;
  provider_subscription_id?: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    username: string;
    email: string;
  };
  plan?: SubscriptionPlan;
}

export interface SubscriptionStats {
  total_subscriptions: number;
  active_subscriptions: number;
  trialing_subscriptions: number;
  canceled_subscriptions: number;
  past_due_subscriptions: number;
  expired_subscriptions: number;
  monthly_recurring_revenue: number;
  churn_rate: number;
  conversion_rate: number;
  avg_subscription_value: number;
}

// ============ Subscription Plans ============
export const getSubscriptionPlans = async (params?: {
  page?: number;
  page_size?: number;
  is_active?: boolean;
}): Promise<{ items: SubscriptionPlan[]; total: number }> => {
  const { data } = await api.get('/api/v1/admin/subscription-plans/', { params });
  return data;
};

export const getSubscriptionPlan = async (id: number): Promise<SubscriptionPlan> => {
  const { data } = await api.get(`/api/v1/admin/subscription-plans/${id}`);
  return data;
};

export const createSubscriptionPlan = async (plan: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> => {
  const { data } = await api.post('/api/v1/admin/subscription-plans/', plan);
  return data;
};

export const updateSubscriptionPlan = async (id: number, plan: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> => {
  const { data } = await api.put(`/api/v1/admin/subscription-plans/${id}`, plan);
  return data;
};

export const deleteSubscriptionPlan = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/admin/subscription-plans/${id}`);
};

export const activateSubscriptionPlan = async (id: number): Promise<SubscriptionPlan> => {
  const { data } = await api.post(`/api/v1/admin/subscription-plans/${id}/activate`);
  return data;
};

export const deactivateSubscriptionPlan = async (id: number): Promise<SubscriptionPlan> => {
  const { data } = await api.post(`/api/v1/admin/subscription-plans/${id}/deactivate`);
  return data;
};

// ============ Payments ============
export const getPayments = async (params?: {
  page?: number;
  page_size?: number;
  user_id?: number;
  status?: string;
  payment_provider?: string;
}): Promise<{ items: Payment[]; total: number }> => {
  const { data } = await api.get('/api/v1/admin/payments/', { params });
  return data;
};

export const getPayment = async (id: number): Promise<Payment> => {
  const { data } = await api.get(`/api/v1/admin/payments/${id}`);
  return data;
};

export const refundPayment = async (
  id: number,
  refundRequest: {
    amount?: number;
    reason?: string;
    reason_detail?: string;
    admin_note?: string;
  }
): Promise<Payment> => {
  const { data } = await api.post(`/api/v1/admin/payments/${id}/refund`, {
    payment_id: id,
    ...refundRequest,
  });
  return data;
};

export const getPaymentStats = async (): Promise<{
  total_revenue: number;
  total_refunded: number;
  success_rate: number;
  avg_transaction_value: number;
}> => {
  const { data } = await api.get('/api/v1/admin/payments/stats/overview');
  return data;
};

// ============ Coupons ============
export const getCoupons = async (params?: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<{ items: Coupon[]; total: number }> => {
  const { data } = await api.get('/api/v1/admin/coupons/', { params });
  return data;
};

export const getCoupon = async (id: number): Promise<Coupon> => {
  const { data } = await api.get(`/api/v1/admin/coupons/${id}`);
  return data;
};

export const createCoupon = async (coupon: Partial<Coupon>): Promise<Coupon> => {
  const { data } = await api.post('/api/v1/admin/coupons/', coupon);
  return data;
};

export const updateCoupon = async (id: number, coupon: Partial<Coupon>): Promise<Coupon> => {
  const { data } = await api.put(`/api/v1/admin/coupons/${id}`, coupon);
  return data;
};

export const deleteCoupon = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/admin/coupons/${id}`);
};

export const activateCoupon = async (id: number): Promise<Coupon> => {
  const { data } = await api.post(`/api/v1/admin/coupons/${id}/activate`);
  return data;
};

export const deactivateCoupon = async (id: number): Promise<Coupon> => {
  const { data } = await api.post(`/api/v1/admin/coupons/${id}/deactivate`);
  return data;
};

// ============ Invoices ============
export const getInvoices = async (params?: {
  page?: number;
  page_size?: number;
  user_id?: number;
  status?: string;
}): Promise<{ items: Invoice[]; total: number }> => {
  const { data } = await api.get('/api/v1/admin/invoices/', { params });
  return data;
};

export const getInvoice = async (id: number): Promise<Invoice> => {
  const { data } = await api.get(`/api/v1/admin/invoices/${id}`);
  return data;
};

export const updateInvoiceStatus = async (id: number, status: string): Promise<Invoice> => {
  const { data } = await api.put(`/api/v1/admin/invoices/${id}/status`, { status });
  return data;
};

export const sendInvoice = async (id: number): Promise<{ success: boolean }> => {
  const { data } = await api.post(`/api/v1/admin/invoices/${id}/send`);
  return data;
};

export const voidInvoice = async (id: number): Promise<Invoice> => {
  const { data } = await api.post(`/api/v1/admin/invoices/${id}/void`);
  return data;
};

// ============ User Subscriptions ============
export const getUserSubscriptions = async (params?: {
  page?: number;
  page_size?: number;
  user_id?: number;
  plan_id?: number;
  status?: string;
}): Promise<{ items: UserSubscription[]; total: number }> => {
  const { data } = await api.get('/api/v1/admin/subscriptions/', { params });
  return data;
};

export const getUserSubscription = async (id: number): Promise<UserSubscription> => {
  const { data } = await api.get(`/api/v1/admin/subscriptions/${id}`);
  return data;
};

export const cancelUserSubscription = async (
  id: number,
  cancel_immediately?: boolean
): Promise<UserSubscription> => {
  const { data } = await api.post(`/api/v1/admin/subscriptions/${id}/cancel`, {
    cancel_immediately,
  });
  return data;
};

export const renewUserSubscription = async (id: number): Promise<UserSubscription> => {
  const { data } = await api.post(`/api/v1/admin/subscriptions/${id}/renew`);
  return data;
};

export const getSubscriptionStats = async (): Promise<SubscriptionStats> => {
  const { data } = await api.get('/api/v1/admin/subscriptions/stats/overview');
  return data;
};

export default {
  // Subscription Plans
  getSubscriptionPlans,
  getSubscriptionPlan,
  createSubscriptionPlan,
  updateSubscriptionPlan,
  deleteSubscriptionPlan,
  activateSubscriptionPlan,
  deactivateSubscriptionPlan,

  // Payments
  getPayments,
  getPayment,
  refundPayment,
  getPaymentStats,

  // Coupons
  getCoupons,
  getCoupon,
  createCoupon,
  updateCoupon,
  deleteCoupon,
  activateCoupon,
  deactivateCoupon,

  // Invoices
  getInvoices,
  getInvoice,
  updateInvoiceStatus,
  sendInvoice,
  voidInvoice,

  // User Subscriptions
  getUserSubscriptions,
  getUserSubscription,
  cancelUserSubscription,
  renewUserSubscription,
  getSubscriptionStats,
};
