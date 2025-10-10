import api from './api'

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar?: string
  is_active: boolean
  is_verified: boolean
  is_vip: boolean
  vip_expires_at?: string
  created_at: string
  last_login_at?: string
}

export interface UserUpdate {
  full_name?: string
  avatar?: string
}

export interface PasswordChange {
  old_password: string
  new_password: string
}

export const userService = {
  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me')
    return response.data
  },

  // Update user profile
  updateProfile: async (data: UserUpdate): Promise<User> => {
    const response = await api.put('/users/me', data)
    return response.data
  },

  // Change password
  changePassword: async (data: PasswordChange): Promise<{ message: string }> => {
    const response = await api.post('/users/me/change-password', data)
    return response.data
  },
}
