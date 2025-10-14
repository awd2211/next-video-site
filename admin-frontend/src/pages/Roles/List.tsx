import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Card,
  Tag,
  Descriptions,
  Tabs,
  Tooltip,
  Empty,
  Spin,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SafetyOutlined,
  UserOutlined,
  KeyOutlined,
  SearchOutlined,
  FilterOutlined,
} from '@ant-design/icons'
import { useState, useMemo } from 'react'
import axios from '@/utils/axios'
import { useTranslation } from 'react-i18next'

const RolesList = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [isRoleModalVisible, setIsRoleModalVisible] = useState(false)
  const [isAdminModalVisible, setIsAdminModalVisible] = useState(false)
  const [editingRole, setEditingRole] = useState<any>(null)
  const [selectedAdmin, setSelectedAdmin] = useState<any>(null)
  const [roleForm] = Form.useForm()
  const [adminRoleForm] = Form.useForm()
  const [activeTab, setActiveTab] = useState('roles')

  // 搜索和过滤状态
  const [roleSearchText, setRoleSearchText] = useState('')
  const [permissionModuleFilter, setPermissionModuleFilter] = useState<string>('all')
  const [adminSearchText, setAdminSearchText] = useState('')

  // 获取角色列表
  const { data: rolesData, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/admin/rbac/roles')
      return res.data
    },
  })

  // 获取权限列表
  const { data: permissionsData, isLoading: permissionsLoading } = useQuery({
    queryKey: ['permissions'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/admin/rbac/permissions')
      return res.data
    },
  })

  // 获取管理员列表
  const { data: adminUsersData, isLoading: adminUsersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/admin/rbac/admin-users')
      return res.data
    },
  })

  // 过滤后的角色列表
  const filteredRoles = useMemo(() => {
    if (!rolesData?.roles) return []
    if (!roleSearchText) return rolesData.roles

    return rolesData.roles.filter((role: any) =>
      role.name.toLowerCase().includes(roleSearchText.toLowerCase()) ||
      role.description?.toLowerCase().includes(roleSearchText.toLowerCase())
    )
  }, [rolesData, roleSearchText])

  // 过滤后的权限列表
  const filteredPermissions = useMemo(() => {
    if (!permissionsData?.grouped) return {}
    if (permissionModuleFilter === 'all') return permissionsData.grouped

    return {
      [permissionModuleFilter]: permissionsData.grouped[permissionModuleFilter]
    }
  }, [permissionsData, permissionModuleFilter])

  // 过滤后的管理员列表
  const filteredAdmins = useMemo(() => {
    if (!adminUsersData?.admin_users) return []
    if (!adminSearchText) return adminUsersData.admin_users

    return adminUsersData.admin_users.filter((admin: any) =>
      admin.username.toLowerCase().includes(adminSearchText.toLowerCase()) ||
      admin.email.toLowerCase().includes(adminSearchText.toLowerCase()) ||
      admin.full_name?.toLowerCase().includes(adminSearchText.toLowerCase())
    )
  }, [adminUsersData, adminSearchText])

  // 创建/更新角色
  const saveRoleMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingRole) {
        return axios.put(`/api/v1/admin/rbac/roles/${editingRole.id}`, values)
      }
      return axios.post('/api/v1/admin/rbac/roles', values)
    },
    onSuccess: () => {
      message.success(t(editingRole ? 'roles.roleUpdated' : 'roles.roleCreated'))
      setIsRoleModalVisible(false)
      setEditingRole(null)
      roleForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('roles.operationFailed'))
    },
  })

  // 删除角色
  const deleteRoleMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/v1/admin/rbac/roles/${id}`),
    onSuccess: () => {
      message.success(t('roles.roleDeleted'))
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('roles.deleteFailed'))
    },
  })

  // 分配角色给管理员
  const assignRolesMutation = useMutation({
    mutationFn: async ({ adminId, roleId }: { adminId: number; roleId: number | null }) => {
      return axios.post(`/api/v1/admin/rbac/admin-users/${adminId}/role`, { role_id: roleId })
    },
    onSuccess: () => {
      message.success(t('roles.roleAssignSuccess'))
      setIsAdminModalVisible(false)
      setSelectedAdmin(null)
      adminRoleForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('roles.roleAssignFailed'))
    },
  })

  const handleEditRole = (role: any) => {
    setEditingRole(role)
    roleForm.setFieldsValue({
      name: role.name,
      description: role.description,
      permission_ids: role.permissions?.map((p: any) => p.id) || [],
    })
    setIsRoleModalVisible(true)
  }

  const handleDeleteRole = (role: any) => {
    Modal.confirm({
      title: t('roles.confirmDeleteRole'),
      content: t('roles.deleteRoleWarning', { name: role.name }),
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      okType: 'danger',
      onOk: () => deleteRoleMutation.mutate(role.id),
    })
  }

  const handleAssignRoles = (admin: any) => {
    if (admin.is_superadmin) {
      message.info(t('roles.superadminNoAssign'))
      return
    }

    setSelectedAdmin(admin)
    adminRoleForm.setFieldsValue({
      role_id: admin.role?.id || null,
    })
    setIsAdminModalVisible(true)
  }

  // 角色表格列
  const roleColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('roles.roleName'),
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <Space>
          <SafetyOutlined style={{ color: record.is_active ? '#1890ff' : '#999' }} />
          <span>{name}</span>
          {!record.is_active && <Tag color="default">{t('roles.inactive')}</Tag>}
        </Space>
      ),
    },
    {
      title: t('roles.roleDescription'),
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: t('common.permissions'),
      key: 'permissions',
      width: 120,
      render: (_: any, record: any) => (
        <Tag color="blue">{t('roles.permissionCount', { count: record.permission_count || 0 })}</Tag>
      ),
    },
    {
      title: t('common.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 200,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEditRole(record)}
          >
            {t('common.edit')}
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteRole(record)}
          >
            {t('common.delete')}
          </Button>
        </Space>
      ),
    },
  ]

  // 管理员表格列
  const adminColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('user.username'),
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: any) => (
        <Space>
          <UserOutlined />
          <span>{username}</span>
          {record.is_superadmin && <Tag color="gold">{t('roles.superadmin')}</Tag>}
          {!record.is_active && <Tag color="red">{t('common.inactive')}</Tag>}
        </Space>
      ),
    },
    {
      title: t('user.email'),
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: t('user.fullName'),
      dataIndex: 'full_name',
      key: 'full_name',
    },
    {
      title: t('roles.currentRole'),
      key: 'role',
      render: (_: any, record: any) => (
        <Space wrap>
          {record.is_superadmin ? (
            <Tag color="gold">{t('roles.allPermissions')}</Tag>
          ) : record.role ? (
            <Tag color="blue">{record.role.name}</Tag>
          ) : (
            <Tag color="default">{t('roles.noRole')}</Tag>
          )}
        </Space>
      ),
    },
    {
      title: t('roles.lastLogin'),
      dataIndex: 'last_login',
      key: 'last_login',
      width: 180,
      render: (date: string) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Button
          type="link"
          icon={<KeyOutlined />}
          onClick={() => handleAssignRoles(record)}
          disabled={record.is_superadmin}
        >
          {t('roles.assignRole')}
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'roles',
            label: (
              <span>
                <SafetyOutlined />
                {t('roles.rolesManagement')}
              </span>
            ),
            children: (
              <Card
                title={t('roles.roleList')}
                extra={
                  <Space>
                    <Input
                      placeholder={t('roles.searchRole')}
                      prefix={<SearchOutlined />}
                      value={roleSearchText}
                      onChange={(e) => setRoleSearchText(e.target.value)}
                      style={{ width: 200 }}
                      allowClear
                    />
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => {
                        setEditingRole(null)
                        roleForm.resetFields()
                        setIsRoleModalVisible(true)
                      }}
                    >
                      {t('roles.createRole')}
                    </Button>
                  </Space>
                }
              >
                <Table
                  columns={roleColumns}
                  dataSource={filteredRoles}
                  loading={rolesLoading}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                  locale={{
                    emptyText: (
                      <Empty
                        description={t('common.noData')}
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                      />
                    ),
                  }}
                />
              </Card>
            ),
          },
          {
            key: 'permissions',
            label: (
              <span>
                <KeyOutlined />
                {t('roles.permissionsList')}
              </span>
            ),
            children: (
              <Card
                title={t('roles.systemPermissions')}
                extra={
                  <Space>
                    <Select
                      value={permissionModuleFilter}
                      onChange={setPermissionModuleFilter}
                      style={{ width: 200 }}
                      placeholder={t('roles.filterByModule')}
                    >
                      <Select.Option value="all">{t('roles.allModules')}</Select.Option>
                      {permissionsData?.grouped &&
                        Object.keys(permissionsData.grouped).map((module) => (
                          <Select.Option key={module} value={module}>
                            {module}
                          </Select.Option>
                        ))}
                    </Select>
                  </Space>
                }
              >
                {permissionsLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Spin tip={t('roles.loading')} />
                  </div>
                ) : (
                  <Space direction="vertical" style={{ width: '100%' }} size="large">
                    {Object.entries(filteredPermissions).map(([module, perms]: [string, any]) => (
                      <Card
                        key={module}
                        type="inner"
                        title={`${t('roles.modulePrefix')} ${module}`}
                        size="small"
                        extra={<Tag color="cyan">{perms.length} {t('common.items')}</Tag>}
                      >
                        <Space wrap>
                          {perms.map((perm: any) => (
                            <Tooltip
                              key={perm.id}
                              title={perm.description || perm.code}
                              placement="top"
                            >
                              <Tag color="blue">
                                {perm.name} ({perm.code})
                              </Tag>
                            </Tooltip>
                          ))}
                        </Space>
                      </Card>
                    ))}
                  </Space>
                )}
              </Card>
            ),
          },
          {
            key: 'admins',
            label: (
              <span>
                <UserOutlined />
                {t('roles.adminUsers')}
              </span>
            ),
            children: (
              <Card
                title={t('roles.adminList')}
                extra={
                  <Input
                    placeholder={t('roles.searchAdmin')}
                    prefix={<SearchOutlined />}
                    value={adminSearchText}
                    onChange={(e) => setAdminSearchText(e.target.value)}
                    style={{ width: 250 }}
                    allowClear
                  />
                }
              >
                <Table
                  columns={adminColumns}
                  dataSource={filteredAdmins}
                  loading={adminUsersLoading}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                  locale={{
                    emptyText: (
                      <Empty
                        description={t('common.noData')}
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                      />
                    ),
                  }}
                />
              </Card>
            ),
          },
        ]}
      />

      {/* 角色编辑 Modal */}
      <Modal
        title={editingRole ? t('roles.editRole') : t('roles.createRole')}
        open={isRoleModalVisible}
        onCancel={() => {
          setIsRoleModalVisible(false)
          setEditingRole(null)
          roleForm.resetFields()
        }}
        onOk={() => roleForm.submit()}
        confirmLoading={saveRoleMutation.isPending}
        width={700}
        okText={t('common.save')}
        cancelText={t('common.cancel')}
      >
        <Form
          form={roleForm}
          layout="vertical"
          onFinish={(values) => saveRoleMutation.mutate(values)}
        >
          <Form.Item
            name="name"
            label={t('roles.roleName')}
            rules={[{ required: true, message: t('form.required') }]}
          >
            <Input placeholder={t('roles.roleNamePlaceholder')} />
          </Form.Item>

          <Form.Item name="description" label={t('roles.roleDescription')}>
            <Input.TextArea placeholder={t('roles.descriptionPlaceholder')} rows={3} />
          </Form.Item>

          <Form.Item
            name="permission_ids"
            label={t('roles.permissionAssignment')}
            rules={[{ required: true, message: t('roles.atLeastOne') }]}
          >
            <Select
              mode="multiple"
              placeholder={t('roles.selectPermissions')}
              loading={permissionsLoading}
              optionFilterProp="label"
              showSearch
              maxTagCount="responsive"
            >
              {permissionsData?.grouped &&
                Object.entries(permissionsData.grouped).map(([module, perms]: [string, any]) => (
                  <Select.OptGroup key={module} label={`${module} (${t('roles.modulePrefix').toLowerCase()})`}>
                    {perms.map((perm: any) => (
                      <Select.Option key={perm.id} value={perm.id} label={`${perm.name} ${perm.code}`}>
                        {perm.name} ({perm.code})
                        {perm.description && <span style={{ color: '#999' }}> - {perm.description}</span>}
                      </Select.Option>
                    ))}
                  </Select.OptGroup>
                ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 管理员角色分配 Modal */}
      <Modal
        title={t('roles.assignRoleTo', { username: selectedAdmin?.username })}
        open={isAdminModalVisible}
        onCancel={() => {
          setIsAdminModalVisible(false)
          setSelectedAdmin(null)
          adminRoleForm.resetFields()
        }}
        onOk={() => adminRoleForm.submit()}
        confirmLoading={assignRolesMutation.isPending}
        okText={t('common.confirm')}
        cancelText={t('common.cancel')}
      >
        {selectedAdmin && (
          <div style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label={t('user.username')}>{selectedAdmin.username}</Descriptions.Item>
              <Descriptions.Item label={t('user.email')}>{selectedAdmin.email}</Descriptions.Item>
              <Descriptions.Item label={t('roles.currentRole')}>
                {selectedAdmin.role ? (
                  <Tag color="blue">{selectedAdmin.role.name}</Tag>
                ) : (
                  <Tag color="default">{t('roles.noRole')}</Tag>
                )}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}

        <Form
          form={adminRoleForm}
          layout="vertical"
          onFinish={(values) =>
            selectedAdmin &&
            assignRolesMutation.mutate({
              adminId: selectedAdmin.id,
              roleId: values.role_id || null,
            })
          }
        >
          <Form.Item
            name="role_id"
            label={t('roles.assignRole')}
            rules={[{ required: false }]}
          >
            <Select
              placeholder={t('roles.selectRolePlaceholder')}
              loading={rolesLoading}
              optionFilterProp="label"
              allowClear
            >
              {rolesData?.roles?.map((role: any) => (
                <Select.Option key={role.id} value={role.id} label={role.name}>
                  {role.name}
                  {role.description && <span style={{ color: '#999' }}> - {role.description}</span>}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default RolesList
