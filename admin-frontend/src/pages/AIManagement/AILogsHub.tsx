import React, { Suspense } from 'react';
import { Tabs, Spin } from 'antd';
import {
  HistoryOutlined,
  DollarOutlined,
  ControlOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import RequestLogs from './RequestLogs';
import CostDashboard from './CostDashboard';
import QuotaManagement from './QuotaManagement';
import TemplateManagement from './TemplateManagement';
import '../../styles/page-layout.css';

const { TabPane } = Tabs;

const AILogsHub: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="page-container" style={{ padding: 0 }}>
      <Tabs
        defaultActiveKey="logs"
        type="card"
        size="large"
        style={{ height: '100%' }}
        tabBarStyle={{ margin: 0, padding: '0 16px', background: '#fff' }}
      >
        <TabPane
          tab={
            <span>
              <HistoryOutlined />
              {t('aiManagement.requestLogs')}
            </span>
          }
          key="logs"
        >
          <Suspense fallback={<div style={{ textAlign: 'center', padding: 50 }}><Spin size="large" /></div>}>
            <RequestLogs />
          </Suspense>
        </TabPane>

        <TabPane
          tab={
            <span>
              <DollarOutlined />
              {t('aiManagement.costMonitoring')}
            </span>
          }
          key="cost"
        >
          <Suspense fallback={<div style={{ textAlign: 'center', padding: 50 }}><Spin size="large" /></div>}>
            <CostDashboard />
          </Suspense>
        </TabPane>

        <TabPane
          tab={
            <span>
              <ControlOutlined />
              {t('aiManagement.quotaManagement')}
            </span>
          }
          key="quota"
        >
          <Suspense fallback={<div style={{ textAlign: 'center', padding: 50 }}><Spin size="large" /></div>}>
            <QuotaManagement />
          </Suspense>
        </TabPane>

        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              {t('aiManagement.templateManagement')}
            </span>
          }
          key="template"
        >
          <Suspense fallback={<div style={{ textAlign: 'center', padding: 50 }}><Spin size="large" /></div>}>
            <TemplateManagement />
          </Suspense>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default AILogsHub;
