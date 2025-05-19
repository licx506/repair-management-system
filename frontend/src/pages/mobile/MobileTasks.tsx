import React, { useEffect, useState } from 'react';
import { List, Tag, Tabs, Spin, Empty, Input, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { getTasks } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { SearchOutlined } from '@ant-design/icons';

const { TabPane } = Tabs;

const MobileTasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await getTasks();
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

  const filteredPendingTasks = pendingTasks.filter(task =>
    task.title.toLowerCase().includes(searchText.toLowerCase()) ||
    (task.description && task.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const filteredAssignedTasks = assignedTasks.filter(task =>
    task.title.toLowerCase().includes(searchText.toLowerCase()) ||
    (task.description && task.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 'calc(100vh - 64px - 50px)' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ paddingBottom: 60 }}>
      <Input
        placeholder="搜索工单"
        prefix={<SearchOutlined />}
        value={searchText}
        onChange={e => setSearchText(e.target.value)}
        style={{ marginBottom: 16 }}
        allowClear
      />

      <Tabs defaultActiveKey="pending">
        <TabPane tab="待接单" key="pending">
          {filteredPendingTasks.length > 0 ? (
            <List
              itemLayout="horizontal"
              dataSource={filteredPendingTasks}
              renderItem={task => (
                <List.Item
                  onClick={() => navigate(`/mobile/tasks/${task.id}`)}
                  style={{ cursor: 'pointer' }}
                  actions={[
                    <Button
                      type="primary"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/mobile/tasks/${task.id}/accept`);
                      }}
                    >
                      接单
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{task.title}</span>
                        {getStatusTag(task.status)}
                      </div>
                    }
                    description={
                      <div>
                        <div>{task.description || '无描述'}</div>
                        <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                          创建时间: {new Date(task.created_at).toLocaleString()}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty description="暂无待接单工单" />
          )}
        </TabPane>
        <TabPane tab="进行中" key="assigned">
          {filteredAssignedTasks.length > 0 ? (
            <List
              itemLayout="horizontal"
              dataSource={filteredAssignedTasks}
              renderItem={task => (
                <List.Item
                  onClick={() => navigate(`/mobile/tasks/${task.id}`)}
                  style={{ cursor: 'pointer' }}
                  actions={[
                    <Button
                      type="primary"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/mobile/tasks/${task.id}/complete`);
                      }}
                    >
                      回单
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{task.title}</span>
                        {getStatusTag(task.status)}
                      </div>
                    }
                    description={
                      <div>
                        <div>{task.description || '无描述'}</div>
                        <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                          接单时间: {task.assigned_at ? new Date(task.assigned_at).toLocaleString() : '未知'}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty description="暂无进行中工单" />
          )}
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MobileTasks;
