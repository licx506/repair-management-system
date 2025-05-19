import React, { useEffect, useState } from 'react';
import { Card, List, Tag, Statistic, Row, Col, Spin, Empty } from 'antd';
import { useNavigate } from 'react-router-dom';
import { getMyTasks } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { CheckCircleOutlined, ClockCircleOutlined, ToolOutlined } from '@ant-design/icons';

const MobileHome: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await getMyTasks();
        setTasks(response);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const pendingTasks = tasks.filter(task => task.status === 'pending');
  const assignedTasks = tasks.filter(task => task.status === 'assigned' || task.status === 'in_progress');
  const completedTasks = tasks.filter(task => task.status === 'completed');

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

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 'calc(100vh - 64px - 50px)' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ paddingBottom: 60 }}>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card>
            <Statistic
              title="待接单"
              value={pendingTasks.length}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="进行中"
              value={assignedTasks.length}
              valueStyle={{ color: '#faad14' }}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已完成"
              value={completedTasks.length}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="我的工单" style={{ marginTop: 16 }}>
        {tasks.length > 0 ? (
          <List
            itemLayout="horizontal"
            dataSource={tasks.slice(0, 5)}
            renderItem={task => (
              <List.Item
                onClick={() => navigate(`/mobile/tasks/${task.id}`)}
                style={{ cursor: 'pointer' }}
              >
                <List.Item.Meta
                  title={
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>{task.title}</span>
                      {getStatusTag(task.status)}
                    </div>
                  }
                  description={task.description || '无描述'}
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无工单" />
        )}
      </Card>
    </div>
  );
};

export default MobileHome;
