/**
 * 管理员个人资料服务
 */
import api from '../utils/axios'

export interface AdminProfile {
  id: number
  email: string
  username: string
  full_name: string | null
  avatar: string | null
  is_superadmin: boolean
  role_id: number | null
  created_at: string
  last_login_at: string | null
}

export interface UpdateProfileRequest {
  full_name?: string | null
  avatar?: string | null
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export interface ChangeEmailRequest {
  new_email: string
  password: string
}

const profileService = {
  // 获取当前管理员信息
  getProfile: async (): Promise<AdminProfile> => {
    const response = await api.get<AdminProfile>('/admin/profile/me')
    return response.data
  },

  // 更新个人资料
  updateProfile: async (data: UpdateProfileRequest): Promise<AdminProfile> => {
    const response = await api.put<AdminProfile>('/admin/profile/me', data)
    return response.data
  },

  // 修改密码
  changePassword: async (data: ChangePasswordRequest): Promise<{ message: string }> => {
    const response = await api.put<{ message: string }>('/admin/profile/me/password', data)
    return response.data
  },

  // 修改邮箱
  changeEmail: async (data: ChangeEmailRequest): Promise<AdminProfile> => {
    const response = await api.put<AdminProfile>('/admin/profile/me/email', data)
    return response.data
  },
}

export default profileService
