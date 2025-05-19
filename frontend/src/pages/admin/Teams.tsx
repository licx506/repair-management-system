import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select, Tag,
  Space, Modal, Form, message, Popconfirm, Tabs, Avatar, List
} from 'antd';
import {
  PlusOutlined, SearchOutlined, EditOutlined, 
  DeleteOutlined, UserAddOutlined, UserDeleteOutlined, TeamOutlined
} from '@ant-design/icons';
import {
  getTeams, createTeam, updateTeam, deleteTeam,
  getTeam, addTeamMember, removeTeamMember
} from '../../api/teams';
import type { Team, TeamDetail, TeamCreateParams, TeamUpdateParams, TeamMemberCreateParams } from '../../api/teams';
import { getUsers } from '../../api/users';
import type { User } from '../../api/auth';

const { Option } = Select;
const { TabPane } = Tabs;

const Teams: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [memberModalVisible, setMemberModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建施工队伍');
  const [editingTeam, setEditingTeam] = useState<Team | null>(null);
  const [currentTeam, setCurrentTeam] = useState<TeamDetail | null>(null);
  const [form] = Form.useForm();
  const [memberForm] = Form.useForm();

  useEffect(() => {
    fetchTeams();
    fetchUsers();
  }, []);

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const response = await getTeams();
      setTeams(response);
    } catch (error) {
      console.error('Failed to fetch teams:', error);
      message.error('获取施工队伍列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await getUsers();
      setUsers(response);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      message.error('获取用户列表失败');
    }
  };

  const fetchTeamDetail = async (teamId: number) => {
    try {
      const response = await getTeam(teamId);
      setCurrentTeam(response);
      return response;
    } catch (error) {
      console.error('Failed to fetch team details:', error);
      message.error('获取施工队伍详情失败');
      return null;
    }
  };

  const handleCreateTeam = () => {
    setModalTitle('新建施工队伍');
    setEditingTeam(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditTeam = (team: Team) => {
    setModalTitle('编辑施工队伍');
    setEditingTeam(team);
    form.setFieldsValue({
      name: team.name,
      description: team.description,
      is_active: team.is_active
    });
    setModalVisible(true);
  };

  const handleDeleteTeam = async (id: number) => {
    try {
      await deleteTeam(id);
      message.success('删除施工队伍成功');
      fetchTeams();
    } catch (error) {
      console.error('Failed to delete team:', error);
      message.error('删除施工队伍失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingTeam) {
        // 更新施工队伍
        await updateTeam(editingTeam.id, values as TeamUpdateParams);
        message.success('更新施工队伍成功');
      } else {
        // 创建施工队伍
        await createTeam(values as TeamCreateParams);
        message.success('创建施工队伍成功');
      }

      setModalVisible(false);
      fetchTeams();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const handleManageMembers = async (team: Team) => {
    const teamDetail = await fetchTeamDetail(team.id);
    if (teamDetail) {
      setMemberModalVisible(true);
    }
  };

  const handleAddMember = async () => {
    try {
      if (!currentTeam) return;
      
      const values = await memberForm.validateFields();
      const params: TeamMemberCreateParams = {
        user_id: values.user_id,
        is_leader: values.is_leader || false
      };
      
      await addTeamMember(currentTeam.id, params);
      message.success('添加队员成功');
      fetchTeamDetail(currentTeam.id);
      memberForm.resetFields();
    } catch (error) {
      console.error('Failed to add team member:', error);
      message.error('添加队员失败');
    }
  };

  const handleRemoveMember = async (teamId: number, userId: number) => {
    try {
      await removeTeamMember(teamId, userId);
      message.success('移除队员成功');
      fetchTeamDetail(teamId);
    } catch (error) {
      console.error('Failed to remove team member:', error);
      message.error('移除队员失败');
    }
  };

  const filteredTeams = teams.filter(team => {
    const matchesSearch =
      team.name.toLowerCase().includes(searchText.toLowerCase()) ||
      (team.description && team.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = statusFilter === undefined || team.is_active === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '队伍名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Team) => (
        <Space size="small">
          <Button
            type="text"
            icon={<TeamOutlined />}
            onClick={() => handleManageMembers(record)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditTeam(record)}
          />
          <Popconfirm
            title="确定要删除这个施工队伍吗？"
            onConfirm={() => handleDeleteTeam(record.id)}
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

  // 过滤掉已经在队伍中的用户
  const availableUsers = users.filter(user => {
    if (!currentTeam) return true;
    return !currentTeam.members.some(member => member.user_id === user.id);
  });

  return (
    <div>
      <Card
        title="施工队伍管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateTeam}
          >
            新建施工队伍
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索施工队伍"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
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
          dataSource={filteredTeams.map(team => ({ ...team, key: team.id }))}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建/编辑施工队伍的模态框 */}
      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="队伍名称"
            rules={[{ required: true, message: '请输入队伍名称' }]}
          >
            <Input placeholder="请输入队伍名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="队伍描述"
          >
            <Input.TextArea placeholder="请输入队伍描述" rows={4} />
          </Form.Item>
          {editingTeam && (
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

      {/* 管理队员的模态框 */}
      <Modal
        title={`管理队员 - ${currentTeam?.name}`}
        open={memberModalVisible}
        onCancel={() => setMemberModalVisible(false)}
        footer={null}
        width={800}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="队员列表" key="1">
            <List
              dataSource={currentTeam?.members || []}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Popconfirm
                      title="确定要移除这个队员吗？"
                      onConfirm={() => handleRemoveMember(currentTeam!.id, item.user_id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<UserDeleteOutlined />}
                      >
                        移除
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar>{item.user.full_name?.[0] || item.user.username[0]}</Avatar>}
                    title={
                      <Space>
                        {item.user.full_name || item.user.username}
                        {item.is_leader && <Tag color="gold">队长</Tag>}
                      </Space>
                    }
                    description={`电话: ${item.user.phone || '未设置'} | 加入时间: ${new Date(item.joined_at).toLocaleString()}`}
                  />
                </List.Item>
              )}
            />
          </TabPane>
          <TabPane tab="添加队员" key="2">
            <Form form={memberForm} layout="vertical" onFinish={handleAddMember}>
              <Form.Item
                name="user_id"
                label="选择用户"
                rules={[{ required: true, message: '请选择用户' }]}
              >
                <Select
                  placeholder="请选择用户"
                  showSearch
                  optionFilterProp="children"
                >
                  {availableUsers.map(user => (
                    <Option key={user.id} value={user.id}>
                      {user.full_name || user.username} ({user.phone || '无电话'})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="is_leader"
                label="是否为队长"
                valuePropName="checked"
                initialValue={false}
              >
                <Select>
                  <Option value={true}>是</Option>
                  <Option value={false}>否</Option>
                </Select>
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<UserAddOutlined />}>
                  添加队员
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default Teams;
