import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Button, Spin, message, Form, Divider,
  Select, InputNumber, Switch, Space, Typography, Row, Col
} from 'antd';
import {
  ArrowLeftOutlined, PlusOutlined, DeleteOutlined
} from '@ant-design/icons';
import { getTask, completeTask } from '../../api/tasks';
import type { TaskDetail, TaskCompleteParams } from '../../api/tasks';
import { getMaterials } from '../../api/materials';
import type { Material } from '../../api/materials';
import { getWorkItems } from '../../api/work-items';
import type { WorkItem } from '../../api/work-items';


const { Title, Text } = Typography;
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

  // 用于计算总费用
  const [laborCost, setLaborCost] = useState<number>(0);
  const [companyMaterialCost, setCompanyMaterialCost] = useState<number>(0);
  const [selfMaterialCost, setSelfMaterialCost] = useState<number>(0);
  const [totalCost, setTotalCost] = useState<number>(0);

  // 分类相关状态
  const [workItemCategories, setWorkItemCategories] = useState<string[]>([]);
  const [materialCategories, setMaterialCategories] = useState<string[]>([]);

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

        // 提取所有不重复的材料分类
        const materialCats = [...new Set(materialsResponse.map(item => item.category))];
        setMaterialCategories(materialCats);

        // 提取所有不重复的工作内容分类
        const workItemCats = [...new Set(workItemsResponse.map(item => item.category))];
        setWorkItemCategories(workItemCats);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        message.error('获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  // 监听表单变化，计算费用
  const calculateCosts = () => {
    try {
      const formValues = form.getFieldsValue();

      // 计算施工费
      let newLaborCost = 0;
      if (formValues.work_items && formValues.work_items.length > 0) {
        formValues.work_items.forEach((item: any) => {
          if (item && item.work_item_id && item.quantity) {
            const workItem = workItems.find(w => w.id === item.work_item_id);
            if (workItem) {
              newLaborCost += workItem.unit_price * item.quantity;
            }
          }
        });
      }

      // 计算材料费
      let newCompanyMaterialCost = 0;
      let newSelfMaterialCost = 0;

      if (formValues.materials && formValues.materials.length > 0) {
        formValues.materials.forEach((item: any) => {
          if (item && item.material_id && item.quantity) {
            const material = materials.find(m => m.id === item.material_id);
            if (material) {
              const cost = material.unit_price * item.quantity;
              if (item.is_company_provided) {
                newCompanyMaterialCost += cost;
              } else {
                newSelfMaterialCost += cost;
              }
            }
          }
        });
      }

      setLaborCost(newLaborCost);
      setCompanyMaterialCost(newCompanyMaterialCost);
      setSelfMaterialCost(newSelfMaterialCost);
      setTotalCost(newLaborCost + newCompanyMaterialCost + newSelfMaterialCost);
    } catch (error) {
      console.error('计算费用失败:', error);
    }
  };

  // 当表单值变化时重新计算费用
  useEffect(() => {
    calculateCosts();
  }, [form.getFieldsValue()]);



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
          initialValues={{
            materials: [{ material_id: undefined, quantity: 1, is_company_provided: false }],
            work_items: [{ work_item_id: undefined, quantity: 1 }]
          }}
          onValuesChange={calculateCosts}
        >
          <Divider orientation="left">使用材料</Divider>

          {/* 材料清单列标题 - 移动端布局 */}
          <div style={{ background: '#f5f5f5', padding: '8px', fontWeight: 'bold', marginBottom: 8, fontSize: '12px' }}>
            <Row gutter={[8, 8]}>
              <Col span={8}><Text>名称/分类</Text></Col>
              <Col span={6}><Text>单价/单位</Text></Col>
              <Col span={5}><Text>数量</Text></Col>
              <Col span={5}><Text>供应方式</Text></Col>
            </Row>
          </div>

          <Form.List name="materials">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => {
                  // 获取当前行的材料ID、数量和供应方式
                  const materialId = form.getFieldValue(['materials', name, 'material_id']);
                  const quantity = form.getFieldValue(['materials', name, 'quantity']) || 0;
                  const isCompanyProvided = form.getFieldValue(['materials', name, 'is_company_provided']);

                  // 查找材料详情
                  const material = materials.find(item => item.id === materialId);

                  // 计算金额
                  const amount = material ? material.unit_price * quantity : 0;

                  return (
                    <div key={key} style={{ marginBottom: 16, padding: 8, border: '1px solid #f0f0f0', borderRadius: 4 }}>
                      <Row gutter={[8, 8]}>
                        <Col span={24}>
                          <Form.Item
                            {...restField}
                            name={[name, 'material_id']}
                            rules={[{ required: true, message: '请选择材料' }]}
                            style={{ marginBottom: 8 }}
                          >
                            <Select
                              placeholder="选择材料"
                              style={{ width: '100%' }}
                              onChange={() => calculateCosts()}
                            >
                              {materials.map(material => (
                                <Option key={material.id} value={material.id}>
                                  {material.name} ({material.category})
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                      </Row>

                      <Row gutter={[8, 8]} align="middle">
                        <Col span={8}>
                          <Text style={{ fontSize: '12px' }}>
                            单价: ¥{material?.unit_price?.toFixed(2) || '0.00'}/{material?.unit || '-'}
                          </Text>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            {...restField}
                            name={[name, 'quantity']}
                            rules={[{ required: true, message: '请输入数量' }]}
                            style={{ marginBottom: 0 }}
                          >
                            <InputNumber
                              placeholder="数量"
                              min={0.01}
                              step={0.01}
                              style={{ width: '100%' }}
                              onChange={() => calculateCosts()}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            {...restField}
                            name={[name, 'is_company_provided']}
                            valuePropName="checked"
                            style={{ marginBottom: 0 }}
                          >
                            <Switch
                              checkedChildren="甲供"
                              unCheckedChildren="自购"
                              onChange={() => calculateCosts()}
                            />
                          </Form.Item>
                        </Col>
                      </Row>

                      <Row gutter={[8, 8]} align="middle" style={{ marginTop: 8 }}>
                        <Col span={16}>
                          <Text style={{ fontSize: '12px' }}>金额: ¥{amount.toFixed(2)}</Text>
                        </Col>
                        <Col span={8} style={{ textAlign: 'right' }}>
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => {
                              remove(name);
                              setTimeout(calculateCosts, 0);
                            }}
                          >
                            删除
                          </Button>
                        </Col>
                      </Row>
                    </div>
                  );
                })}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    添加材料
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>

          <Divider orientation="left">工作内容</Divider>

          {/* 工作内容列标题 - 移动端布局 */}
          <div style={{ background: '#f5f5f5', padding: '8px', fontWeight: 'bold', marginBottom: 8, fontSize: '12px' }}>
            <Row gutter={[8, 8]}>
              <Col span={10}><Text>工作内容/分类</Text></Col>
              <Col span={7}><Text>单价/单位</Text></Col>
              <Col span={7}><Text>数量/金额</Text></Col>
            </Row>
          </div>

          <Form.List name="work_items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => {
                  // 获取当前行的工作内容ID和数量
                  const workItemId = form.getFieldValue(['work_items', name, 'work_item_id']);
                  const quantity = form.getFieldValue(['work_items', name, 'quantity']) || 0;

                  // 查找工作内容详情
                  const workItem = workItems.find(item => item.id === workItemId);

                  // 计算金额
                  const amount = workItem ? workItem.unit_price * quantity : 0;

                  return (
                    <div key={key} style={{ marginBottom: 16, padding: 8, border: '1px solid #f0f0f0', borderRadius: 4 }}>
                      <Row gutter={[8, 8]}>
                        <Col span={24}>
                          <Form.Item
                            {...restField}
                            name={[name, 'work_item_id']}
                            rules={[{ required: true, message: '请选择工作内容' }]}
                            style={{ marginBottom: 8 }}
                          >
                            <Select
                              placeholder="选择工作内容"
                              style={{ width: '100%' }}
                              onChange={() => calculateCosts()}
                            >
                              {workItems.map(workItem => (
                                <Option key={workItem.id} value={workItem.id}>
                                  {workItem.name} ({workItem.category})
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                      </Row>

                      <Row gutter={[8, 8]} align="middle">
                        <Col span={10}>
                          <Text style={{ fontSize: '12px' }}>
                            编号: {workItem?.project_number || '-'}
                          </Text>
                        </Col>
                        <Col span={7}>
                          <Text style={{ fontSize: '12px' }}>
                            ¥{workItem?.unit_price?.toFixed(2) || '0.00'}/{workItem?.unit || '-'}
                          </Text>
                        </Col>
                        <Col span={7}>
                          <Form.Item
                            {...restField}
                            name={[name, 'quantity']}
                            rules={[{ required: true, message: '请输入数量' }]}
                            style={{ marginBottom: 0 }}
                          >
                            <InputNumber
                              placeholder="数量"
                              min={0.01}
                              step={0.01}
                              style={{ width: '100%' }}
                              onChange={() => calculateCosts()}
                            />
                          </Form.Item>
                        </Col>
                      </Row>

                      <Row gutter={[8, 8]} align="middle" style={{ marginTop: 8 }}>
                        <Col span={16}>
                          <Text style={{ fontSize: '12px' }}>金额: ¥{amount.toFixed(2)}</Text>
                        </Col>
                        <Col span={8} style={{ textAlign: 'right' }}>
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => {
                              remove(name);
                              setTimeout(calculateCosts, 0);
                            }}
                          >
                            删除
                          </Button>
                        </Col>
                      </Row>
                    </div>
                  );
                })}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    添加工作内容
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>

          <Divider orientation="left">费用统计</Divider>
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card
                size="small"
                title="施工费"
                style={{
                  background: '#f6ffed',
                  borderColor: '#b7eb8f'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{laborCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title="甲供材料费"
                style={{
                  background: '#e6f7ff',
                  borderColor: '#91d5ff'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{companyMaterialCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title="自购材料费"
                style={{
                  background: '#fff7e6',
                  borderColor: '#ffd591'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{selfMaterialCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title="总费用"
                style={{
                  background: '#fff1f0',
                  borderColor: '#ffa39e'
                }}
              >
                <div style={{ fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{totalCost.toFixed(2)}
                </div>
              </Card>
            </Col>
          </Row>

          <Form.Item style={{ marginTop: 24 }}>
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
