import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Spin, message, Modal, Divider, List } from 'antd';
import { getTask, updateTask } from '../../api/tasks';
import type { TaskDetail } from '../../api/tasks';
import { ArrowLeftOutlined, CheckCircleOutlined, SwapOutlined } from '@ant-design/icons';

const MobileTaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [acceptLoading, setAcceptLoading] = useState(false);
  const [transferModalVisible, setTransferModalVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTask = async () => {
      if (!id) return;

      try {
        const response = await getTask(parseInt(id));
        setTask(response);
      } catch (error) {
        console.error('Failed to fetch task:', error);
        message.error('获取工单详情失败');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id]);

  const handleAcceptTask = async () => {
    if (!id) return;

    setAcceptLoading(true);
    try {
      const response = await updateTask(parseInt(id), { status: 'assigned' });
      setTask({ ...task!, ...response });
      message.success('接单成功');
    } catch (error) {
      console.error('Failed to accept task:', error);
      message.error('接单失败');
    } finally {
      setAcceptLoading(false);
    }
  };

  const handleTransferTask = () => {
    setTransferModalVisible(true);
  };

  const handleCompleteTask = () => {
    navigate(`/mobile/tasks/${id}/complete`);
  };

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

  if (!task) {
    return (
      <div>
        <Button
          icon={<ArrowLeftOutlined />}
          style={{ marginBottom: 16 }}
          onClick={() => navigate(-1)}
        >
          返回
        </Button>
        <Card>
          <div style={{ textAlign: 'center' }}>工单不存在或已被删除</div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ paddingBottom: 60 }}>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => navigate(-1)}
      >
        返回
      </Button>

      <Card title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>工单详情</span>
          {getStatusTag(task.status)}
        </div>
      }>
        <Descriptions column={1}>
          <Descriptions.Item label="标题">{task.title}</Descriptions.Item>
          <Descriptions.Item label="描述">{task.description || '无描述'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{new Date(task.created_at).toLocaleString()}</Descriptions.Item>
          {task.assigned_at && (
            <Descriptions.Item label="接单时间">{new Date(task.assigned_at).toLocaleString()}</Descriptions.Item>
          )}
          {task.completed_at && (
            <Descriptions.Item label="完成时间">{new Date(task.completed_at).toLocaleString()}</Descriptions.Item>
          )}
          {task.status === 'completed' && (
            <Descriptions.Item label="总费用">¥{task.total_cost.toFixed(2)}</Descriptions.Item>
          )}
        </Descriptions>

        {task.status === 'completed' && (
          <>
            <Divider orientation="left">使用材料</Divider>
            {task.materials.length > 0 ? (
              <List
                size="small"
                dataSource={task.materials}
                renderItem={material => (
                  <List.Item>
                    <div style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{material.material_id}</span>
                        <span>{material.is_company_provided ? '甲供' : '自购'}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#888' }}>
                        <span>数量: {material.quantity}</span>
                        <span>单价: ¥{material.unit_price.toFixed(2)}</span>
                        <span>总价: ¥{material.total_price.toFixed(2)}</span>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <div>无使用材料</div>
            )}

            <Divider orientation="left">工作内容</Divider>
            {task.work_items.length > 0 ? (
              <List
                size="small"
                dataSource={task.work_items}
                renderItem={workItem => (
                  <List.Item>
                    <div style={{ width: '100%' }}>
                      <div>{workItem.work_item_id}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#888' }}>
                        <span>数量: {workItem.quantity}</span>
                        <span>单价: ¥{workItem.unit_price.toFixed(2)}</span>
                        <span>总价: ¥{workItem.total_price.toFixed(2)}</span>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <div>无工作内容</div>
            )}
          </>
        )}

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-around' }}>
          {task.status === 'pending' && (
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={handleAcceptTask}
              loading={acceptLoading}
            >
              接单
            </Button>
          )}

          {(task.status === 'assigned' || task.status === 'in_progress') && (
            <>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleCompleteTask}
              >
                回单
              </Button>
              <Button
                icon={<SwapOutlined />}
                onClick={handleTransferTask}
              >
                转派
              </Button>
            </>
          )}
        </div>
      </Card>

      <Modal
        title="转派工单"
        open={transferModalVisible}
        onCancel={() => setTransferModalVisible(false)}
        footer={null}
      >
        <p>转派功能正在开发中...</p>
      </Modal>
    </div>
  );
};

export default MobileTaskDetail;
