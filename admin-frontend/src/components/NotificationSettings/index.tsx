/**
 * NotificationSettings Component
 * 通知偏好设置组件，可以嵌入到 Settings 页面
 */
import { Card, Switch, Checkbox, TimePicker, Button, Space, Divider, message, Select, Slider, Tag } from 'antd'
import { BellOutlined, SoundOutlined, DesktopOutlined, MobileOutlined } from '@ant-design/icons'
import { useNotificationPreferences } from '@/hooks/useNotificationPreferences'
import { desktopNotification } from '@/utils/desktopNotification'
import dayjs from 'dayjs'

const { Option } = Select

export default function NotificationSettings() {
  const { preferences, updatePreferences, resetPreferences } = useNotificationPreferences()

  const handleRequestDesktopPermission = async () => {
    const permission = await desktopNotification.requestPermission()
    if (permission === 'granted') {
      updatePreferences({ enableDesktopNotification: true })
      message.success('桌面通知权限已授予')

      // 发送测试通知
      desktopNotification.show({
        title: '测试通知',
        body: '桌面通知已成功启用！',
        severity: 'info',
      })
    } else if (permission === 'denied') {
      message.error('桌面通知权限被拒绝，请在浏览器设置中手动启用')
    }
  }

  const permissionStatus = desktopNotification.getPermission()

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* 通知方式 */}
      <Card
        title={<><BellOutlined /> 通知方式</>}
        size="small"
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* 声音提醒 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <SoundOutlined />
              <span>启用声音提醒</span>
            </Space>
            <Switch
              checked={preferences.enableSound}
              onChange={(checked) => {
                updatePreferences({ enableSound: checked })
                message.success(checked ? '声音提醒已启用' : '声音提醒已禁用')
              }}
            />
          </div>

          {/* 桌面通知 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <DesktopOutlined />
              <span>启用桌面通知</span>
              {permissionStatus === 'denied' && (
                <Tag color="red">权限被拒绝</Tag>
              )}
              {permissionStatus === 'default' && (
                <Tag color="orange">需要授权</Tag>
              )}
            </Space>
            <Space>
              {permissionStatus !== 'granted' && (
                <Button size="small" onClick={handleRequestDesktopPermission}>
                  请求权限
                </Button>
              )}
              <Switch
                checked={preferences.enableDesktopNotification && permissionStatus === 'granted'}
                disabled={permissionStatus !== 'granted'}
                onChange={(checked) => {
                  updatePreferences({ enableDesktopNotification: checked })
                  message.success(checked ? '桌面通知已启用' : '桌面通知已禁用')
                }}
              />
            </Space>
          </div>

          {/* 震动提醒 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <MobileOutlined />
              <span>启用震动提醒（移动端）</span>
            </Space>
            <Switch
              checked={preferences.enableVibration}
              onChange={(checked) => {
                updatePreferences({ enableVibration: checked })
                message.success(checked ? '震动提醒已启用' : '震动提醒已禁用')

                // 测试震动
                if (checked && 'vibrate' in navigator) {
                  navigator.vibrate([200, 100, 200])
                }
              }}
            />
          </div>
        </Space>
      </Card>

      {/* 通知位置 */}
      <Card title="通知位置" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <span style={{ fontSize: 13, color: '#666' }}>应用内通知弹窗的显示位置</span>
          <Select
            value={preferences.notificationPosition}
            onChange={(value) => updatePreferences({ notificationPosition: value })}
            style={{ width: '100%' }}
          >
            <Option value="topRight">右上角</Option>
            <Option value="topLeft">左上角</Option>
            <Option value="bottomRight">右下角</Option>
            <Option value="bottomLeft">左下角</Option>
          </Select>
        </Space>
      </Card>

      {/* 严重程度过滤 */}
      <Card title="严重程度过滤" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <span style={{ fontSize: 13, color: '#666' }}>选择要显示的通知严重程度</span>
          <Checkbox
            checked={preferences.severityFilter.info}
            onChange={(e) =>
              updatePreferences({
                severityFilter: { ...preferences.severityFilter, info: e.target.checked },
              })
            }
          >
            <Tag color="blue">信息</Tag> 常规信息通知
          </Checkbox>
          <Checkbox
            checked={preferences.severityFilter.warning}
            onChange={(e) =>
              updatePreferences({
                severityFilter: { ...preferences.severityFilter, warning: e.target.checked },
              })
            }
          >
            <Tag color="orange">警告</Tag> 警告级别通知
          </Checkbox>
          <Checkbox
            checked={preferences.severityFilter.error}
            onChange={(e) =>
              updatePreferences({
                severityFilter: { ...preferences.severityFilter, error: e.target.checked },
              })
            }
          >
            <Tag color="red">错误</Tag> 错误级别通知
          </Checkbox>
          <Checkbox
            checked={preferences.severityFilter.critical}
            onChange={(e) =>
              updatePreferences({
                severityFilter: { ...preferences.severityFilter, critical: e.target.checked },
              })
            }
          >
            <Tag color="red">严重</Tag> 严重错误通知（建议保持启用）
          </Checkbox>
        </Space>
      </Card>

      {/* 免打扰时段 */}
      <Card title="免打扰时段" size="small">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>启用免打扰</span>
            <Switch
              checked={preferences.quietHours.enabled}
              onChange={(checked) =>
                updatePreferences({
                  quietHours: { ...preferences.quietHours, enabled: checked },
                })
              }
            />
          </div>

          {preferences.quietHours.enabled && (
            <>
              <span style={{ fontSize: 13, color: '#666' }}>
                在免打扰时段，只会显示严重级别（critical）的通知
              </span>
              <Space>
                <span>从</span>
                <TimePicker
                  format="HH:mm"
                  value={dayjs(preferences.quietHours.startTime, 'HH:mm')}
                  onChange={(time) =>
                    updatePreferences({
                      quietHours: {
                        ...preferences.quietHours,
                        startTime: time?.format('HH:mm') || '22:00',
                      },
                    })
                  }
                />
                <span>到</span>
                <TimePicker
                  format="HH:mm"
                  value={dayjs(preferences.quietHours.endTime, 'HH:mm')}
                  onChange={(time) =>
                    updatePreferences({
                      quietHours: {
                        ...preferences.quietHours,
                        endTime: time?.format('HH:mm') || '08:00',
                      },
                    })
                  }
                />
              </Space>
            </>
          )}
        </Space>
      </Card>

      {/* 最大可见通知数 */}
      <Card title="显示设置" size="small">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <div style={{ marginBottom: 8 }}>
              <span>最大同时显示通知数：</span>
              <span style={{ fontWeight: 'bold', marginLeft: 8 }}>{preferences.maxVisibleNotifications}</span>
            </div>
            <Slider
              min={1}
              max={10}
              value={preferences.maxVisibleNotifications}
              onChange={(value) => updatePreferences({ maxVisibleNotifications: value })}
              marks={{
                1: '1',
                5: '5',
                10: '10',
              }}
            />
            <span style={{ fontSize: 12, color: '#999' }}>
              同时显示超过此数量的通知时，旧通知会自动关闭
            </span>
          </div>
        </Space>
      </Card>

      <Divider />

      {/* 重置按钮 */}
      <div style={{ textAlign: 'center' }}>
        <Button onClick={() => {
          resetPreferences()
          message.success('通知偏好已重置为默认设置')
        }}>
          重置为默认设置
        </Button>
      </div>

      {/* 使用说明 */}
      <Card size="small" style={{ background: '#f0f5ff', borderColor: '#adc6ff' }}>
        <Space direction="vertical" size="small">
          <div><strong>💡 使用说明：</strong></div>
          <div>• 声音提醒：收到通知时播放音效</div>
          <div>• 桌面通知：在浏览器外显示通知弹窗（需要授权）</div>
          <div>• 震动提醒：在移动端收到严重通知时震动</div>
          <div>• 免打扰时段：在指定时间段内只显示严重级别通知</div>
          <div>• 严重程度：critical &gt; error &gt; warning &gt; info</div>
        </Space>
      </Card>
    </Space>
  )
}
