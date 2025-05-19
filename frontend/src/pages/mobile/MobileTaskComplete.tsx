import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Button, Spin, message, Form, Divider,
  Select, InputNumber, Switch, Space, Typography
} from 'antd';
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { getTask, completeTask } from '../../api/tasks';
import type { TaskDetail, TaskCompleteParams } from '../../api/tasks';
import { getMaterials } from '../../api/materials';
import type { Material } from '../../api/materials';
import { getWorkItems } from '../../api/work-items';
import type { WorkItem } from '../../api/work-items';

const { Title } = Typography;
const { Option } = Select;

const MobileTaskComplete: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;

      try {
        const [taskResponse, materialsResponse, workItemsResponse] = await Promise.all([
          getTask(parseInt(id)),
          getMaterials({ is_active: true }),
          getWorkItems({ is_active: true })
        ]);

        setTask(taskResponse);
        setMaterials(materialsResponse);
        setWorkItems(workItemsResponse);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        message.error('获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSubmit = async (values: any) => {
    if (!id) return;

    const params: TaskCompleteParams = {
      materials: values.materials || [],
      work_items: values.work_items || []
    };

    setSubmitting(true);
    try {
      await completeTask(parseInt(id), params);
      message.success('回单成功');
      navigate(`/mobile/tasks/${id}`);
    } catch (error) {
      console.error('Failed to complete task:', error);
      message.error('回单失败');
    } finally {
      setSubmitting(false);
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

      <Card title="工单回单">
        <Title level={4}>{task.title}</Title>
        <p>{task.description || '无描述'}</p>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ materials: [{}], work_items: [{}] }}
        >
          <Divider orientation="left">使用材料</Divider>
          <Form.List name="materials">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'material_id']}
                      rules={[{ required: true, message: '请选择材料' }]}
                    >
                      <Select placeholder="选择材料" style={{ width: 120 }}>
                        {materials.map(material => (
                          <Option key={material.id} value={material.id}>
                            {material.name} (¥{material.unit_price}/{material.unit})
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'quantity']}
                      rules={[{ required: true, message: '请输入数量' }]}
                    >
                      <InputNumber placeholder="数量" min={0.01} step={0.01} />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'is_company_provided']}
                      valuePropName="checked"
                      initialValue={false}
                    >
                      <Switch checkedChildren="甲供" unCheckedChildren="自购" />
                    </Form.Item>
                    <DeleteOutlined onClick={() => remove(name)} />
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    添加材料
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>

          <Divider orientation="left">工作内容</Divider>
          <Form.List name="work_items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'work_item_id']}
                      rules={[{ required: true, message: '请选择工作内容' }]}
                    >
                      <Select placeholder="选择工作内容" style={{ width: 150 }}>
                        {workItems.map(workItem => (
                          <Option key={workItem.id} value={workItem.id}>
                            {workItem.name} (¥{workItem.unit_price}/{workItem.unit})
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'quantity']}
                      rules={[{ required: true, message: '请输入数量' }]}
                    >
                      <InputNumber placeholder="数量" min={0.01} step={0.01} />
                    </Form.Item>
                    <DeleteOutlined onClick={() => remove(name)} />
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    添加工作内容
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={submitting} block>
              提交回单
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default MobileTaskComplete;
