/**
 * 发票服务 API
 */

import api from './api';

export interface Invoice {
  id: number;
  user_id: number;
  subscription_id: number | null;
  payment_id: number | null;
  invoice_number: string;
  status: 'draft' | 'pending' | 'paid' | 'void' | 'uncollectible';
  currency: string;
  subtotal: string;
  tax: string;
  discount: string;
  total: string;
  amount_paid: string;
  amount_due: string;
  billing_email: string;
  billing_name: string | null;
  billing_address: string | null;
  line_items: any | null;
  payment_due_date: string | null;
  paid_at: string | null;
  voided_at: string | null;
  pdf_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CreateInvoiceRequest {
  subscription_id?: number;
  payment_id?: number;
  billing_email: string;
  billing_name?: string;
  billing_address?: string;
  line_items?: any;
  payment_due_date?: string;
}

export interface UpdateInvoiceRequest {
  billing_email?: string;
  billing_name?: string;
  billing_address?: string;
  line_items?: any;
}

export interface InvoiceDownloadResponse {
  pdf_url: string;
  invoice_number: string;
}

/**
 * 创建发票
 */
export const createInvoice = async (request: CreateInvoiceRequest): Promise<Invoice> => {
  const { data } = await api.post('/invoices', request);
  return data;
};

/**
 * 获取发票列表
 */
export const getInvoices = async (params?: {
  skip?: number;
  limit?: number;
}): Promise<{ items: Invoice[]; total: number; skip: number; limit: number }> => {
  const { data } = await api.get('/invoices', { params });
  return data;
};

/**
 * 获取发票详情
 */
export const getInvoice = async (invoiceId: number): Promise<Invoice> => {
  const { data } = await api.get(`/invoices/${invoiceId}`);
  return data;
};

/**
 * 根据发票号获取发票
 */
export const getInvoiceByNumber = async (invoiceNumber: string): Promise<Invoice> => {
  const { data } = await api.get(`/invoices/number/${invoiceNumber}`);
  return data;
};

/**
 * 更新发票
 */
export const updateInvoice = async (
  invoiceId: number,
  request: UpdateInvoiceRequest
): Promise<Invoice> => {
  const { data } = await api.patch(`/invoices/${invoiceId}`, request);
  return data;
};

/**
 * 作废发票
 */
export const voidInvoice = async (invoiceId: number): Promise<Invoice> => {
  const { data } = await api.post(`/invoices/${invoiceId}/void`);
  return data;
};

/**
 * 生成发票 PDF
 */
export const generateInvoicePdf = async (
  invoiceId: number
): Promise<InvoiceDownloadResponse> => {
  const { data } = await api.post(`/invoices/${invoiceId}/generate-pdf`);
  return data;
};

/**
 * 下载发票 PDF
 */
export const downloadInvoicePdf = async (invoiceId: number): Promise<Blob> => {
  const { data } = await api.get(`/invoices/${invoiceId}/download-pdf`, {
    responseType: 'blob',
  });
  return data;
};

/**
 * 发送发票邮件
 */
export const sendInvoiceEmail = async (invoiceId: number): Promise<{ message: string }> => {
  const { data } = await api.post(`/invoices/${invoiceId}/send-email`);
  return data;
};
