import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { createSubscription, type SubscriptionPlan } from '../services/subscription';
import { validateCoupon } from '../services/coupon';
import { createPaymentIntent } from '../services/payment';

const Checkout: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const plan = location.state?.plan as SubscriptionPlan;

  const [couponCode, setCouponCode] = useState('');
  const [couponApplied, setCouponApplied] = useState(false);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [finalAmount, setFinalAmount] = useState(0);
  const [couponError, setCouponError] = useState('');
  const [paymentProvider, setPaymentProvider] = useState<'stripe' | 'paypal' | 'alipay'>('stripe');
  const [autoRenew, setAutoRenew] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (!plan) {
      navigate('/subscription');
      return;
    }
    setFinalAmount(parseFloat(plan.price_usd));
  }, [plan, navigate]);

  // 验证优惠券
  const validateCouponMutation = useMutation({
    mutationFn: validateCoupon,
    onSuccess: (data) => {
      if (data.valid) {
        setCouponApplied(true);
        setDiscountAmount(data.discount_amount);
        setFinalAmount(data.final_amount);
        setCouponError('');
      } else {
        setCouponError(data.error_message || t('checkout.invalidCoupon'));
        setCouponApplied(false);
      }
    },
    onError: () => {
      setCouponError(t('checkout.couponValidationError'));
      setCouponApplied(false);
    },
  });

  // 创建订阅
  const createSubscriptionMutation = useMutation({
    mutationFn: createSubscription,
    onSuccess: async (subscription) => {
      // TODO: 根据支付提供商处理后续流程
      // Stripe: 使用 client_secret
      // PayPal: 重定向到 payment_url
      // Alipay: 重定向到 payment_url

      navigate(`/account/subscription?success=true`);
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || t('checkout.subscriptionError'));
      setIsProcessing(false);
    },
  });

  const handleApplyCoupon = () => {
    if (!couponCode.trim()) {
      setCouponError(t('checkout.enterCouponCode'));
      return;
    }

    validateCouponMutation.mutate({
      code: couponCode,
      plan_id: plan.id,
      amount: plan.price_usd,
    });
  };

  const handleRemoveCoupon = () => {
    setCouponCode('');
    setCouponApplied(false);
    setDiscountAmount(0);
    setFinalAmount(parseFloat(plan.price_usd));
    setCouponError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      await createSubscriptionMutation.mutateAsync({
        plan_id: plan.id,
        payment_provider: paymentProvider,
        coupon_code: couponApplied ? couponCode : undefined,
        auto_renew: autoRenew,
      });
    } catch (error) {
      // Error handled in mutation
    }
  };

  if (!plan) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-8 py-6 bg-blue-600">
            <h1 className="text-3xl font-bold text-white">{t('checkout.title')}</h1>
          </div>

          <form onSubmit={handleSubmit} className="p-8">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Left Column - Plan Summary */}
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  {t('checkout.planSummary')}
                </h2>

                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{plan.name_en}</h3>
                      <p className="text-sm text-gray-600">{plan.description_en}</p>
                    </div>
                    {plan.is_popular && (
                      <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                        {t('subscription.popular')}
                      </span>
                    )}
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-700">
                      <svg
                        className="h-5 w-5 text-green-500 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      {plan.max_video_quality.toUpperCase()} {t('subscription.quality')}
                    </div>
                    <div className="flex items-center text-sm text-gray-700">
                      <svg
                        className="h-5 w-5 text-green-500 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      {plan.max_concurrent_streams} {t('subscription.devices')}
                    </div>
                    {plan.allow_downloads && (
                      <div className="flex items-center text-sm text-gray-700">
                        <svg
                          className="h-5 w-5 text-green-500 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        {t('subscription.downloads')}
                      </div>
                    )}
                  </div>

                  <div className="border-t border-gray-200 pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-gray-700">{t('checkout.subtotal')}</span>
                      <span className="font-semibold">${plan.price_usd}</span>
                    </div>
                    {couponApplied && (
                      <div className="flex justify-between items-center mb-2 text-green-600">
                        <span>{t('checkout.discount')}</span>
                        <span>-${discountAmount.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="flex justify-between items-center text-lg font-bold">
                      <span>{t('checkout.total')}</span>
                      <span className="text-blue-600">${finalAmount.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Coupon Code */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('checkout.haveCoupon')}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                      disabled={couponApplied}
                      placeholder={t('checkout.enterCouponCode')}
                      className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    {couponApplied ? (
                      <button
                        type="button"
                        onClick={handleRemoveCoupon}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                      >
                        {t('checkout.remove')}
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={handleApplyCoupon}
                        disabled={validateCouponMutation.isPending}
                        className="px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 text-sm font-medium disabled:opacity-50"
                      >
                        {t('checkout.apply')}
                      </button>
                    )}
                  </div>
                  {couponError && (
                    <p className="mt-1 text-sm text-red-600">{couponError}</p>
                  )}
                  {couponApplied && (
                    <p className="mt-1 text-sm text-green-600">
                      {t('checkout.couponApplied')}
                    </p>
                  )}
                </div>
              </div>

              {/* Right Column - Payment Details */}
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  {t('checkout.paymentMethod')}
                </h2>

                {/* Payment Provider Selection */}
                <div className="space-y-3 mb-6">
                  <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      name="payment-provider"
                      value="stripe"
                      checked={paymentProvider === 'stripe'}
                      onChange={(e) => setPaymentProvider(e.target.value as 'stripe')}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3 flex-1">
                      <span className="font-medium text-gray-900">
                        {t('checkout.creditCard')}
                      </span>
                      <span className="text-sm text-gray-500 ml-2">
                        ({t('checkout.powered')} Stripe)
                      </span>
                    </div>
                    <div className="flex gap-1">
                      <img src="/icons/visa.svg" alt="Visa" className="h-6" />
                      <img src="/icons/mastercard.svg" alt="Mastercard" className="h-6" />
                    </div>
                  </label>

                  <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      name="payment-provider"
                      value="paypal"
                      checked={paymentProvider === 'paypal'}
                      onChange={(e) => setPaymentProvider(e.target.value as 'paypal')}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3 flex-1">
                      <span className="font-medium text-gray-900">PayPal</span>
                    </div>
                    <img src="/icons/paypal.svg" alt="PayPal" className="h-6" />
                  </label>

                  <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      name="payment-provider"
                      value="alipay"
                      checked={paymentProvider === 'alipay'}
                      onChange={(e) => setPaymentProvider(e.target.value as 'alipay')}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3 flex-1">
                      <span className="font-medium text-gray-900">
                        {t('checkout.alipay')}
                      </span>
                    </div>
                    <img src="/icons/alipay.svg" alt="Alipay" className="h-6" />
                  </label>
                </div>

                {/* Auto-renewal Option */}
                {plan.billing_period !== 'lifetime' && (
                  <div className="mb-6">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={autoRenew}
                        onChange={(e) => setAutoRenew(e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {t('checkout.autoRenew')}
                      </span>
                    </label>
                    <p className="mt-1 ml-6 text-xs text-gray-500">
                      {t('checkout.autoRenewDescription')}
                    </p>
                  </div>
                )}

                {/* Terms */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600">
                    {t('checkout.termsDescription')}
                  </p>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isProcessing || createSubscriptionMutation.isPending}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      {t('checkout.processing')}
                    </span>
                  ) : (
                    t('checkout.confirmAndPay', { amount: finalAmount.toFixed(2) })
                  )}
                </button>

                <p className="mt-4 text-center text-xs text-gray-500">
                  🔒 {t('checkout.securePayment')}
                </p>
              </div>
            </div>
          </form>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate(-1)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            ← {t('checkout.backToPlans')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
