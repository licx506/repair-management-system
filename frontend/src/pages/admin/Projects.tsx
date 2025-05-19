import React, { useEffect, useState } from 'react';
import {
  Card, Table, Tag, Button, Input, Select,
  Space, Modal, Form, message, Popconfirm
} from 'antd';
import {
  PlusOutlined, SearchOutlined,
  EditOutlined, DeleteOutlined
} from '@ant-design/icons';
import {
  getProjects, createProject, updateProject, deleteProject
} from '../../api/projects';
import type { Project, ProjectCreateParams, ProjectUpdateParams } from '../../api/projects';

const { Option } = Select;

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建项目');
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await getProjects();
      setProjects(response);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      message.error('获取项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = () => {
    setModalTitle('新建项目');
    setEditingProject(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditProject = (project: Project) => {
    setModalTitle('编辑项目');
    setEditingProject(project);
    form.setFieldsValue({
      title: project.title,
      description: project.description,
      location: project.location,
      contact_name: project.contact_name,
      contact_phone: project.contact_phone,
      status: project.status,
      priority: project.priority
    });
    setModalVisible(true);
  };

  const handleDeleteProject = async (id: number) => {
    try {
      await deleteProject(id);
      message.success('删除项目成功');
      fetchProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      message.error('删除项目失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingProject) {
        // 更新项目
        await updateProject(editingProject.id, values as ProjectUpdateParams);
        message.success('更新项目成功');
      } else {
        // 创建项目
        await createProject(values as ProjectCreateParams);
        message.success('创建项目成功');
      }

      setModalVisible(false);
      fetchProjects();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'pending':
        return <Tag color="default">待处理</Tag>;
      case 'in_progress':
        return <Tag color="processing">进行中</Tag>;
      case 'completed':
        return <Tag color="success">已完成</Tag>;
      case 'cancelled':
        return <Tag color="error">已取消</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch =
      project.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (project.description && project.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = !statusFilter || project.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      title: '项目ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '项目名称',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
      filters: [
        { text: '待处理', value: 'pending' },
        { text: '进行中', value: 'in_progress' },
        { text: '已完成', value: 'completed' },
        { text: '已取消', value: 'cancelled' },
      ],
      onFilter: (value: any, record: any) => record.status === value,
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: '联系人',
      dataIndex: 'contact_name',
      key: 'contact_name',
    },
    {
      title: '联系电话',
      dataIndex: 'contact_phone',
      key: 'contact_phone',
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
      render: (_: any, record: Project) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditProject(record)}
          />
          <Popconfirm
            title="确定要删除这个项目吗？"
            onConfirm={() => handleDeleteProject(record.id)}
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
        title="项目管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateProject}
          >
            新建项目
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索项目"
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
            <Option value="pending">待处理</Option>
            <Option value="in_progress">进行中</Option>
            <Option value="completed">已完成</Option>
            <Option value="cancelled">已取消</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredProjects.map(project => ({ ...project, key: project.id }))}
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
          <Form.Item
            name="title"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="项目描述"
          >
            <Input.TextArea placeholder="请输入项目描述" rows={4} />
          </Form.Item>
          <Form.Item
            name="location"
            label="项目位置"
            rules={[{ required: true, message: '请输入项目位置' }]}
          >
            <Input placeholder="请输入项目位置" />
          </Form.Item>
          <Form.Item
            name="contact_name"
            label="联系人"
            rules={[{ required: true, message: '请输入联系人' }]}
          >
            <Input placeholder="请输入联系人" />
          </Form.Item>
          <Form.Item
            name="contact_phone"
            label="联系电话"
            rules={[{ required: true, message: '请输入联系电话' }]}
          >
            <Input placeholder="请输入联系电话" />
          </Form.Item>
          {editingProject && (
            <Form.Item
              name="status"
              label="状态"
            >
              <Select>
                <Option value="pending">待处理</Option>
                <Option value="in_progress">进行中</Option>
                <Option value="completed">已完成</Option>
                <Option value="cancelled">已取消</Option>
              </Select>
            </Form.Item>
          )}
          <Form.Item
            name="priority"
            label="优先级"
            initialValue={1}
          >
            <Select>
              <Option value={1}>低</Option>
              <Option value={2}>中低</Option>
              <Option value={3}>中</Option>
              <Option value={4}>中高</Option>
              <Option value={5}>高</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Projects;
