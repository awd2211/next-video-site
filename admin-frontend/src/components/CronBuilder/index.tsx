/**
 * Cron Expression Builder Component
 * Provides a user-friendly interface for creating and editing cron expressions
 */

import { Alert, Button, Card, Col, Divider, Input, Row, Select, Space, Tabs, Tag, Typography } from 'antd'
import {  CheckCircleOutlined, CloseCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons'
import React, { useEffect, useState } from 'react'
import { schedulingService } from '@/services/scheduling'
import { useQuery } from '@tanstack/react-query'

const { Title, Text, Paragraph } = Typography
const { Option } = Select
const { TabPane } = Tabs

interface CronBuilderProps {
  value?: string
  onChange?: (value: string) => void
  onValidate?: (valid: boolean, description: string) => void
}

interface CronPattern {
  name: string
  expression: string
  description: string
  category: string
  next_run?: string
}

interface CronValidation {
  valid: boolean
  error_message?: string
  description: string
  next_occurrences: string[]
}

const CronBuilder: React.FC<CronBuilderProps> = ({ value = '0 9 * * *', onChange, onValidate }) => {
  const [activeTab, setActiveTab] = useState<string>('simple')
  const [expression, setExpression] = useState<string>(value)
  const [validation, setValidation] = useState<CronValidation | null>(null)
  const [isValidating, setIsValidating] = useState(false)

  // Simple mode state
  const [simpleMinute, setSimpleMinute] = useState('0')
  const [simpleHour, setSimpleHour] = useState('9')
  const [simpleDay, setSimpleDay] = useState('*')
  const [simpleMonth, setSimpleMonth] = useState('*')
  const [simpleWeekday, setSimpleWeekday] = useState('*')

  // Fetch predefined patterns
  const { data: patternsData, isLoading: patternsLoading } = useQuery({
    queryKey: ['cron-patterns'],
    queryFn: schedulingService.getCronPatterns,
  })

  // Parse existing expression into simple mode
  useEffect(() => {
    if (value) {
      const parts = value.split(' ')
      if (parts.length === 5) {
        setSimpleMinute(parts[0])
        setSimpleHour(parts[1])
        setSimpleDay(parts[2])
        setSimpleMonth(parts[3])
        setSimpleWeekday(parts[4])
        setExpression(value)
      }
    }
  }, [value])

  // Validate expression
  const validateExpression = async (expr: string) => {
    if (!expr || expr.trim().length === 0) {
      setValidation(null)
      return
    }

    setIsValidating(true)
    try {
      const result = await schedulingService.validateCron(expr)
      setValidation(result)
      if (onValidate) {
        onValidate(result.valid, result.description)
      }
    } catch (error) {
      console.error('Validation error:', error)
      setValidation({
        valid: false,
        error_message: 'Failed to validate expression',
        description: '',
        next_occurrences: [],
      })
    } finally {
      setIsValidating(false)
    }
  }

  // Update expression from simple mode
  const updateFromSimple = () => {
    const newExpr = `${simpleMinute} ${simpleHour} ${simpleDay} ${simpleMonth} ${simpleWeekday}`
    setExpression(newExpr)
    if (onChange) {
      onChange(newExpr)
    }
    validateExpression(newExpr)
  }

  useEffect(() => {
    if (activeTab === 'simple') {
      updateFromSimple()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [simpleMinute, simpleHour, simpleDay, simpleMonth, simpleWeekday])

  // Handle manual expression change
  const handleExpressionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newExpr = e.target.value
    setExpression(newExpr)
    if (onChange) {
      onChange(newExpr)
    }
    validateExpression(newExpr)
  }

  // Handle pattern selection
  const handlePatternSelect = (pattern: CronPattern) => {
    setExpression(pattern.expression)
    if (onChange) {
      onChange(pattern.expression)
    }
    validateExpression(pattern.expression)
  }

  // Group patterns by category
  const groupedPatterns = React.useMemo(() => {
    if (!patternsData?.patterns) return {}

    return patternsData.patterns.reduce((acc, pattern) => {
      if (!acc[pattern.category]) {
        acc[pattern.category] = []
      }
      acc[pattern.category].push(pattern)
      return acc
    }, {} as Record<string, CronPattern[]>)
  }, [patternsData])

  // Minute options
  const minuteOptions = [
    { value: '*', label: 'Every minute' },
    { value: '0', label: ':00' },
    { value: '15', label: ':15' },
    { value: '30', label: ':30' },
    { value: '45', label: ':45' },
    { value: '*/5', label: 'Every 5 minutes' },
    { value: '*/10', label: 'Every 10 minutes' },
    { value: '*/15', label: 'Every 15 minutes' },
    { value: '*/30', label: 'Every 30 minutes' },
  ]

  // Hour options
  const hourOptions = Array.from({ length: 24 }, (_, i) => ({
    value: i.toString(),
    label: `${i.toString().padStart(2, '0')}:00`,
  }))

  hourOptions.unshift(
    { value: '*', label: 'Every hour' },
    { value: '*/2', label: 'Every 2 hours' },
    { value: '*/6', label: 'Every 6 hours' },
    { value: '*/12', label: 'Every 12 hours' }
  )

  // Day options
  const dayOptions = [
    { value: '*', label: 'Every day' },
    ...Array.from({ length: 31 }, (_, i) => ({
      value: (i + 1).toString(),
      label: `Day ${i + 1}`,
    })),
    { value: '1-15', label: 'Days 1-15' },
    { value: '16-31', label: 'Days 16-31' },
  ]

  // Month options
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const monthOptions = [
    { value: '*', label: 'Every month' },
    ...monthNames.map((name, i) => ({
      value: (i + 1).toString(),
      label: name,
    })),
  ]

  // Weekday options
  const weekdayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

  const weekdayOptions = [
    { value: '*', label: 'Every day' },
    ...weekdayNames.map((name, i) => ({
      value: i.toString(),
      label: name,
    })),
    { value: '1-5', label: 'Weekdays (Mon-Fri)' },
    { value: '0,6', label: 'Weekends (Sat-Sun)' },
  ]

  return (
    <Card>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* Tabs for different input modes */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* Predefined Patterns */}
          <TabPane tab="Templates" key="templates">
            {patternsLoading ? (
              <Text>Loading patterns...</Text>
            ) : (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {Object.entries(groupedPatterns).map(([category, patterns]) => (
                  <div key={category}>
                    <Title level={5} style={{ textTransform: 'capitalize' }}>
                      {category.replace('_', ' ')}
                    </Title>
                    <Row gutter={[8, 8]}>
                      {patterns.map((pattern) => (
                        <Col key={pattern.name} span={12}>
                          <Card
                            size="small"
                            hoverable
                            onClick={() => handlePatternSelect(pattern)}
                            style={{
                              borderColor:
                                expression === pattern.expression ? '#1890ff' : undefined,
                            }}
                          >
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              <Text strong>{pattern.description}</Text>
                              <Text code style={{ fontSize: '12px' }}>
                                {pattern.expression}
                              </Text>
                            </Space>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </div>
                ))}
              </Space>
            )}
          </TabPane>

          {/* Simple Builder */}
          <TabPane tab="Simple Builder" key="simple">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Row gutter={16}>
                <Col span={8}>
                  <Text strong>Minute</Text>
                  <Select
                    value={simpleMinute}
                    onChange={setSimpleMinute}
                    style={{ width: '100%', marginTop: 8 }}
                    showSearch
                  >
                    {minuteOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Col>

                <Col span={8}>
                  <Text strong>Hour</Text>
                  <Select
                    value={simpleHour}
                    onChange={setSimpleHour}
                    style={{ width: '100%', marginTop: 8 }}
                    showSearch
                  >
                    {hourOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Col>

                <Col span={8}>
                  <Text strong>Day of Month</Text>
                  <Select
                    value={simpleDay}
                    onChange={setSimpleDay}
                    style={{ width: '100%', marginTop: 8 }}
                    showSearch
                  >
                    {dayOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Text strong>Month</Text>
                  <Select
                    value={simpleMonth}
                    onChange={setSimpleMonth}
                    style={{ width: '100%', marginTop: 8 }}
                    showSearch
                  >
                    {monthOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Col>

                <Col span={12}>
                  <Text strong>Day of Week</Text>
                  <Select
                    value={simpleWeekday}
                    onChange={setSimpleWeekday}
                    style={{ width: '100%', marginTop: 8 }}
                    showSearch
                  >
                    {weekdayOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Col>
              </Row>
            </Space>
          </TabPane>

          {/* Advanced Manual Entry */}
          <TabPane tab="Advanced" key="advanced">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Text strong>Cron Expression</Text>
                <Input
                  value={expression}
                  onChange={handleExpressionChange}
                  placeholder="0 9 * * *"
                  style={{ marginTop: 8 }}
                  suffix={<QuestionCircleOutlined />}
                />
              </div>

              <Alert
                message="Cron Format: minute hour day month weekday"
                description={
                  <div>
                    <Paragraph style={{ marginBottom: 8 }}>
                      <Text code>*</Text> - Every value
                      <br />
                      <Text code>*/n</Text> - Every n values
                      <br />
                      <Text code>a-b</Text> - Range from a to b
                      <br />
                      <Text code>a,b,c</Text> - Specific values
                    </Paragraph>
                    <Paragraph style={{ marginBottom: 0 }}>
                      <Text strong>Examples:</Text>
                      <br />
                      <Text code>0 9 * * *</Text> - Daily at 9:00 AM
                      <br />
                      <Text code>*/15 * * * *</Text> - Every 15 minutes
                      <br />
                      <Text code>0 9 * * 1-5</Text> - Weekdays at 9:00 AM
                    </Paragraph>
                  </div>
                }
                type="info"
                showIcon
              />
            </Space>
          </TabPane>
        </Tabs>

        <Divider />

        {/* Current Expression Display */}
        <div>
          <Text strong>Current Expression: </Text>
          <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
            {expression}
          </Tag>
        </div>

        {/* Validation Result */}
        {validation && (
          <Alert
            message={
              <Space>
                {validation.valid ? (
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                ) : (
                  <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                )}
                <Text strong>{validation.valid ? 'Valid Expression' : 'Invalid Expression'}</Text>
              </Space>
            }
            description={
              <Space direction="vertical" style={{ width: '100%' }}>
                {validation.valid ? (
                  <>
                    <Text>{validation.description}</Text>
                    {validation.next_occurrences && validation.next_occurrences.length > 0 && (
                      <>
                        <Text strong style={{ marginTop: 8 }}>
                          Next 5 executions:
                        </Text>
                        {validation.next_occurrences.map((time, index) => (
                          <Text key={index} type="secondary">
                            {index + 1}. {new Date(time).toLocaleString()}
                          </Text>
                        ))}
                      </>
                    )}
                  </>
                ) : (
                  <Text type="danger">{validation.error_message}</Text>
                )}
              </Space>
            }
            type={validation.valid ? 'success' : 'error'}
            showIcon
          />
        )}

        {/* Validate Button */}
        <Button
          type="primary"
          loading={isValidating}
          onClick={() => validateExpression(expression)}
          block
        >
          Validate Expression
        </Button>
      </Space>
    </Card>
  )
}

export default CronBuilder
