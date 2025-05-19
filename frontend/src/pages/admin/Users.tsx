import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select,
  Space, Modal, Form, message, Popconfirm, Tag, Alert
} from 'antd';
import {
  PlusOutlined, SearchOutlined,
  EditOutlined, DeleteOutlined, UserOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import {
  getUsers, getUser, updateUser, deleteUser
} from '../../api/users';
import { register } from '../../api/auth';
import type { User } from '../../api/auth';
import type { UserUpdateParams } from '../../api/users';
import { useAuth } from '../../contexts/AuthContext';
import { getToken, isAdmin } from '../../utils/auth';

const { Option } = Select;

const Users: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [roleFilter, setRoleFilter] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建用户');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);

    // 检查用户是否已登录
    const token = getToken();
    if (!token) {
      setError('您尚未登录或登录已过期，请重新登录');
      setLoading(false);
      return;
    }

    // 检查用户是否是管理员
    if (!isAdmin()) {
      setError('您没有权限访问此页面');
      setLoading(false);
      return;
    }

    try {
      console.log('Fetching users with token:', token);
      const response = await getUsers();
      console.log('Users fetched:', response);
      setUsers(response);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      if (error instanceof Error) {
        setError(`获取用户列表失败: ${error.message}`);
      } else {
        setError('获取用户列表失败');
      }
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setModalTitle('新建用户');
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditUser = (user: User) => {
    setModalTitle('编辑用户');
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      phone: user.phone,
      role: user.role,
      is_active: user.is_active
    });
    setModalVisible(true);
  };

  const handleDeleteUser = async (id: number) => {
    try {
      await deleteUser(id);
      message.success('删除用户成功');
      fetchUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      message.error('删除用户失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingUser) {
        // 更新用户
        try {
          console.log('Updating user with values:', values);
          const updateParams: UserUpdateParams = {
            email: values.email,
            full_name: values.full_name,
            phone: values.phone,
            role: values.role,
            is_active: values.is_active
          };
          const updatedUser = await updateUser(editingUser.id, updateParams);
          console.log('User updated successfully:', updatedUser);
          message.success('更新用户成功');

          // 关闭模态框
          setModalVisible(false);

          // 添加延迟，确保后端有足够时间处理请求
          setTimeout(() => {
            fetchUsers();
          }, 500);
        } catch (error) {
          console.error('Failed to update user:', error);
          message.error('更新用户失败: ' + (error instanceof Error ? error.message : String(error)));
        }
      } else {
        // 创建用户
        try {
          console.log('Creating user with values:', values);
          const newUser = await register({
            username: values.username,
            password: values.password,
            email: values.email,
            full_name: values.full_name,
            phone: values.phone,
            role: values.role
          });
          console.log('User created successfully:', newUser);
          message.success('创建用户成功');

          // 关闭模态框
          setModalVisible(false);

          // 添加延迟，确保后端有足够时间处理请求
          setTimeout(() => {
            fetchUsers();
          }, 500);
        } catch (error) {
          console.error('Failed to create user:', error);
          message.error('创建用户失败: ' + (error instanceof Error ? error.message : String(error)));
        }
      }
    } catch (error) {
      console.error('Form validation failed:', error);
      message.error('表单验证失败，请检查输入');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch =
      user.username.toLowerCase().includes(searchText.toLowerCase()) ||
      user.email.toLowerCase().includes(searchText.toLowerCase()) ||
      (user.full_name && user.full_name.toLowerCase().includes(searchText.toLowerCase()));

    const matchesRole = roleFilter === undefined || user.role === roleFilter;
    const matchesStatus = statusFilter === undefined || user.is_active === statusFilter;

    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleTag = (role: string) => {
    switch (role) {
      case 'admin':
        return <Tag color="red">管理员</Tag>;
      case 'manager':
        return <Tag color="blue">经理</Tag>;
      case 'worker':
        return <Tag color="green">工人</Tag>;
      default:
        return <Tag>{role}</Tag>;
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
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
      render: (text: string) => text || '-',
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      render: (text: string) => text || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => getRoleTag(role),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        active ? <span style={{ color: '#52c41a' }}>启用</span> : <span style={{ color: '#ff4d4f' }}>禁用</span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: User) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditUser(record)}
          />
          <Popconfirm
            title="确定要删除这个用户吗？"
            onConfirm={() => handleDeleteUser(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="用户管理"
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchUsers}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateUser}
            >
              新建用户
            </Button>
          </Space>
        }
      >
        {error && (
          <Alert
            message="错误"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Button size="small" type="primary" onClick={fetchUsers}>
                重试
              </Button>
            }
          />
        )}
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索用户"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Select
            placeholder="角色筛选"
            style={{ width: 120 }}
            allowClear
            value={roleFilter}
            onChange={value => setRoleFilter(value)}
          >
            <Option value="admin">管理员</Option>
            <Option value="manager">经理</Option>
            <Option value="worker">工人</Option>
          </Select>
          <Select
            placeholder="状态筛选"
            style={{ width: 120 }}
            allowClear
            value={statusFilter}
            onChange={value => setStatusFilter(value)}
          >
            <Option value={true}>启用</Option>
            <Option value={false}>禁用</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredUsers.map(user => ({ ...user, key: user.id }))}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          {!editingUser && (
            <>
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item
                name="password"
                label="密码"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item
            name="full_name"
            label="姓名"
          >
            <Input placeholder="请输入姓名" />
          </Form.Item>
          <Form.Item
            name="phone"
            label="电话"
          >
            <Input placeholder="请输入电话" />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            initialValue="worker"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="admin">管理员</Option>
              <Option value="manager">经理</Option>
              <Option value="worker">工人</Option>
            </Select>
          </Form.Item>
          {editingUser && (
            <Form.Item
              name="is_active"
              label="状态"
              initialValue={true}
            >
              <Select>
                <Option value={true}>启用</Option>
                <Option value={false}>禁用</Option>
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default Users;
