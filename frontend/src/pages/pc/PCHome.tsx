import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ToolOutlined,
  ProjectOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { getMyTasks } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { getProjects } from '../../api/projects';
import { getTeams } from '../../api/teams';
import { getTaskStatistics } from '../../api/statistics';
import type { TaskStatistics } from '../../api/statistics';

const PCHome: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tasksResponse, statisticsResponse] = await Promise.all([
          getMyTasks(),
          getTaskStatistics()
        ]);
        setTasks(tasksResponse);
        setStatistics(statisticsResponse);
      } catch (error) {
        console.error('Failed to fetch data:', error);
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
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: Task) => (
        <span>
          {record.status === 'pending' && (
            <Button
              type="link"
              size="small"
              onClick={() => navigate(`/pc/tasks/${record.id}/accept`)}
            >
              接单
            </Button>
          )}
          {(record.status === 'assigned' || record.status === 'in_progress') && (
            <Button
              type="link"
              size="small"
              onClick={() => navigate(`/pc/tasks/${record.id}/complete`)}
            >
              回单
            </Button>
          )}
          <Button
            type="link"
            size="small"
            onClick={() => navigate(`/pc/tasks/${record.id}`)}
          >
            查看
          </Button>
        </span>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="待接单"
              value={statistics?.pending_tasks || 0}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={statistics?.in_progress_tasks || 0}
              valueStyle={{ color: '#faad14' }}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={statistics?.completed_tasks || 0}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="完成率"
              value={(statistics?.completion_rate || 0) * 100}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card title="我的工单" style={{ marginTop: 16 }}>
        <Table
          columns={columns}
          dataSource={tasks.slice(0, 5).map(task => ({ ...task, key: task.id }))}
          loading={loading}
          pagination={false}
        />
        {tasks.length > 5 && (
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Button type="link" onClick={() => navigate('/pc/tasks')}>
              查看更多
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default PCHome;
