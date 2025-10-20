import { useState, useEffect } from 'react';
import { Modal, Form, DatePicker, Alert, Space, Typography } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import dayjs, { Dayjs } from 'dayjs';

const { Text } = Typography;

export interface SchedulePublishFormData {
  scheduled_publish_at: string;
}

interface SchedulePublishModalProps {
  visible: boolean;
  videoId?: number;
  videoTitle?: string;
  currentScheduledTime?: string | null;
  onOk: (data: SchedulePublishFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

const SchedulePublishModal: React.FC<SchedulePublishModalProps> = ({
  visible,
  videoId,
  videoTitle,
  currentScheduledTime,
  onOk,
  onCancel,
  loading = false,
}) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      if (currentScheduledTime) {
        form.setFieldsValue({
          scheduled_time: dayjs(currentScheduledTime),
        });
      } else {
        form.resetFields();
      }
    }
  }, [visible, currentScheduledTime, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const scheduledDateTime = values.scheduled_time as Dayjs;

      await onOk({
        scheduled_publish_at: scheduledDateTime.toISOString(),
      });
      form.resetFields();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const disabledDate = (current: Dayjs) => {
    // 不能选择今天之前的日期
    return current && current < dayjs().startOf('day');
  };

  const disabledTime = (selectedDate: Dayjs | null) => {
    if (!selectedDate) return {};

    const now = dayjs();
    const isToday = selectedDate.isSame(now, 'day');

    if (!isToday) return {};

    // 如果是今天，禁用已过去的时间
    return {
      disabledHours: () => {
        const hours = [];
        for (let i = 0; i < now.hour(); i++) {
          hours.push(i);
        }
        return hours;
      },
      disabledMinutes: (selectedHour: number) => {
        if (selectedHour === now.hour()) {
          const minutes = [];
          for (let i = 0; i <= now.minute(); i++) {
            minutes.push(i);
          }
          return minutes;
        }
        return [];
      },
    };
  };

  return (
    <Modal
      title={
        <Space>
          <ClockCircleOutlined style={{ color: '#1890ff' }} />
          {t('video.operation.schedulePublish') || '定时发布'}
        </Space>
      }
      open={visible}
      onOk={handleSubmit}
      onCancel={onCancel}
      confirmLoading={loading}
      okText={t('common.confirm') || '确认'}
      cancelText={t('common.cancel') || '取消'}
      width={550}
    >
      <Alert
        message={t('video.operation.schedulePublishTip') || '设置定时发布后，视频将在指定时间自动发布'}
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {videoTitle && (
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">{t('video.title') || '视频标题'}:</Text>{' '}
          <Text strong>{videoTitle}</Text>
        </div>
      )}

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          scheduled_time: currentScheduledTime ? dayjs(currentScheduledTime) : undefined,
        }}
      >
        <Form.Item
          label={t('video.operation.scheduledTime') || '发布时间'}
          name="scheduled_time"
          rules={[
            { required: true, message: t('video.operation.scheduleTimeRequired') || '请选择发布时间' },
            {
              validator: (_, value: Dayjs) => {
                if (!value) return Promise.resolve();

                const now = dayjs();
                if (value.isBefore(now)) {
                  return Promise.reject(
                    new Error(t('video.operation.scheduleTimeMustBeFuture') || '发布时间必须是未来时间')
                  );
                }

                return Promise.resolve();
              },
            },
          ]}
        >
          <DatePicker
            showTime
            format="YYYY-MM-DD HH:mm"
            placeholder={t('video.operation.selectScheduleTime') || '选择发布时间'}
            style={{ width: '100%' }}
            disabledDate={disabledDate}
            disabledTime={(date) => disabledTime(date)}
            showNow={false}
          />
        </Form.Item>

        <Alert
          message={
            <div>
              <div style={{ marginBottom: 8 }}>
                <strong>{t('video.operation.scheduleNotes') || '注意事项'}:</strong>
              </div>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>{t('video.operation.scheduleNote1') || '设置定时发布后，视频状态将变为"草稿"'}</li>
                <li>{t('video.operation.scheduleNote2') || '系统会在设定时间自动将视频发布'}</li>
                <li>{t('video.operation.scheduleNote3') || '发布前可随时取消或修改发布时间'}</li>
              </ul>
            </div>
          }
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Form>
    </Modal>
  );
};

export default SchedulePublishModal;
