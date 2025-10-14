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
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import ChunkedUploader from '../../components/ChunkedUploader'
import { createFormRules } from '@/utils/formRules'
import { VALIDATION_LIMITS, NUMBER_LIMITS } from '@/utils/validationConfig'

const { TextArea } = Input
const { Option } = Select

const VideoForm = () => {
  const { t } = useTranslation()
  const formRules = createFormRules(t)
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
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        marginBottom: 24,
        paddingBottom: 16,
        borderBottom: '1px solid #e9e9e7'
      }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/videos')}
          style={{ borderRadius: 8 }}
        >
          返回列表
        </Button>
        <h2 style={{
          margin: 0,
          fontSize: 20,
          fontWeight: 600,
          color: '#16191f'
        }}>
          {isEdit ? '编辑视频' : '新增视频'}
        </h2>
      </div>

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
                label={t('video.title')}
                rules={[
                  formRules.required(t('video.title')),
                  formRules.length(VALIDATION_LIMITS.VIDEO_TITLE.min, VALIDATION_LIMITS.VIDEO_TITLE.max)
                ]}
                hasFeedback
              >
                <Input 
                  placeholder={t('video.titlePlaceholder')} 
                  size="large"
                  showCount
                  maxLength={VALIDATION_LIMITS.VIDEO_TITLE.max}
                />
              </Form.Item>

              <Form.Item 
                name="original_title" 
                label={t('video.originalTitle')}
                rules={[
                  formRules.maxLength(VALIDATION_LIMITS.VIDEO_ORIGINAL_TITLE.max)
                ]}
              >
                <Input 
                  placeholder={t('video.originalTitlePlaceholder')}
                  showCount
                  maxLength={VALIDATION_LIMITS.VIDEO_ORIGINAL_TITLE.max}
                />
              </Form.Item>

              <Form.Item 
                name="description" 
                label={t('video.description')}
                rules={[
                  formRules.maxLength(VALIDATION_LIMITS.VIDEO_DESCRIPTION.max)
                ]}
              >
                <TextArea 
                  rows={6} 
                  placeholder={t('video.descriptionPlaceholder')}
                  showCount
                  maxLength={VALIDATION_LIMITS.VIDEO_DESCRIPTION.max}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="video_type"
                    label={t('video.type')}
                    rules={[formRules.required(t('video.type'))]}
                    hasFeedback
                  >
                    <Select placeholder={t('video.typePlaceholder')}>
                      <Option value="movie">{t('category.movie')}</Option>
                      <Option value="tv_series">{t('category.tvSeries')}</Option>
                      <Option value="anime">{t('category.anime')}</Option>
                      <Option value="documentary">{t('category.documentary')}</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="status"
                    label={t('video.status')}
                    rules={[formRules.required(t('video.status'))]}
                    hasFeedback
                  >
                    <Select placeholder={t('video.statusPlaceholder')}>
                      <Option value="DRAFT">{t('video.draft')}</Option>
                      <Option value="PUBLISHED">{t('video.published')}</Option>
                      <Option value="ARCHIVED">{t('video.archived')}</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item 
                    name="release_year" 
                    label={t('video.releaseYear')}
                    rules={[formRules.numberRange(NUMBER_LIMITS.YEAR.min, NUMBER_LIMITS.YEAR.max)]}
                  >
                    <InputNumber 
                      style={{ width: '100%' }} 
                      min={NUMBER_LIMITS.YEAR.min} 
                      max={NUMBER_LIMITS.YEAR.max} 
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="release_date" label={t('video.releaseDate')}>
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item 
                    name="duration" 
                    label={t('video.duration')}
                    rules={[formRules.numberRange(1, NUMBER_LIMITS.DURATION.max)]}
                  >
                    <InputNumber 
                      style={{ width: '100%' }} 
                      min={1}
                      max={NUMBER_LIMITS.DURATION.max}
                    />
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

              <Form.Item
                name="video_url"
                label={t('video.videoUrl')}
                rules={[formRules.url]}
              >
                <Input placeholder={t('video.videoUrlPlaceholder')} />
              </Form.Item>

              <Form.Item label={t('video.posterUpload')}>
                <ChunkedUploader
                  videoId={isEdit ? Number(id) : undefined}
                  uploadType="poster"
                  accept="image/*"
                  maxSize={10}
                  onUploadComplete={(url) => {
                    form.setFieldsValue({ poster_url: url })
                    message.success(t('video.posterUploadSuccess'))
                  }}
                />
              </Form.Item>

              <Form.Item
                name="poster_url"
                label={t('video.posterUrl')}
                rules={[formRules.url]}
              >
                <Input placeholder={t('video.posterUrlPlaceholder')} />
              </Form.Item>

              <Form.Item label={t('video.backdropUpload')}>
                <ChunkedUploader
                  videoId={isEdit ? Number(id) : undefined}
                  uploadType="backdrop"
                  accept="image/*"
                  maxSize={10}
                  onUploadComplete={(url) => {
                    form.setFieldsValue({ backdrop_url: url })
                    message.success(t('video.backdropUploadSuccess'))
                  }}
                />
              </Form.Item>

              <Form.Item
                name="backdrop_url"
                label={t('video.backdropUrl')}
                rules={[formRules.url]}
              >
                <Input placeholder={t('video.backdropUrlPlaceholder')} />
              </Form.Item>

              <Form.Item
                name="trailer_url"
                label={t('video.trailerUrl')}
                rules={[formRules.url]}
              >
                <Input placeholder={t('video.trailerUrlPlaceholder')} />
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
