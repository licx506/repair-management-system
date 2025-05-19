import React, { useEffect, useState } from 'react';
import { List, Tag, Spin, Empty, Input, Card } from 'antd';
import { useNavigate } from 'react-router-dom';
import { getMyTasks } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { SearchOutlined, CheckCircleOutlined } from '@ant-design/icons';

const MobileCompleted: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await getMyTasks({ status: 'completed' });
        setTasks(response);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const filteredTasks = tasks.filter(task =>
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
        placeholder="搜索已完成工单"
        prefix={<SearchOutlined />}
        value={searchText}
        onChange={e => setSearchText(e.target.value)}
        style={{ marginBottom: 16 }}
        allowClear
      />

      <Card title={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
          <span>已完成工单</span>
        </div>
      }>
        {filteredTasks.length > 0 ? (
          <List
            itemLayout="horizontal"
            dataSource={filteredTasks}
            renderItem={task => (
              <List.Item
                onClick={() => navigate(`/mobile/tasks/${task.id}`)}
                style={{ cursor: 'pointer' }}
              >
                <List.Item.Meta
                  title={task.title}
                  description={
                    <div>
                      <div>{task.description || '无描述'}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#888', marginTop: '4px' }}>
                        <span>完成时间: {task.completed_at ? new Date(task.completed_at).toLocaleString() : '未知'}</span>
                        <span>费用: ¥{task.total_cost.toFixed(2)}</span>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无已完成工单" />
        )}
      </Card>
    </div>
  );
};

export default MobileCompleted;
