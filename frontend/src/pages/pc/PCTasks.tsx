import React, { useEffect, useState } from 'react';
import {
  Card, Table, Tag, Button, Input, Select,
  Space, Tabs, Modal, Form, message
} from 'antd';
import { useNavigate } from 'react-router-dom';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';
import { getTasks, getMyTasks, updateTask } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { getProjects } from '../../api/projects';
import { getTeams } from '../../api/teams';

const { Option } = Select;
const { TabPane } = Tabs;

const PCTasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [myTasks, setMyTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [transferModalVisible, setTransferModalVisible] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [allTasksResponse, myTasksResponse] = await Promise.all([
          getTasks(),
          getMyTasks()
        ]);
        setTasks(allTasksResponse);
        setMyTasks(myTasksResponse);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'pending':
        return <Tag color="default">待接单</Tag>;
      case 'assigned':
        return <Tag color="processing">已接单</Tag>;
      case 'in_progress':
        return <Tag color="warning">进行中</Tag>;
      case 'completed':
        return <Tag color="success">已完成</Tag>;
      case 'cancelled':
        return <Tag color="error">已取消</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  const handleAcceptTask = async (taskId: number) => {
    try {
      const response = await updateTask(taskId, { status: 'assigned' });

      // 更新任务列表
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, ...response } : task
      ));
      setMyTasks([...myTasks, response]);

      message.success('接单成功');
    } catch (error) {
      console.error('Failed to accept task:', error);
      message.error('接单失败');
    }
  };

  const handleTransferTask = (task: Task) => {
    setCurrentTask(task);
    setTransferModalVisible(true);
  };

  const handleTransferSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (!currentTask) return;

      await updateTask(currentTask.id, {
        team_id: values.team_id,
        assigned_to_id: values.user_id
      });

      message.success('转派成功');
      setTransferModalVisible(false);

      // 刷新任务列表
      const [allTasksResponse, myTasksResponse] = await Promise.all([
        getTasks(),
        getMyTasks()
      ]);
      setTasks(allTasksResponse);
      setMyTasks(myTasksResponse);
    } catch (error) {
      console.error('Failed to transfer task:', error);
      message.error('转派失败');
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = !statusFilter || task.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const filteredMyTasks = myTasks.filter(task => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = !statusFilter || task.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      title: '工单标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Task) => (
        <a onClick={() => navigate(`/pc/tasks/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
      filters: [
        { text: '待接单', value: 'pending' },
        { text: '已接单', value: 'assigned' },
        { text: '进行中', value: 'in_progress' },
        { text: '已完成', value: 'completed' },
        { text: '已取消', value: 'cancelled' },
      ],
      onFilter: (value: string, record: Task) => record.status === value,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a: Task, b: Task) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: Task) => (
        <Space size="small">
          {record.status === 'pending' && (
            <Button
              type="link"
              size="small"
              onClick={() => handleAcceptTask(record.id)}
            >
              接单
            </Button>
          )}
          {(record.status === 'assigned' || record.status === 'in_progress') && (
            <>
              <Button
                type="link"
                size="small"
                onClick={() => navigate(`/pc/tasks/${record.id}/complete`)}
              >
                回单
              </Button>
              <Button
                type="link"
                size="small"
                onClick={() => handleTransferTask(record)}
              >
                转派
              </Button>
            </>
          )}
          <Button
            type="link"
            size="small"
            onClick={() => navigate(`/pc/tasks/${record.id}`)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索工单"
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
          <Option value="pending">待接单</Option>
          <Option value="assigned">已接单</Option>
          <Option value="in_progress">进行中</Option>
          <Option value="completed">已完成</Option>
          <Option value="cancelled">已取消</Option>
        </Select>
      </Space>

      <Tabs defaultActiveKey="all">
        <TabPane tab="所有工单" key="all">
          <Table
            columns={columns}
            dataSource={filteredTasks.map(task => ({ ...task, key: task.id }))}
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </TabPane>
        <TabPane tab="我的工单" key="my">
          <Table
            columns={columns}
            dataSource={filteredMyTasks.map(task => ({ ...task, key: task.id }))}
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </TabPane>
      </Tabs>

      <Modal
        title="转派工单"
        open={transferModalVisible}
        onOk={handleTransferSubmit}
        onCancel={() => setTransferModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="team_id"
            label="选择施工队"
            rules={[{ required: true, message: '请选择施工队' }]}
          >
            <Select placeholder="选择施工队">
              <Option value={1}>施工队1</Option>
              <Option value={2}>施工队2</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="user_id"
            label="选择施工人员"
            rules={[{ required: true, message: '请选择施工人员' }]}
          >
            <Select placeholder="选择施工人员">
              <Option value={1}>施工人员1</Option>
              <Option value={2}>施工人员2</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PCTasks;
