import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Card,
  Row,
  Col,
  message,
  Space,
  Spin,
} from 'antd'
import { SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useHotkeys } from 'react-hotkeys-hook'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import ChunkedUploader from '../../components/ChunkedUploader'

const { TextArea } = Input
const { Option } = Select

const VideoForm = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const isEdit = !!id
  
  // Ctrl+S to save
  useHotkeys('ctrl+s', (e) => {
    e.preventDefault()
    form.submit()
  }, { enableOnFormTags: true })

  // 获取分类列表
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/categories')
      return response.data
    },
  })

  // 获取国家列表
  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/countries')
      return response.data
    },
  })

  // 获取标签列表
  const { data: tags } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/tags')
      return response.data
    },
  })

  // 如果是编辑模式，获取视频详情
  const { data: video, isLoading: videoLoading } = useQuery({
    queryKey: ['admin-video', id],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/admin/videos/${id}`)
      return response.data
    },
    enabled: isEdit,
  })

  // 填充表单数据
  useEffect(() => {
    if (video) {
      form.setFieldsValue({
        ...video,
        release_date: video.release_date ? dayjs(video.release_date) : null,
        category_ids: video.categories?.map((c: any) => c.id) || [],
        tag_ids: video.tags?.map((t: any) => t.id) || [],
      })
    }
  }, [video, form])

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const data = {
        ...values,
        release_date: values.release_date ? values.release_date.format('YYYY-MM-DD') : null,
        category_ids: values.category_ids || [],
        tag_ids: values.tag_ids || [],
        actor_ids: values.actor_ids || [],
        director_ids: values.director_ids || [],
      }

      if (isEdit) {
        await axios.put(`/api/v1/admin/videos/${id}`, data)
        message.success('视频更新成功！')
      } else {
        await axios.post('/api/v1/admin/videos', data)
        message.success('视频创建成功！')
      }

      navigate('/videos')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  if (isEdit && videoLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <Space style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/videos')}>
          返回列表
        </Button>
        <h2 style={{ margin: 0 }}>{isEdit ? '编辑视频' : '新增视频'}</h2>
      </Space>

      <Form 
        form={form} 
        layout="vertical" 
        onFinish={onFinish} 
        autoComplete="off"
        validateTrigger="onBlur"
      >
        <Row gutter={24}>
          {/* 左侧列 */}
          <Col span={16}>
            <Card title="基本信息" style={{ marginBottom: 24 }}>
              <Form.Item
                name="title"
                label="标题"
                rules={[
                  { required: true, message: '请输入标题' },
                  { min: 2, message: '标题至少2个字符' },
                  { max: 500, message: '标题不能超过500个字符' },
                ]}
                hasFeedback
              >
                <Input 
                  placeholder="请输入视频标题" 
                  size="large"
                  showCount
                  maxLength={500}
                />
              </Form.Item>

              <Form.Item 
                name="original_title" 
                label="原始标题"
                rules={[
                  { max: 500, message: '原始标题不能超过500个字符' },
                ]}
              >
                <Input 
                  placeholder="请输入原始标题（如外文标题）"
                  showCount
                  maxLength={500}
                />
              </Form.Item>

              <Form.Item 
                name="description" 
                label="简介"
                rules={[
                  { max: 2000, message: '简介不能超过2000个字符' },
                ]}
              >
                <TextArea 
                  rows={6} 
                  placeholder="请输入视频简介"
                  showCount
                  maxLength={2000}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="video_type"
                    label="类型"
                    rules={[{ required: true, message: '请选择类型' }]}
                    hasFeedback
                  >
                    <Select placeholder="请选择视频类型">
                      <Option value="movie">电影</Option>
                      <Option value="tv_series">电视剧</Option>
                      <Option value="anime">动漫</Option>
                      <Option value="documentary">纪录片</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="status"
                    label="状态"
                    rules={[{ required: true, message: '请选择状态' }]}
                    hasFeedback
                  >
                    <Select placeholder="请选择状态">
                      <Option value="draft">草稿</Option>
                      <Option value="published">已发布</Option>
                      <Option value="archived">已归档</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="release_year" label="上映年份">
                    <InputNumber style={{ width: '100%' }} min={1900} max={2100} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="release_date" label="上映日期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="duration" label="时长（分钟）">
                    <InputNumber style={{ width: '100%' }} min={1} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item name="country_id" label="国家/地区">
                <Select
                  placeholder="请选择国家/地区"
                  loading={!countries}
                  showSearch
                  optionFilterProp="children"
                >
                  {countries?.map((country: any) => (
                    <Option key={country.id} value={country.id}>
                      {country.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item name="language" label="语言">
                <Input placeholder="例如：中文 / 英语 / 日语" />
              </Form.Item>
            </Card>

            <Card title="文件上传" style={{ marginBottom: 24 }}>
              <Form.Item label="视频文件">
                <ChunkedUploader
                  videoId={isEdit ? Number(id) : undefined}
                  uploadType="video"
                  accept="video/*"
                  maxSize={2048}
                  onUploadComplete={(url) => {
                    form.setFieldsValue({ video_url: url })
                    message.success('视频上传成功')
                  }}
                />
              </Form.Item>

              <Form.Item name="video_url" label="视频地址">
                <Input placeholder="视频播放地址（自动填充或手动输入）" />
              </Form.Item>

              <Form.Item label="海报图片上传">
                <ChunkedUploader
                  videoId={isEdit ? Number(id) : undefined}
                  uploadType="poster"
                  accept="image/*"
                  maxSize={10}
                  onUploadComplete={(url) => {
                    form.setFieldsValue({ poster_url: url })
                    message.success('海报上传成功')
                  }}
                />
              </Form.Item>

              <Form.Item name="poster_url" label="海报地址">
                <Input placeholder="海报图片 URL（自动填充或手动输入）" />
              </Form.Item>

              <Form.Item label="背景图片上传">
                <ChunkedUploader
                  videoId={isEdit ? Number(id) : undefined}
                  uploadType="backdrop"
                  accept="image/*"
                  maxSize={10}
                  onUploadComplete={(url) => {
                    form.setFieldsValue({ backdrop_url: url })
                    message.success('背景图片上传成功')
                  }}
                />
              </Form.Item>

              <Form.Item name="backdrop_url" label="背景地址">
                <Input placeholder="背景图片 URL（自动填充或手动输入）" />
              </Form.Item>

              <Form.Item name="trailer_url" label="预告片地址">
                <Input placeholder="预告片地址（可选）" />
              </Form.Item>
            </Card>

            <Card title="剧集信息" style={{ marginBottom: 24 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="total_seasons" label="总季数">
                    <InputNumber style={{ width: '100%' }} min={0} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="total_episodes" label="总集数">
                    <InputNumber style={{ width: '100%' }} min={0} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* 右侧列 */}
          <Col span={8}>
            <Card title="分类和标签" style={{ marginBottom: 24 }}>
              <Form.Item name="category_ids" label="分类">
                <Select
                  mode="multiple"
                  placeholder="请选择分类"
                  loading={!categories}
                  maxTagCount={3}
                >
                  {categories?.map((cat: any) => (
                    <Option key={cat.id} value={cat.id}>
                      {cat.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item name="tag_ids" label="标签">
                <Select
                  mode="multiple"
                  placeholder="请选择标签"
                  loading={!tags}
                  maxTagCount="responsive"
                >
                  {tags?.map((tag: any) => (
                    <Option key={tag.id} value={tag.id}>
                      {tag.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Card>

            <Card title="操作" style={{ marginBottom: 24 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  size="large"
                  icon={<SaveOutlined />}
                >
                  {isEdit ? '保存修改' : '创建视频'}
                </Button>
                <Button block onClick={() => navigate('/videos')}>
                  取消
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>
      </Form>
    </div>
  )
}

export default VideoForm
