import React, { useState } from 'react'
import { Drawer, Form, Select, DatePicker, Button, Space, InputNumber, Radio } from 'antd'
import { FilterOutlined } from '@ant-design/icons'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

export interface FilterOptions {
  mediaType?: 'image' | 'video'
  sizeMin?: number  // bytes
  sizeMax?: number  // bytes
  dateRange?: [Dayjs, Dayjs]
}

interface FilterDrawerProps {
  visible: boolean
  onClose: () => void
  onApply: (filters: FilterOptions) => void
  currentFilters: FilterOptions
}

/**
 * 高级筛选抽屉组件
 */
const FilterDrawer: React.FC<FilterDrawerProps> = ({
  visible,
  onClose,
  onApply,
  currentFilters,
}) => {
  const [form] = Form.useForm()
  const [sizeUnit, setSizeUnit] = useState<'KB' | 'MB' | 'GB'>('MB')

  // 文件大小预设选项
  const sizePresets = [
    { label: '小于 1MB', value: [0, 1024 * 1024] },
    { label: '1MB - 10MB', value: [1024 * 1024, 10 * 1024 * 1024] },
    { label: '10MB - 100MB', value: [10 * 1024 * 1024, 100 * 1024 * 1024] },
    { label: '100MB - 1GB', value: [100 * 1024 * 1024, 1024 * 1024 * 1024] },
    { label: '大于 1GB', value: [1024 * 1024 * 1024, Infinity] },
  ]

  // 日期预设选项
  const datePresets = [
    { label: '今天', value: [dayjs().startOf('day'), dayjs().endOf('day')] as [Dayjs, Dayjs] },
    { label: '最近 7 天', value: [dayjs().subtract(7, 'day'), dayjs()] as [Dayjs, Dayjs] },
    { label: '最近 30 天', value: [dayjs().subtract(30, 'day'), dayjs()] as [Dayjs, Dayjs] },
    { label: '最近 3 个月', value: [dayjs().subtract(3, 'month'), dayjs()] as [Dayjs, Dayjs] },
  ]

  // 单位转换
  const convertToBytes = (value: number, unit: 'KB' | 'MB' | 'GB'): number => {
    const units = { KB: 1024, MB: 1024 * 1024, GB: 1024 * 1024 * 1024 }
    return value * units[unit]
  }

  const convertFromBytes = (bytes: number, unit: 'KB' | 'MB' | 'GB'): number => {
    const units = { KB: 1024, MB: 1024 * 1024, GB: 1024 * 1024 * 1024 }
    return bytes / units[unit]
  }

  // 应用筛选
  const handleApply = () => {
    const values = form.getFieldsValue()
    const filters: FilterOptions = {}

    if (values.mediaType) {
      filters.mediaType = values.mediaType
    }

    if (values.sizeMin !== undefined && values.sizeMin !== null) {
      filters.sizeMin = convertToBytes(values.sizeMin, sizeUnit)
    }

    if (values.sizeMax !== undefined && values.sizeMax !== null) {
      filters.sizeMax = convertToBytes(values.sizeMax, sizeUnit)
    }

    if (values.dateRange && values.dateRange.length === 2) {
      filters.dateRange = values.dateRange
    }

    onApply(filters)
    onClose()
  }

  // 重置筛选
  const handleReset = () => {
    form.resetFields()
    onApply({})
    onClose()
  }

  // 应用预设大小
  const handleSizePreset = (value: number[]) => {
    if (value.length === 2) {
      const [min, max] = value
      form.setFieldsValue({
        sizeMin: min !== undefined ? convertFromBytes(min, sizeUnit) : undefined,
        sizeMax: max === Infinity || max === undefined ? undefined : convertFromBytes(max, sizeUnit),
      })
    }
  }

  // 应用预设日期
  const handleDatePreset = (value: [Dayjs, Dayjs]) => {
    form.setFieldsValue({
      dateRange: value,
    })
  }

  return (
    <Drawer
      title={
        <span>
          <FilterOutlined style={{ marginRight: 8 }} />
          高级筛选
        </span>
      }
      placement="right"
      onClose={onClose}
      open={visible}
      width={400}
      footer={
        <Space style={{ float: 'right' }}>
          <Button onClick={handleReset}>重置</Button>
          <Button type="primary" onClick={handleApply}>
            应用筛选
          </Button>
        </Space>
      }
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          mediaType: currentFilters.mediaType,
          sizeMin: currentFilters.sizeMin ? convertFromBytes(currentFilters.sizeMin, sizeUnit) : undefined,
          sizeMax: currentFilters.sizeMax ? convertFromBytes(currentFilters.sizeMax, sizeUnit) : undefined,
          dateRange: currentFilters.dateRange,
        }}
      >
        <Form.Item label="文件类型" name="mediaType">
          <Select placeholder="选择文件类型" allowClear>
            <Select.Option value="image">图片</Select.Option>
            <Select.Option value="video">视频</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item label="文件大小">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Radio.Group value={sizeUnit} onChange={(e) => setSizeUnit(e.target.value)}>
              <Radio.Button value="KB">KB</Radio.Button>
              <Radio.Button value="MB">MB</Radio.Button>
              <Radio.Button value="GB">GB</Radio.Button>
            </Radio.Group>

            <Space.Compact style={{ width: '100%' }}>
              <Form.Item name="sizeMin" noStyle>
                <InputNumber
                  placeholder="最小"
                  min={0}
                  style={{ width: '50%' }}
                />
              </Form.Item>
              <Form.Item name="sizeMax" noStyle>
                <InputNumber
                  placeholder="最大"
                  min={0}
                  style={{ width: '50%' }}
                />
              </Form.Item>
            </Space.Compact>

            <div style={{ marginTop: 8 }}>
              <div style={{ marginBottom: 8, fontSize: 12, color: '#8c8c8c' }}>快速选择:</div>
              <Space wrap>
                {sizePresets.map((preset) => (
                  <Button
                    key={preset.label}
                    size="small"
                    onClick={() => handleSizePreset(preset.value)}
                  >
                    {preset.label}
                  </Button>
                ))}
              </Space>
            </div>
          </Space>
        </Form.Item>

        <Form.Item label="上传时间" name="dateRange">
          <RangePicker
            style={{ width: '100%' }}
            showTime
            format="YYYY-MM-DD HH:mm"
          />
        </Form.Item>

        <div style={{ marginTop: -16, marginBottom: 16 }}>
          <div style={{ marginBottom: 8, fontSize: 12, color: '#8c8c8c' }}>快速选择:</div>
          <Space wrap>
            {datePresets.map((preset) => (
              <Button
                key={preset.label}
                size="small"
                onClick={() => handleDatePreset(preset.value)}
              >
                {preset.label}
              </Button>
            ))}
          </Space>
        </div>
      </Form>
    </Drawer>
  )
}

export default FilterDrawer
