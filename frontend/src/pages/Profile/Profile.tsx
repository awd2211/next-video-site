import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userService, User, UserUpdate, PasswordChange } from '@/services/userService'
import { historyService } from '@/services/historyService'
import { favoriteService } from '@/services/favoriteService'

const Profile = () => {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'stats'>('profile')
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<UserUpdate>({})
  const [passwordData, setPasswordData] = useState<PasswordChange>({
    old_password: '',
    new_password: '',
  })

  // Fetch user data
  const { data: user, isLoading } = useQuery({
    queryKey: ['current-user'],
    queryFn: userService.getCurrentUser,
  })

  // Fetch statistics
  const { data: historyData } = useQuery({
    queryKey: ['user-history-stats'],
    queryFn: () => historyService.getUserHistory(1, 1), // Just to get total count
    enabled: activeTab === 'stats',
  })

  const { data: favoritesData } = useQuery({
    queryKey: ['user-favorites-stats'],
    queryFn: () => favoriteService.getUserFavorites(1, 1), // Just to get total count
    enabled: activeTab === 'stats',
  })

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: userService.updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['current-user'] })
      setIsEditing(false)
      alert('个人信息更新成功！')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '更新失败')
    },
  })

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: userService.changePassword,
    onSuccess: () => {
      setPasswordData({ old_password: '', new_password: '' })
      alert('密码修改成功！')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '密码修改失败')
    },
  })

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault()
    updateProfileMutation.mutate(formData)
  }

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordData.new_password.length < 6) {
      alert('新密码长度不能少于6位')
      return
    }
    changePasswordMutation.mutate(passwordData)
  }

  const startEditing = () => {
    setIsEditing(true)
    setFormData({
      full_name: user?.full_name,
      avatar: user?.avatar,
    })
  }

  if (isLoading) {
    return <div className="text-center py-12">加载中...</div>
  }

  if (!user) {
    return <div className="text-center py-12">请先登录</div>
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">个人中心</h1>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'profile'
              ? 'text-blue-500 border-b-2 border-blue-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          个人信息
        </button>
        <button
          onClick={() => setActiveTab('password')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'password'
              ? 'text-blue-500 border-b-2 border-blue-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          修改密码
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'stats'
              ? 'text-blue-500 border-b-2 border-blue-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          观看统计
        </button>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-gray-800 rounded-lg p-6">
          {!isEditing ? (
            <div className="space-y-4">
              {/* Avatar */}
              <div className="flex items-center gap-4 mb-6">
                <div className="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center overflow-hidden">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.username} className="w-full h-full object-cover" />
                  ) : (
                    <svg className="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{user.username}</h2>
                  <p className="text-gray-400">{user.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">用户名</label>
                  <p className="text-lg">{user.username}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">邮箱</label>
                  <p className="text-lg">{user.email}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">姓名</label>
                  <p className="text-lg">{user.full_name || '未设置'}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">账号状态</label>
                  <p className="text-lg">
                    {user.is_active ? (
                      <span className="text-green-500">活跃</span>
                    ) : (
                      <span className="text-red-500">已禁用</span>
                    )}
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">VIP状态</label>
                  <p className="text-lg">
                    {user.is_vip ? (
                      <span className="text-yellow-500">VIP会员</span>
                    ) : (
                      <span className="text-gray-400">普通用户</span>
                    )}
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">注册时间</label>
                  <p className="text-lg">{new Date(user.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              <button
                onClick={startEditing}
                className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
              >
                编辑资料
              </button>
            </div>
          ) : (
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">姓名</label>
                <input
                  type="text"
                  value={formData.full_name || ''}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入您的姓名"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">头像URL</label>
                <input
                  type="url"
                  value={formData.avatar || ''}
                  onChange={(e) => setFormData({ ...formData, avatar: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入头像图片链接"
                />
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  type="submit"
                  disabled={updateProfileMutation.isPending}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {updateProfileMutation.isPending ? '保存中...' : '保存'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  取消
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="bg-gray-800 rounded-lg p-6">
          <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium mb-2">当前密码</label>
              <input
                type="password"
                value={passwordData.old_password}
                onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入当前密码"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">新密码</label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入新密码（至少6位）"
                required
                minLength={6}
              />
            </div>

            <button
              type="submit"
              disabled={changePasswordMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {changePasswordMutation.isPending ? '修改中...' : '修改密码'}
            </button>
          </form>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-6">观看统计</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-700 rounded-lg p-6 text-center">
              <div className="text-4xl font-bold text-blue-500 mb-2">{historyData?.total || 0}</div>
              <div className="text-gray-400">观看历史</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-6 text-center">
              <div className="text-4xl font-bold text-red-500 mb-2">{favoritesData?.total || 0}</div>
              <div className="text-gray-400">收藏视频</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-6 text-center">
              <div className="text-4xl font-bold text-green-500 mb-2">
                {new Date(user.created_at).toLocaleDateString()}
              </div>
              <div className="text-gray-400">注册时间</div>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href="/history"
              className="block bg-gray-700 hover:bg-gray-600 rounded-lg p-4 transition-colors"
            >
              <h3 className="font-semibold mb-2">观看历史</h3>
              <p className="text-sm text-gray-400">查看所有观看记录</p>
            </a>
            <a
              href="/favorites"
              className="block bg-gray-700 hover:bg-gray-600 rounded-lg p-4 transition-colors"
            >
              <h3 className="font-semibold mb-2">我的收藏</h3>
              <p className="text-sm text-gray-400">查看所有收藏的视频</p>
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

export default Profile
