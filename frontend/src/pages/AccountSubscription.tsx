import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  getMyActiveSubscription,
  getMySubscriptions,
  cancelSubscription,
  updateSubscription,
} from '../services/subscription';
import { getPayments } from '../services/payment';
import { getInvoices, downloadInvoicePdf } from '../services/invoice';

const AccountSubscription: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelImmediately, setCancelImmediately] = useState(false);

  // 获取活跃订阅
  const { data: activeSubscription, isLoading: subscriptionLoading } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: getMyActiveSubscription,
  });

  // 获取订阅历史
  const { data: subscriptionsData } = useQuery({
    queryKey: ['my-subscriptions'],
    queryFn: getMySubscriptions,
  });

  // 获取支付历史
  const { data: paymentsData } = useQuery({
    queryKey: ['my-payments'],
    queryFn: () => getPayments({ limit: 10 }),
  });

  // 获取发票
  const { data: invoicesData } = useQuery({
    queryKey: ['my-invoices'],
    queryFn: () => getInvoices({ limit: 10 }),
  });

  // 取消订阅
  const cancelMutation = useMutation({
    mutationFn: (subscriptionId: number) =>
      cancelSubscription(subscriptionId, { immediately: cancelImmediately }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] });
      queryClient.invalidateQueries({ queryKey: ['my-subscriptions'] });
      setShowCancelModal(false);
      alert(
        cancelImmediately
          ? t('subscription.canceledImmediately')
          : t('subscription.canceledAtPeriodEnd')
      );
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || t('subscription.cancelError'));
    },
  });

  // 更新自动续费
  const updateAutoRenewMutation = useMutation({
    mutationFn: ({
      subscriptionId,
      autoRenew,
    }: {
      subscriptionId: number;
      autoRenew: boolean;
    }) => updateSubscription(subscriptionId, { auto_renew: autoRenew }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] });
    },
  });

  const handleDownloadInvoice = async (invoiceId: number) => {
    try {
      const blob = await downloadInvoicePdf(invoiceId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert(t('invoice.downloadError'));
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      trialing: 'bg-blue-100 text-blue-800',
      past_due: 'bg-yellow-100 text-yellow-800',
      canceled: 'bg-red-100 text-red-800',
      expired: 'bg-gray-100 text-gray-800',
    };

    const labels: Record<string, string> = {
      active: t('subscription.statusActive'),
      trialing: t('subscription.statusTrialing'),
      past_due: t('subscription.statusPastDue'),
      canceled: t('subscription.statusCanceled'),
      expired: t('subscription.statusExpired'),
    };

    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${styles[status]}`}>
        {labels[status] || status}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (subscriptionLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          {t('subscription.mySubscription')}
        </h1>

        {/* Active Subscription Card */}
        {activeSubscription ? (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {activeSubscription.plan?.name_en}
                  </h2>
                  {getStatusBadge(activeSubscription.status)}
                </div>
                <p className="text-gray-600">{activeSubscription.plan?.description_en}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-blue-600">
                  ${activeSubscription.plan?.price_usd}
                </p>
                <p className="text-sm text-gray-500">
                  / {activeSubscription.plan?.billing_period}
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">{t('subscription.features')}</h3>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-gray-700">
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
                    {activeSubscription.plan?.max_video_quality.toUpperCase()}{' '}
                    {t('subscription.quality')}
                  </li>
                  <li className="flex items-center text-sm text-gray-700">
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
                    {activeSubscription.plan?.max_concurrent_streams} {t('subscription.devices')}
                  </li>
                  {activeSubscription.plan?.allow_downloads && (
                    <li className="flex items-center text-sm text-gray-700">
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
                    </li>
                  )}
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-3">
                  {t('subscription.billingInfo')}
                </h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-sm text-gray-600">{t('subscription.nextBillingDate')}</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {formatDate(activeSubscription.current_period_end)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-600">{t('subscription.autoRenewal')}</dt>
                    <dd className="flex items-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={activeSubscription.auto_renew}
                          onChange={(e) =>
                            updateAutoRenewMutation.mutate({
                              subscriptionId: activeSubscription.id,
                              autoRenew: e.target.checked,
                            })
                          }
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        <span className="ml-3 text-sm font-medium text-gray-900">
                          {activeSubscription.auto_renew
                            ? t('subscription.enabled')
                            : t('subscription.disabled')}
                        </span>
                      </label>
                    </dd>
                  </div>
                  {activeSubscription.cancel_at_period_end && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                      <p className="text-sm text-yellow-800">
                        {t('subscription.willCancelOn', {
                          date: formatDate(activeSubscription.current_period_end),
                        })}
                      </p>
                    </div>
                  )}
                </dl>
              </div>
            </div>

            <div className="flex gap-4 pt-6 border-t border-gray-200">
              <button
                onClick={() => navigate('/subscription')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                {t('subscription.changePlan')}
              </button>
              {!activeSubscription.cancel_at_period_end && (
                <button
                  onClick={() => setShowCancelModal(true)}
                  className="px-6 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 font-medium"
                >
                  {t('subscription.cancelSubscription')}
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 mb-8 text-center">
            <svg
              className="h-16 w-16 text-gray-400 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {t('subscription.noActiveSubscription')}
            </h3>
            <p className="text-gray-600 mb-6">{t('subscription.noActiveDescription')}</p>
            <button
              onClick={() => navigate('/subscription')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              {t('subscription.browsePlans')}
            </button>
          </div>
        )}

        {/* Tabs for Payment History and Invoices */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button className="px-6 py-4 text-sm font-medium text-blue-600 border-b-2 border-blue-600">
                {t('subscription.paymentHistory')}
              </button>
              <button className="px-6 py-4 text-sm font-medium text-gray-500 hover:text-gray-700">
                {t('subscription.invoices')}
              </button>
            </nav>
          </div>

          {/* Payment History Table */}
          <div className="p-6">
            {paymentsData && paymentsData.items.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('payment.date')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('payment.amount')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('payment.method')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('payment.status')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {paymentsData.items.map((payment) => (
                      <tr key={payment.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(payment.created_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          ${payment.amount} {payment.currency.toUpperCase()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {payment.payment_provider}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(payment.status)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">{t('payment.noPayments')}</p>
            )}
          </div>
        </div>

        {/* Cancel Modal */}
        {showCancelModal && activeSubscription && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                {t('subscription.confirmCancel')}
              </h3>
              <p className="text-gray-600 mb-6">{t('subscription.cancelDescription')}</p>

              <label className="flex items-center mb-6">
                <input
                  type="checkbox"
                  checked={cancelImmediately}
                  onChange={(e) => setCancelImmediately(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {t('subscription.cancelImmediately')}
                </span>
              </label>

              <div className="flex gap-4">
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={() => cancelMutation.mutate(activeSubscription.id)}
                  disabled={cancelMutation.isPending}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  {cancelMutation.isPending ? t('common.processing') : t('subscription.confirm')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccountSubscription;
