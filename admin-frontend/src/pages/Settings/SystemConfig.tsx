import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  message,
  Tabs,
  Space,
  Divider,
  Select,
  Tag,
} from 'antd'
import {
  SaveOutlined,
  ReloadOutlined,
  GlobalOutlined,
  CloudUploadOutlined,
  VideoCameraOutlined,
  CommentOutlined,
  UserOutlined,
  SafetyOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'

const { TextArea } = Input
const { TabPane } = Tabs
const { Option } = Select

const SystemConfig = () => {
  const [form] = Form.useForm()
  const queryClient = useQueryClient()  // Fetch system settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['system-settings'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/system/settings')
      return response.data
    },
  })

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: async (values: any) => {
      const response = await axios.put('/api/v1/admin/system/settings', values)
      return response.data
    },
    onSuccess: () => {
      message.success('系统设置已更新')
      queryClient.invalidateQueries({ queryKey: ['system-settings'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '更新失败')
    },
  })

  // Reset settings mutation
  const resetMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post('/api/v1/admin/system/settings/reset', null)
      return response.data
    },
    onSuccess: () => {
      message.success('系统设置已重置为默认值')
      queryClient.invalidateQueries({ queryKey: ['system-settings'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '重置失败')
    },
  })

  useEffect(() => {
    if (settings) {
      form.setFieldsValue(settings)
    }
  }, [settings, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      updateMutation.mutate(values)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  const handleReset = () => {
    if (window.confirm('确定要重置所有设置为默认值吗？此操作不可恢复。')) {
      resetMutation.mutate()
    }
  }

  return (
    <div>
      <Card
        title="系统配置"
        extra={
          <Space>
            <Button
              danger
              icon={<ReloadOutlined />}
              onClick={handleReset}
              loading={resetMutation.isPending}
            >
              重置为默认值
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSubmit}
              loading={updateMutation.isPending}
            >
              保存设置
            </Button>
          </Space>
        }
      >
        <Form form={form} layout="vertical" disabled={isLoading}>
          <Tabs defaultActiveKey="basic" size="large">
            {/* 网站基本信息 */}
            <TabPane
              tab={
                <span>
                  <GlobalOutlined />
                  网站信息
                </span>
              }
              key="basic"
            >
              <Form.Item label="网站名称" name="site_name" rules={[{ required: true }]}>
                <Input placeholder="视频网站" />
              </Form.Item>
              <Form.Item label="网站URL" name="site_url" rules={[{ required: true, type: 'url' }]}>
                <Input placeholder="http://localhost:3000" />
              </Form.Item>
              <Form.Item label="网站描述" name="site_description">
                <TextArea rows={3} placeholder="网站简介" />
              </Form.Item>
              <Form.Item label="关键词" name="site_keywords">
                <Input placeholder="视频,在线观看,电影" />
              </Form.Item>
              <Form.Item label="网站Logo URL" name="site_logo">
                <Input placeholder="https://example.com/logo.png" />
              </Form.Item>
              <Form.Item label="网站Favicon URL" name="site_favicon">
                <Input placeholder="https://example.com/favicon.ico" />
              </Form.Item>

              <Divider>SEO设置</Divider>

              <Form.Item label="SEO标题" name="seo_title">
                <Input placeholder="覆盖默认标题" />
              </Form.Item>
              <Form.Item label="SEO描述" name="seo_description">
                <TextArea rows={2} placeholder="搜索引擎描述" />
              </Form.Item>
              <Form.Item label="SEO关键词" name="seo_keywords">
                <Input placeholder="关键词1,关键词2,关键词3" />
              </Form.Item>
            </TabPane>

            {/* 上传设置 */}
            <TabPane
              tab={
                <span>
                  <CloudUploadOutlined />
                  上传设置
                </span>
              }
              key="upload"
            >
              <Form.Item label="视频最大大小 (MB)" name="upload_max_size">
                <InputNumber min={1} max={10240} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item label="允许的视频格式" name="upload_allowed_formats">
                <Select mode="tags" placeholder="输入格式后按回车">
                  <Option value="mp4">mp4</Option>
                  <Option value="avi">avi</Option>
                  <Option value="mkv">mkv</Option>
                  <Option value="webm">webm</Option>
                  <Option value="flv">flv</Option>
                </Select>
              </Form.Item>
              <Form.Item label="图片最大大小 (MB)" name="image_max_size">
                <InputNumber min={1} max={100} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item label="允许的图片格式" name="image_allowed_formats">
                <Select mode="tags" placeholder="输入格式后按回车">
                  <Option value="jpg">jpg</Option>
                  <Option value="jpeg">jpeg</Option>
                  <Option value="png">png</Option>
                  <Option value="webp">webp</Option>
                  <Option value="gif">gif</Option>
                </Select>
              </Form.Item>
            </TabPane>

            {/* 视频设置 */}
            <TabPane
              tab={
                <span>
                  <VideoCameraOutlined />
                  视频设置
                </span>
              }
              key="video"
            >
              <Form.Item label="自动审核通过" name="video_auto_approve" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="需要人工审核" name="video_require_review" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="默认清晰度" name="video_default_quality">
                <Select>
                  <Option value="360p">360p</Option>
                  <Option value="480p">480p</Option>
                  <Option value="720p">720p</Option>
                  <Option value="1080p">1080p</Option>
                  <Option value="4k">4K</Option>
                </Select>
              </Form.Item>
              <Form.Item label="启用转码" name="video_enable_transcode" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="转码格式" name="video_transcode_formats">
                <Select mode="multiple">
                  <Option value="360p">360p</Option>
                  <Option value="480p">480p</Option>
                  <Option value="720p">720p</Option>
                  <Option value="1080p">1080p</Option>
                  <Option value="4k">4K</Option>
                </Select>
              </Form.Item>
            </TabPane>

            {/* 评论设置 */}
            <TabPane
              tab={
                <span>
                  <CommentOutlined />
                  评论设置
                </span>
              }
              key="comment"
            >
              <Form.Item label="启用评论" name="comment_enable" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="需要审核" name="comment_require_approval" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="允许游客评论" name="comment_allow_guest" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="评论最大长度" name="comment_max_length">
                <InputNumber min={50} max={5000} style={{ width: '100%' }} />
              </Form.Item>
            </TabPane>

            {/* 用户设置 */}
            <TabPane
              tab={
                <span>
                  <UserOutlined />
                  用户设置
                </span>
              }
              key="user"
            >
              <Form.Item label="允许注册" name="user_enable_registration" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item
                label="需要邮箱验证"
                name="user_require_email_verification"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item label="默认头像URL" name="user_default_avatar">
                <Input placeholder="https://example.com/avatar.png" />
              </Form.Item>
              <Form.Item label="最大收藏数" name="user_max_favorites">
                <InputNumber min={100} max={10000} style={{ width: '100%' }} />
              </Form.Item>
            </TabPane>

            {/* 安全设置 */}
            <TabPane
              tab={
                <span>
                  <SafetyOutlined />
                  安全设置
                </span>
              }
              key="security"
            >
              <Form.Item label="启用验证码" name="security_enable_captcha" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="登录最大尝试次数" name="security_login_max_attempts">
                <InputNumber min={3} max={10} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item label="锁定时长 (分钟)" name="security_login_lockout_duration">
                <InputNumber min={5} max={120} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item label="会话超时 (秒)" name="security_session_timeout">
                <InputNumber min={1800} max={86400} style={{ width: '100%' }} />
              </Form.Item>
            </TabPane>

            {/* 其他设置 */}
            <TabPane
              tab={
                <span>
                  <SettingOutlined />
                  其他设置
                </span>
              }
              key="other"
            >
              <Form.Item label="维护模式" name="maintenance_mode" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item label="维护提示信息" name="maintenance_message">
                <TextArea rows={2} placeholder="网站正在维护中，请稍后访问" />
              </Form.Item>
              <Form.Item label="统计代码 (Google Analytics等)" name="analytics_code">
                <TextArea rows={3} placeholder="<!-- Google Analytics -->" />
              </Form.Item>
              <Form.Item label="自定义CSS" name="custom_css">
                <TextArea rows={4} placeholder=".custom { color: red; }" />
              </Form.Item>
              <Form.Item label="自定义JavaScript" name="custom_js">
                <TextArea rows={4} placeholder="console.log('custom');" />
              </Form.Item>
            </TabPane>
          </Tabs>
        </Form>
      </Card>
    </div>
  )
}

export default SystemConfig
