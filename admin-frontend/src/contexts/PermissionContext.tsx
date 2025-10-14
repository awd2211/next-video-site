import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axios from '@/utils/axios'
import { message } from 'antd'

interface PermissionContextType {
  permissions: string[]
  isSuperadmin: boolean
  role: string | null
  hasPermission: (code: string) => boolean
  hasAnyPermission: (...codes: string[]) => boolean
  hasAllPermissions: (...codes: string[]) => boolean
  isLoading: boolean
  reload: () => Promise<void>
}

const PermissionContext = createContext<PermissionContextType | null>(null)

interface PermissionProviderProps {
  children: ReactNode
}

export const PermissionProvider = ({ children }: PermissionProviderProps) => {
  const [permissions, setPermissions] = useState<string[]>([])
  const [isSuperadmin, setIsSuperadmin] = useState(false)
  const [role, setRole] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadPermissions = async () => {
    try {
      setIsLoading(true)
      const res = await axios.get('/api/v1/admin/rbac/my-permissions')
      setPermissions(res.data.permissions || [])
      setIsSuperadmin(res.data.is_superadmin || false)
      setRole(res.data.role || null)
    } catch (error: any) {
      console.error('Failed to load permissions:', error)
      // 不显示错误消息,静默失败
      setPermissions([])
      setIsSuperadmin(false)
      setRole(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    // 检查是否已登录
    const token = localStorage.getItem('admin_access_token')
    if (token) {
      loadPermissions()
    } else {
      setIsLoading(false)
    }
  }, [])

  const hasPermission = (code: string): boolean => {
    // 超级管理员拥有所有权限
    if (isSuperadmin) return true

    // 通配符权限
    if (permissions.includes('*')) return true

    // 精确匹配
    if (permissions.includes(code)) return true

    // 模块级通配符 (如 video.* 匹配 video.create)
    const module = code.split('.')[0]
    if (permissions.includes(`${module}.*`)) return true

    return false
  }

  const hasAnyPermission = (...codes: string[]): boolean => {
    if (isSuperadmin) return true
    return codes.some(code => hasPermission(code))
  }

  const hasAllPermissions = (...codes: string[]): boolean => {
    if (isSuperadmin) return true
    return codes.every(code => hasPermission(code))
  }

  const reload = async () => {
    await loadPermissions()
  }

  const value: PermissionContextType = {
    permissions,
    isSuperadmin,
    role,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isLoading,
    reload,
  }

  return <PermissionContext.Provider value={value}>{children}</PermissionContext.Provider>
}

export const usePermissions = () => {
  const context = useContext(PermissionContext)
  if (!context) {
    throw new Error('usePermissions must be used within PermissionProvider')
  }
  return context
}

// 导出类型供其他模块使用
export type { PermissionContextType }
