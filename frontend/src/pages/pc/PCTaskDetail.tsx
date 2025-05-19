import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Descriptions, Tag, Button, Spin, message,
  Modal, Form, Select, Divider, Table, Typography
} from 'antd';
import {
  ArrowLeftOutlined, CheckCircleOutlined,
  SwapOutlined, EditOutlined
} from '@ant-design/icons';
import { getTask, updateTask } from '../../api/tasks';
import type { TaskDetail } from '../../api/tasks';
import { getTeams } from '../../api/teams';

const { Title } = Typography;
const { Option } = Select;

const PCTaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [acceptLoading, setAcceptLoading] = useState(false);
  const [transferModalVisible, setTransferModalVisible] = useState(false);
  const [form] = Form.useForm();
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

  const handleTransferSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (!id) return;

      const response = await updateTask(parseInt(id), {
        team_id: values.team_id,
        assigned_to_id: values.user_id
      });

      setTask({ ...task!, ...response });
      message.success('转派成功');
      setTransferModalVisible(false);
    } catch (error) {
      console.error('Failed to transfer task:', error);
      message.error('转派失败');
    }
  };

  const handleCompleteTask = () => {
    navigate(`/pc/tasks/${id}/complete`);
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

  const materialColumns = [
    {
      title: '材料ID',
      dataIndex: 'material_id',
      key: 'material_id',
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '类型',
      dataIndex: 'is_company_provided',
      key: 'is_company_provided',
      render: (isCompanyProvided: boolean) => (
        isCompanyProvided ? <Tag color="blue">甲供</Tag> : <Tag color="green">自购</Tag>
      ),
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      key: 'total_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
  ];

  const workItemColumns = [
    {
      title: '工作内容ID',
      dataIndex: 'work_item_id',
      key: 'work_item_id',
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      key: 'total_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
  ];

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
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => navigate(-1)}
      >
        返回
      </Button>

      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>工单详情</span>
            {getStatusTag(task.status)}
          </div>
        }
        extra={
          <div>
            {task.status === 'pending' && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleAcceptTask}
                loading={acceptLoading}
                style={{ marginRight: 8 }}
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
                  style={{ marginRight: 8 }}
                >
                  回单
                </Button>
                <Button
                  icon={<SwapOutlined />}
                  onClick={handleTransferTask}
                  style={{ marginRight: 8 }}
                >
                  转派
                </Button>
              </>
            )}

            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/pc/tasks/${id}/edit`)}
            >
              编辑
            </Button>
          </div>
        }
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="工单ID">{task.id}</Descriptions.Item>
          <Descriptions.Item label="项目ID">{task.project_id}</Descriptions.Item>
          <Descriptions.Item label="标题">{task.title}</Descriptions.Item>
          <Descriptions.Item label="状态">{getStatusTag(task.status)}</Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>{task.description || '无描述'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{new Date(task.created_at).toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="创建人ID">{task.created_by_id}</Descriptions.Item>

          {task.assigned_to_id && (
            <Descriptions.Item label="指派给">{task.assigned_to_id}</Descriptions.Item>
          )}

          {task.team_id && (
            <Descriptions.Item label="施工队">{task.team_id}</Descriptions.Item>
          )}

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
            <Table
              columns={materialColumns}
              dataSource={task.materials.map(material => ({ ...material, key: material.id }))}
              pagination={false}
            />

            <Divider orientation="left">工作内容</Divider>
            <Table
              columns={workItemColumns}
              dataSource={task.work_items.map(workItem => ({ ...workItem, key: workItem.id }))}
              pagination={false}
            />
          </>
        )}
      </Card>

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

export default PCTaskDetail;
