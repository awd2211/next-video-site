/**
 * DashboardWidget - 可自定义的仪表盘组件容器
 * 包装各种统计卡片、图表等组件，支持拖拽和调整大小
 */
import React from 'react';
import { Card } from 'antd';
import { EyeInvisibleOutlined, DragOutlined } from '@ant-design/icons';
import './index.css';

interface DashboardWidgetProps {
  id: string;
  title?: string;
  children: React.ReactNode;
  editMode?: boolean;
  visible?: boolean;
  onToggleVisibility?: (id: string) => void;
  extra?: React.ReactNode;
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({
  id,
  title,
  children,
  editMode = false,
  visible = true,
  onToggleVisibility,
  extra,
}) => {
  if (!visible && !editMode) {
    return null;
  }

  return (
    <Card
      title={
        editMode ? (
          <div className="widget-header-edit">
            <DragOutlined className="drag-handle" />
            <span>{title}</span>
          </div>
        ) : (
          title
        )
      }
      className={`dashboard-widget ${!visible ? 'widget-hidden' : ''} ${editMode ? 'widget-edit-mode' : ''}`}
      extra={
        editMode ? (
          <EyeInvisibleOutlined
            className="visibility-toggle"
            onClick={() => onToggleVisibility?.(id)}
            style={{
              cursor: 'pointer',
              color: visible ? '#1890ff' : '#d9d9d9',
              fontSize: 16
            }}
          />
        ) : (
          extra
        )
      }
      bodyStyle={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {visible ? children : <div className="widget-hidden-overlay">Hidden</div>}
    </Card>
  );
};

export default DashboardWidget;
