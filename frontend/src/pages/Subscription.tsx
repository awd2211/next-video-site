import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getSubscriptionPlans, type SubscriptionPlan } from '../services/subscription';
import { getMyActiveSubscription } from '../services/subscription';

const Subscription: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [selectedBillingPeriod, setSelectedBillingPeriod] = useState<
    'monthly' | 'quarterly' | 'yearly' | 'lifetime'
  >('monthly');

  // 获取订阅套餐
  const { data: plansData, isLoading: plansLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: getSubscriptionPlans,
  });

  // 获取当前用户的订阅状态
  const { data: currentSubscription } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: getMyActiveSubscription,
  });

  const plans = plansData?.items || [];

  // 过滤当前计费周期的套餐
  const filteredPlans = plans.filter(
    (plan) => plan.billing_period === selectedBillingPeriod && plan.is_active
  );

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    navigate(`/checkout`, { state: { plan } });
  };

  const getBillingPeriodLabel = (period: string) => {
    switch (period) {
      case 'monthly':
        return t('subscription.monthly');
      case 'quarterly':
        return t('subscription.quarterly');
      case 'yearly':
        return t('subscription.yearly');
      case 'lifetime':
        return t('subscription.lifetime');
      default:
        return period;
    }
  };

  const formatPrice = (plan: SubscriptionPlan) => {
    return `$${plan.price_usd}`;
  };

  const getSavingsPercentage = (plan: SubscriptionPlan) => {
    // 找到对应的月度套餐来计算节省百分比
    const monthlyPlan = plans.find(
      (p) =>
        p.billing_period === 'monthly' &&
        p.max_video_quality === plan.max_video_quality &&
        p.max_concurrent_streams === plan.max_concurrent_streams
    );

    if (!monthlyPlan || plan.billing_period === 'monthly') {
      return null;
    }

    const monthlyPrice = parseFloat(monthlyPlan.price_usd);
    const planPrice = parseFloat(plan.price_usd);

    let monthsMultiplier = 1;
    if (plan.billing_period === 'quarterly') monthsMultiplier = 3;
    if (plan.billing_period === 'yearly') monthsMultiplier = 12;

    const expectedPrice = monthlyPrice * monthsMultiplier;
    const savings = ((expectedPrice - planPrice) / expectedPrice) * 100;

    return Math.round(savings);
  };

  if (plansLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-300">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            {t('subscription.chooseYourPlan')}
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            {t('subscription.planDescription')}
          </p>
        </div>

        {/* Current Subscription Alert */}
        {currentSubscription && (
          <div className="mb-8 bg-blue-900/20 border border-blue-700 rounded-lg p-4 max-w-3xl mx-auto">
            <div className="flex items-center">
              <svg
                className="h-5 w-5 text-blue-400 mr-3"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
              <div className="flex-1">
                <p className="text-sm text-blue-200">
                  {t('subscription.currentlySubscribed', {
                    plan: currentSubscription.plan?.name_en,
                  })}
                </p>
              </div>
              <button
                onClick={() => navigate('/account/subscription')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium"
              >
                {t('subscription.manageSubscription')}
              </button>
            </div>
          </div>
        )}

        {/* Billing Period Selector */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex rounded-lg border border-gray-700 bg-gray-800 p-1">
            {['monthly', 'quarterly', 'yearly', 'lifetime'].map((period) => (
              <button
                key={period}
                onClick={() =>
                  setSelectedBillingPeriod(
                    period as 'monthly' | 'quarterly' | 'yearly' | 'lifetime'
                  )
                }
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedBillingPeriod === period
                    ? 'bg-red-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                {getBillingPeriodLabel(period)}
                {period === 'yearly' && (
                  <span className="ml-2 text-xs bg-green-900/40 text-green-400 px-2 py-0.5 rounded">
                    {t('subscription.save20')}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {filteredPlans.map((plan) => {
            const savings = getSavingsPercentage(plan);

            return (
              <div
                key={plan.id}
                className={`relative bg-gray-800 rounded-2xl shadow-lg overflow-hidden transition-transform hover:scale-105 ${
                  plan.is_popular ? 'ring-2 ring-red-600' : ''
                }`}
              >
                {/* Popular Badge */}
                {plan.is_popular && (
                  <div className="absolute top-0 right-0 bg-red-600 text-white px-4 py-1 text-sm font-medium rounded-bl-lg">
                    {t('subscription.mostPopular')}
                  </div>
                )}

                {/* Savings Badge */}
                {savings && (
                  <div className="absolute top-0 left-0 bg-green-500 text-white px-3 py-1 text-xs font-bold rounded-br-lg">
                    {t('subscription.savePercent', { percent: savings })}
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {plan.name_en}
                  </h3>

                  {/* Plan Description */}
                  <p className="text-gray-400 mb-6">{plan.description_en}</p>

                  {/* Price */}
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-white">
                      {formatPrice(plan)}
                    </span>
                    {plan.billing_period !== 'lifetime' && (
                      <span className="text-gray-400 ml-2">
                        / {getBillingPeriodLabel(plan.billing_period)}
                      </span>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-4 mb-8">
                    <li className="flex items-start">
                      <svg
                        className="h-6 w-6 text-green-500 mr-3 flex-shrink-0"
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
                      <span className="text-gray-300">
                        {t('subscription.videoQuality', {
                          quality: plan.max_video_quality.toUpperCase(),
                        })}
                      </span>
                    </li>
                    <li className="flex items-start">
                      <svg
                        className="h-6 w-6 text-green-500 mr-3 flex-shrink-0"
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
                      <span className="text-gray-300">
                        {t('subscription.concurrentStreams', {
                          count: plan.max_concurrent_streams,
                        })}
                      </span>
                    </li>
                    {plan.allow_downloads && (
                      <li className="flex items-start">
                        <svg
                          className="h-6 w-6 text-green-500 mr-3 flex-shrink-0"
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
                        <span className="text-gray-300">
                          {t('subscription.allowDownloads')}
                        </span>
                      </li>
                    )}
                    {plan.trial_days > 0 && (
                      <li className="flex items-start">
                        <svg
                          className="h-6 w-6 text-green-500 mr-3 flex-shrink-0"
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
                        <span className="text-gray-300">
                          {t('subscription.freeTrial', { days: plan.trial_days })}
                        </span>
                      </li>
                    )}
                  </ul>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSelectPlan(plan)}
                    className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                      plan.is_popular
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-gray-700 hover:bg-gray-600 text-white'
                    }`}
                  >
                    {currentSubscription?.plan_id === plan.id
                      ? t('subscription.currentPlan')
                      : t('subscription.choosePlan')}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            {t('subscription.faqTitle')}
          </h2>
          <div className="space-y-4">
            <details className="bg-gray-800 rounded-lg p-6 shadow">
              <summary className="font-semibold text-white cursor-pointer">
                {t('subscription.faq1Question')}
              </summary>
              <p className="mt-4 text-gray-400">{t('subscription.faq1Answer')}</p>
            </details>
            <details className="bg-gray-800 rounded-lg p-6 shadow">
              <summary className="font-semibold text-white cursor-pointer">
                {t('subscription.faq2Question')}
              </summary>
              <p className="mt-4 text-gray-400">{t('subscription.faq2Answer')}</p>
            </details>
            <details className="bg-gray-800 rounded-lg p-6 shadow">
              <summary className="font-semibold text-white cursor-pointer">
                {t('subscription.faq3Question')}
              </summary>
              <p className="mt-4 text-gray-400">{t('subscription.faq3Answer')}</p>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
