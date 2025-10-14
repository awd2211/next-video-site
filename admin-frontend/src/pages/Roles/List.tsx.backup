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
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SafetyOutlined,
  UserOutlined,
  KeyOutlined,
} from '@ant-design/icons'
import { useState } from 'react'
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

  // 创建/更新角色
  const saveRoleMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingRole) {
        return axios.put(`/api/v1/admin/rbac/roles/${editingRole.id}`, values)
      }
      return axios.post('/api/v1/admin/rbac/roles', values)
    },
    onSuccess: () => {
      message.success(editingRole ? '更新成功' : '创建成功')
      setIsRoleModalVisible(false)
      setEditingRole(null)
      roleForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // 删除角色
  const deleteRoleMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/v1/admin/rbac/roles/${id}`),
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  // 分配角色给管理员
  const assignRolesMutation = useMutation({
    mutationFn: async ({ adminId, roleId }: { adminId: number; roleId: number | null }) => {
      return axios.post(`/api/v1/admin/rbac/admin-users/${adminId}/role`, { role_id: roleId })
    },
    onSuccess: () => {
      message.success('角色分配成功')
      setIsAdminModalVisible(false)
      setSelectedAdmin(null)
      adminRoleForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '分配失败')
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
      title: '确认删除',
      content: `确定要删除角色"${role.name}"吗？此操作不可恢复。`,
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      onOk: () => deleteRoleMutation.mutate(role.id),
    })
  }

  const handleAssignRoles = (admin: any) => {
    if (admin.is_superadmin) {
      message.info('超级管理员拥有所有权限，无需分配角色')
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
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <Space>
          <SafetyOutlined style={{ color: record.is_active ? '#1890ff' : '#999' }} />
          <span>{name}</span>
          {!record.is_active && <Tag color="default">已禁用</Tag>}
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '权限数量',
      key: 'permissions',
      width: 120,
      render: (_: any, record: any) => (
        <Tag color="blue">{record.permission_count || 0} 个权限</Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEditRole(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteRole(record)}
          >
            删除
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
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: any) => (
        <Space>
          <UserOutlined />
          <span>{username}</span>
          {record.is_superadmin && <Tag color="gold">超级管理员</Tag>}
          {!record.is_active && <Tag color="red">已禁用</Tag>}
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
    },
    {
      title: '角色',
      key: 'role',
      render: (_: any, record: any) => (
        <Space wrap>
          {record.is_superadmin ? (
            <Tag color="gold">所有权限</Tag>
          ) : record.role ? (
            <Tag color="blue">{record.role.name}</Tag>
          ) : (
            <Tag color="default">无角色</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      width: 180,
      render: (date: string) => (date ? new Date(date).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Button
          type="link"
          icon={<KeyOutlined />}
          onClick={() => handleAssignRoles(record)}
          disabled={record.is_superadmin}
        >
          分配角色
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
                角色管理
              </span>
            ),
            children: (
              <Card
                title="角色列表"
                extra={
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                      setEditingRole(null)
                      roleForm.resetFields()
                      setIsRoleModalVisible(true)
                    }}
                  >
                    创建角色
                  </Button>
                }
              >
                <Table
                  columns={roleColumns}
                  dataSource={rolesData?.roles}
                  loading={rolesLoading}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                />
              </Card>
            ),
          },
          {
            key: 'permissions',
            label: (
              <span>
                <KeyOutlined />
                权限列表
              </span>
            ),
            children: (
              <Card title="系统权限">
                {permissionsLoading ? (
                  <div>加载中...</div>
                ) : (
                  <Space direction="vertical" style={{ width: '100%' }} size="large">
                    {permissionsData?.grouped &&
                      Object.entries(permissionsData.grouped).map(([module, perms]: [string, any]) => (
                        <Card key={module} type="inner" title={`模块: ${module}`} size="small">
                          <Space wrap>
                            {perms.map((perm: any) => (
                              <Tag key={perm.id} color="blue">
                                {perm.name} ({perm.code})
                              </Tag>
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
                管理员用户
              </span>
            ),
            children: (
              <Card title="管理员列表">
                <Table
                  columns={adminColumns}
                  dataSource={adminUsersData?.admin_users}
                  loading={adminUsersLoading}
                  rowKey="id"
                  pagination={{ pageSize: 20 }}
                />
              </Card>
            ),
          },
        ]}
      />

      {/* 角色编辑 Modal */}
      <Modal
        title={editingRole ? '编辑角色' : '创建角色'}
        open={isRoleModalVisible}
        onCancel={() => {
          setIsRoleModalVisible(false)
          setEditingRole(null)
          roleForm.resetFields()
        }}
        onOk={() => roleForm.submit()}
        confirmLoading={saveRoleMutation.isPending}
        width={700}
      >
        <Form
          form={roleForm}
          layout="vertical"
          onFinish={(values) => saveRoleMutation.mutate(values)}
        >
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="例如：内容编辑、审核员" />
          </Form.Item>

          <Form.Item name="description" label="角色描述">
            <Input.TextArea placeholder="简要描述该角色的职责" rows={3} />
          </Form.Item>

          <Form.Item
            name="permission_ids"
            label="权限分配"
            rules={[{ required: true, message: '请至少选择一个权限' }]}
          >
            <Select
              mode="multiple"
              placeholder="选择权限"
              loading={permissionsLoading}
              optionFilterProp="label"
              showSearch
            >
              {permissionsData?.grouped &&
                Object.entries(permissionsData.grouped).map(([module, perms]: [string, any]) => (
                  <Select.OptGroup key={module} label={`${module} (模块)`}>
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
        title={`为 ${selectedAdmin?.username} 分配角色`}
        open={isAdminModalVisible}
        onCancel={() => {
          setIsAdminModalVisible(false)
          setSelectedAdmin(null)
          adminRoleForm.resetFields()
        }}
        onOk={() => adminRoleForm.submit()}
        confirmLoading={assignRolesMutation.isPending}
      >
        {selectedAdmin && (
          <div style={{ marginBottom: 16 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="用户名">{selectedAdmin.username}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{selectedAdmin.email}</Descriptions.Item>
              <Descriptions.Item label="当前角色">
                {selectedAdmin.role ? (
                  <Tag color="blue">{selectedAdmin.role.name}</Tag>
                ) : (
                  <Tag color="default">无角色</Tag>
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
            label="选择角色"
            rules={[{ required: false, message: '请选择一个角色' }]}
          >
            <Select
              placeholder="选择角色（留空表示取消分配）"
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
