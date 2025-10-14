import { ReactNode } from 'react'
import { usePermissions } from '@/contexts/PermissionContext'
import { Tooltip, Spin } from 'antd'
import { LockOutlined } from '@ant-design/icons'

interface PermissionGuardProps {
  /** 所需权限代码,支持单个或多个 */
  permission: string | string[]
  /** 子组件 */
  children: ReactNode
  /** 无权限时的替代内容 */
  fallback?: ReactNode
  /** 无权限时是否完全隐藏 */
  hideIfNoPermission?: boolean
  /** 无权限时是否显示提示 */
  showTooltip?: boolean
  /** 无权限时是否禁用(仅对按钮等交互元素有效) */
  disabled?: boolean
  /** 自定义无权限提示文本 */
  noPermissionText?: string
  /** 检查模式: 'any' 拥有任一权限即可, 'all' 必须拥有所有权限 */
  mode?: 'any' | 'all'
}

export const PermissionGuard = ({
  permission,
  children,
  fallback = null,
  hideIfNoPermission = false,
  showTooltip = true,
  disabled = false,
  noPermissionText = '您没有此操作的权限',
  mode = 'any',
}: PermissionGuardProps) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isLoading } = usePermissions()

  // 加载中显示骨架屏
  if (isLoading) {
    return <Spin size="small" />
  }

  // 计算是否有权限
  let hasAccess = false
  if (Array.isArray(permission)) {
    hasAccess = mode === 'any'
      ? hasAnyPermission(...permission)
      : hasAllPermissions(...permission)
  } else {
    hasAccess = hasPermission(permission)
  }

  // 有权限,正常渲染
  if (hasAccess) {
    return <>{children}</>
  }

  // 无权限,完全隐藏
  if (hideIfNoPermission) {
    return null
  }

  // 无权限,显示替代内容
  if (fallback) {
    return <>{fallback}</>
  }

  // 无权限,禁用并显示提示
  if (showTooltip) {
    return (
      <Tooltip title={noPermissionText}>
        <span
          style={{
            cursor: 'not-allowed',
            opacity: 0.5,
            display: 'inline-block',
          }}
        >
          {children}
        </span>
      </Tooltip>
    )
  }

  // 无权限,禁用但不显示提示
  return (
    <span
      style={{
        cursor: 'not-allowed',
        opacity: 0.5,
        display: 'inline-block',
      }}
    >
      {children}
    </span>
  )
}

/**
 * 权限保护的按钮组件
 * 无权限时自动显示锁图标
 */
interface PermissionButtonProps extends PermissionGuardProps {
  onClick?: () => void
  icon?: ReactNode
  type?: 'primary' | 'default' | 'dashed' | 'text' | 'link'
  danger?: boolean
  className?: string
}

export const PermissionButton = ({
  permission,
  children,
  onClick,
  icon,
  type = 'default',
  danger = false,
  className = '',
  ...guardProps
}: PermissionButtonProps) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions()

  const hasAccess = Array.isArray(permission)
    ? guardProps.mode === 'all'
      ? hasAllPermissions(...permission)
      : hasAnyPermission(...permission)
    : hasPermission(permission)

  if (!hasAccess) {
    return (
      <Tooltip title={guardProps.noPermissionText || '您没有此操作的权限'}>
        <button
          className={`ant-btn ant-btn-${type} ${danger ? 'ant-btn-danger' : ''} ${className}`}
          disabled
          style={{ cursor: 'not-allowed', opacity: 0.5 }}
        >
          <LockOutlined />
          {children}
        </button>
      </Tooltip>
    )
  }

  return (
    <button
      className={`ant-btn ant-btn-${type} ${danger ? 'ant-btn-danger' : ''} ${className}`}
      onClick={onClick}
    >
      {icon}
      {children}
    </button>
  )
}

/**
 * 用于条件渲染的Hook
 */
export const usePermissionCheck = (permission: string | string[], mode: 'any' | 'all' = 'any') => {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions()

  if (Array.isArray(permission)) {
    return mode === 'any' ? hasAnyPermission(...permission) : hasAllPermissions(...permission)
  }

  return hasPermission(permission)
}
