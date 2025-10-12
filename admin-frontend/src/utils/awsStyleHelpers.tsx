/**
 * AWS Cloudscape 风格组件工具函数
 * 提供统一的 AWS 风格 Tag、日期格式化等功能
 */

import { Tag } from 'antd'
import { CSSProperties, ReactNode } from 'react'
import dayjs from 'dayjs'

/**
 * AWS 风格的状态颜色配置
 */
export const AWS_STATUS_COLORS = {
  // 成功/激活/通过
  success: {
    bg: 'rgba(29, 129, 2, 0.1)',
    color: '#1d8102',
    border: '1px solid rgba(29, 129, 2, 0.2)',
  },
  // 警告/待审核/处理中
  warning: {
    bg: 'rgba(255, 153, 0, 0.1)',
    color: '#ff9900',
    border: '1px solid rgba(255, 153, 0, 0.2)',
  },
  // 错误/拒绝/禁用
  error: {
    bg: 'rgba(209, 50, 18, 0.1)',
    color: '#d13212',
    border: '1px solid rgba(209, 50, 18, 0.2)',
  },
  // 信息/普通
  info: {
    bg: 'rgba(0, 115, 187, 0.1)',
    color: '#0073bb',
    border: '1px solid rgba(0, 115, 187, 0.2)',
  },
  // 默认/灰色
  default: {
    bg: 'rgba(0, 0, 0, 0.04)',
    color: '#787774',
    border: '1px solid rgba(0, 0, 0, 0.1)',
  },
  // VIP/金色
  gold: {
    bg: 'rgba(255, 193, 7, 0.15)',
    color: '#d48806',
    border: '1px solid rgba(255, 193, 7, 0.3)',
  },
}

/**
 * AWS 风格的 Tag 组件
 * @param type 状态类型
 * @param children 内容
 * @param icon 图标
 */
export const AWSTag = ({
  type = 'default',
  children,
  icon,
  style,
}: {
  type?: keyof typeof AWS_STATUS_COLORS
  children: ReactNode
  icon?: ReactNode
  style?: CSSProperties
}) => {
  const colors = AWS_STATUS_COLORS[type]
  return (
    <Tag
      icon={icon}
      style={{
        backgroundColor: colors.bg,
        color: colors.color,
        border: colors.border,
        borderRadius: '4px',
        ...style,
      }}
    >
      {children}
    </Tag>
  )
}

/**
 * AWS 风格的等宽字体样式（用于数字、日期、代码）
 */
export const monospaceFontStyle: CSSProperties = {
  fontFamily: 'Monaco, Menlo, Consolas, monospace',
  color: '#37352f',
}

/**
 * 格式化日期为 AWS 风格（等宽字体）
 */
export const formatAWSDate = (
  date: string | Date,
  format: string = 'YYYY-MM-DD HH:mm'
) => {
  return (
    <span style={{ ...monospaceFontStyle, fontSize: '13px' }}>
      {dayjs(date).format(format)}
    </span>
  )
}

/**
 * 格式化数字为 AWS 风格（等宽字体）
 */
export const formatAWSNumber = (num: number | string) => {
  return <span style={monospaceFontStyle}>{num}</span>
}

/**
 * 视频状态 Tag 映射
 */
export const VideoStatusTag = ({ status }: { status: string }) => {
  const statusMap: Record<
    string,
    { type: keyof typeof AWS_STATUS_COLORS; text: string }
  > = {
    draft: { type: 'default', text: '草稿' },
    published: { type: 'success', text: '已发布' },
    archived: { type: 'warning', text: '已归档' },
  }
  const config = statusMap[status] || { type: 'default', text: status }
  return <AWSTag type={config.type}>{config.text}</AWSTag>
}

/**
 * 用户状态 Tag 映射
 */
export const UserStatusTag = ({ isActive }: { isActive: boolean }) => {
  return (
    <AWSTag type={isActive ? 'success' : 'error'}>
      {isActive ? '正常' : '已禁用'}
    </AWSTag>
  )
}

/**
 * 评论状态 Tag 映射
 */
export const CommentStatusTag = ({ status }: { status: string }) => {
  const statusMap: Record<
    string,
    { type: keyof typeof AWS_STATUS_COLORS; text: string }
  > = {
    PENDING: { type: 'warning', text: '待审核' },
    APPROVED: { type: 'success', text: '已通过' },
    REJECTED: { type: 'error', text: '已拒绝' },
  }
  const config = statusMap[status] || { type: 'default', text: status }
  return <AWSTag type={config.type}>{config.text}</AWSTag>
}

/**
 * AWS 风格的空状态文字颜色
 */
export const AWS_EMPTY_COLOR = '#787774'

/**
 * AWS 风格的卡片样式
 */
export const awsCardStyle: CSSProperties = {
  borderRadius: '8px',
  boxShadow: '0 0 0 1px rgba(0, 7, 22, 0.05), 0 1px 1px 0 rgba(0, 7, 22, 0.05)',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
}

/**
 * AWS 风格的按钮样式
 */
export const awsButtonStyle: CSSProperties = {
  borderRadius: '8px',
  fontWeight: 500,
}
