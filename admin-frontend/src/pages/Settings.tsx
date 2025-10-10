import { Tabs } from 'antd'
import { MailOutlined, FileTextOutlined, SettingOutlined } from '@ant-design/icons'
import EmailConfig from './Settings/EmailConfig'
import EmailTemplates from './Settings/EmailTemplates'
import SystemConfig from './Settings/SystemConfig'

const { TabPane } = Tabs

const Settings = () => {
  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>系统设置</h2>
      <Tabs defaultActiveKey="email" size="large">
        <TabPane
          tab={
            <span>
              <MailOutlined />
              邮件服务器
            </span>
          }
          key="email"
        >
          <EmailConfig />
        </TabPane>
        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              邮件模板
            </span>
          }
          key="templates"
        >
          <EmailTemplates />
        </TabPane>
        <TabPane
          tab={
            <span>
              <SettingOutlined />
              系统配置
            </span>
          }
          key="system"
        >
          <SystemConfig />
        </TabPane>
      </Tabs>
    </div>
  )
}

export default Settings
