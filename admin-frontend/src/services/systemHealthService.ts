import api from '../utils/axios';

// ============ Types ============

export interface ServiceStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time_ms?: number;
  message?: string;
  error?: string;
}

export interface DatabaseHealth extends ServiceStatus {
  database_name?: string;
  database_version?: string;
  pool_size?: number;
  checked_out?: number;
  checked_in?: number;
  overflow?: number;
  utilization_percent?: number;
}

export interface RedisHealth extends ServiceStatus {
  used_memory_mb?: number;
  max_memory_mb?: number | string;
  memory_utilization_percent?: number;
  keys_count?: number;
}

export interface BucketInfo {
  name: string;
  creation_date?: string;
  object_count?: number;
  size_gb?: number;
  size_bytes?: number;
  error?: string;
}

export interface StorageHealth extends ServiceStatus {
  bucket_exists?: boolean;
  can_read?: boolean;
  used_gb?: number;
  total_gb?: number;
  utilization_percent?: number;
  object_count?: number;
  buckets?: BucketInfo[];
  buckets_count?: number;
}

export interface TaskInfo {
  task_id: string;
  task_name: string;
  worker: string;
  args?: string;
  kwargs?: string;
}

export interface CeleryHealth extends ServiceStatus {
  workers_count: number;
  active_tasks: number;
  reserved_tasks?: number;
  scheduled_tasks?: number;
  total_succeeded?: number;
  total_failed?: number;
  active_task_list?: TaskInfo[];
  reserved_task_list?: TaskInfo[];
  registered_tasks?: string[];
}

export interface SystemResources {
  cpu?: {
    usage_percent: number;
    cores: number;
    frequency_mhz?: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  memory?: {
    used_gb: number;
    total_gb: number;
    available_gb: number;
    usage_percent: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  disk?: {
    used_gb: number;
    total_gb: number;
    free_gb: number;
    usage_percent: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  network?: {
    bytes_sent_gb: number;
    bytes_recv_gb: number;
    packets_sent: number;
    packets_recv: number;
    errors_in: number;
    errors_out: number;
    drops_in: number;
    drops_out: number;
  };
  processes?: {
    count: number;
  };
}

export interface AlertStatistics {
  active_total: number;
  critical: number;
  warning: number;
  resolved_24h: number;
}

export interface HealthData {
  timestamp: string;
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    database: DatabaseHealth;
    redis: RedisHealth;
    storage: StorageHealth;
    celery: CeleryHealth;
  };
  system_resources: SystemResources;
  alerts?: {
    statistics: AlertStatistics;
    new_alerts_count: number;
  };
}

export interface SystemAlert {
  id: number;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  metric_name?: string;
  metric_value?: number;
  threshold_value?: number;
  status: 'active' | 'resolved' | 'ignored';
  triggered_at: string;
  resolved_at?: string;
  acknowledged_by?: number;
  acknowledged_at?: string;
  notes?: string;
  context?: any;
  created_at: string;
  updated_at?: string;
}

export interface SLARecord {
  id: number;
  period_start: string;
  period_end: string;
  period_type: 'hourly' | 'daily' | 'weekly' | 'monthly';
  uptime_seconds: number;
  downtime_seconds: number;
  uptime_percentage: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate?: number;
  avg_response_time_ms?: number;
  p50_response_time_ms?: number;
  p95_response_time_ms?: number;
  p99_response_time_ms?: number;
  max_response_time_ms?: number;
  total_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  avg_cpu_usage?: number;
  avg_memory_usage?: number;
  avg_disk_usage?: number;
  created_at: string;
}

export interface CurrentSLA {
  period_start: string;
  period_end: string;
  elapsed_hours: number;
  uptime_percentage: number;
  metrics_collected: number;
  avg_db_response_time_ms?: number;
  total_alerts: number;
  critical_alerts: number;
  status: 'healthy' | 'degraded' | 'poor';
}

// ============ Health Monitoring APIs ============

export const getSystemHealth = async (useCache: boolean = true): Promise<HealthData> => {
  const { data } = await api.get('/api/v1/admin/system-health/health', {
    params: { use_cache: useCache }
  });
  return data;
};

export const getSystemMetrics = async (useCache: boolean = true) => {
  const { data } = await api.get('/api/v1/admin/system-health/metrics', {
    params: { use_cache: useCache }
  });
  return data;
};

export const getMetricsHistory = async (limit: number = 50) => {
  const { data } = await api.get('/api/v1/admin/system-health/history', {
    params: { limit }
  });
  return data;
};

export const getSystemInfo = async () => {
  const { data } = await api.get('/api/v1/admin/system-health/info');
  return data;
};

// ============ Alert Management APIs ============

export const getAlerts = async (params?: {
  page?: number;
  page_size?: number;
  status?: 'active' | 'resolved' | 'all';
  alert_type?: string;
  severity?: 'critical' | 'warning';
}): Promise<{ items: SystemAlert[]; total: number; page: number; page_size: number; pages: number }> => {
  const { data } = await api.get('/api/v1/admin/system-health/alerts', { params });
  return data;
};

export const getAlertStatistics = async (): Promise<{ timestamp: string; statistics: AlertStatistics }> => {
  const { data } = await api.get('/api/v1/admin/system-health/alerts/statistics');
  return data;
};

export const getActiveAlertsCount = async (): Promise<{ total: number; critical: number }> => {
  const { data } = await api.get('/api/v1/admin/system-health/alerts/active/count');
  return data;
};

export const acknowledgeAlert = async (alertId: number, notes?: string): Promise<any> => {
  const { data } = await api.post(`/api/v1/admin/system-health/alerts/${alertId}/acknowledge`, null, {
    params: { notes }
  });
  return data;
};

export const resolveAlert = async (alertId: number, notes?: string): Promise<any> => {
  const { data } = await api.post(`/api/v1/admin/system-health/alerts/${alertId}/resolve`, null, {
    params: { notes }
  });
  return data;
};

// ============ SLA Tracking APIs ============

export const getSLAReport = async (params?: {
  period_type?: 'hourly' | 'daily' | 'weekly' | 'monthly';
  limit?: number;
}): Promise<{ period_type: string; count: number; records: SLARecord[] }> => {
  const { data } = await api.get('/api/v1/admin/system-health/sla/report', { params });
  return data;
};

export const getSLASummary = async (days: number = 30): Promise<any> => {
  const { data } = await api.get('/api/v1/admin/system-health/sla/summary', {
    params: { days }
  });
  return data;
};

export const getCurrentSLA = async (): Promise<CurrentSLA> => {
  const { data } = await api.get('/api/v1/admin/system-health/sla/current');
  return data;
};

export const generateSLAReport = async (periodType: 'hourly' | 'daily'): Promise<any> => {
  const { data } = await api.post('/api/v1/admin/system-health/sla/generate', null, {
    params: { period_type: periodType }
  });
  return data;
};

export default {
  // Health
  getSystemHealth,
  getSystemMetrics,
  getMetricsHistory,
  getSystemInfo,

  // Alerts
  getAlerts,
  getAlertStatistics,
  getActiveAlertsCount,
  acknowledgeAlert,
  resolveAlert,

  // SLA
  getSLAReport,
  getSLASummary,
  getCurrentSLA,
  generateSLAReport,
};
