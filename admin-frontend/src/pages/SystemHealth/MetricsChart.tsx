import { useQuery } from '@tanstack/react-query';
import { Card, Empty, Spin } from 'antd';
import { Line } from '@ant-design/charts';
import axios from '@/utils/axios';

interface MetricsHistory {
  count: number;
  history: Array<{
    timestamp: string;
    data: {
      cpu_usage: number;
      memory_usage: number;
      disk_usage: number;
      db_response_time: number;
      redis_response_time: number;
      storage_response_time: number;
    };
  }>;
}

interface MetricsChartProps {
  metric: 'cpu_usage' | 'memory_usage' | 'disk_usage' | 'db_response_time' | 'redis_response_time' | 'storage_response_time';
  title: string;
  unit?: string;
  height?: number;
}

const MetricsChart = ({ metric, title, unit = '%', height = 200 }: MetricsChartProps) => {
  const { data, isLoading } = useQuery<MetricsHistory>({
    queryKey: ['metrics-history', metric],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/system/history', {
        params: { limit: 50 },
      });
      return response.data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  if (isLoading) {
    return (
      <Card title={title}>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.count === 0) {
    return (
      <Card title={title}>
        <Empty description="No historical data available yet" />
      </Card>
    );
  }

  // Transform data for chart
  const chartData = data.history.map((entry) => ({
    time: new Date(entry.timestamp).toLocaleTimeString(),
    value: entry.data[metric] || 0,
  }));

  const config = {
    data: chartData,
    xField: 'time',
    yField: 'value',
    height,
    smooth: true,
    animation: false,
    point: {
      size: 3,
      shape: 'circle',
    },
    tooltip: {
      formatter: (datum: any) => ({
        name: title,
        value: `${datum.value.toFixed(2)}${unit}`,
      }),
    },
    xAxis: {
      label: {
        autoRotate: true,
        autoHide: true,
      },
    },
    yAxis: {
      label: {
        formatter: (v: string) => `${v}${unit}`,
      },
    },
    color: '#1890ff',
  };

  return (
    <Card title={title} size="small">
      <Line {...config} />
    </Card>
  );
};

export default MetricsChart;
