import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Button, Spin, message, Form, Divider,
  Select, InputNumber, Switch, Space, Typography, Row, Col,
  Table, Upload, Modal
} from 'antd';
import {
  ArrowLeftOutlined, PlusOutlined, DeleteOutlined,
  ImportOutlined, UploadOutlined, InboxOutlined
} from '@ant-design/icons';
import { getTask, completeTask } from '../../api/tasks';
import type { TaskDetail, TaskCompleteParams } from '../../api/tasks';
import { getMaterials } from '../../api/materials';
import type { Material } from '../../api/materials';
import { getWorkItems } from '../../api/work-items';
import type { WorkItem } from '../../api/work-items';
import { getApiBaseUrl } from '../../utils/config';
import ImportModal from '../../components/ImportModal';

const { Title, Text } = Typography;
const { Option } = Select;

const PCTaskComplete: React.FC = () => {
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

  // 批量导入相关状态
  const [workItemsImportModalVisible, setWorkItemsImportModalVisible] = useState(false);
  const [materialsImportModalVisible, setMaterialsImportModalVisible] = useState(false);
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
              const itemCost = workItem.unit_price * item.quantity;
              newLaborCost += itemCost;

              // 调试信息
              console.log(`工作内容: ${workItem.name}, 单价: ${workItem.unit_price}, 数量: ${item.quantity}, 小计: ${itemCost}`);
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

              // 调试信息
              console.log(`材料: ${material.name}, 单价: ${material.unit_price}, 数量: ${item.quantity}, 小计: ${cost}, 类型: ${item.is_company_provided ? '甲供' : '自购'}`);

              if (item.is_company_provided) {
                newCompanyMaterialCost += cost;
              } else {
                newSelfMaterialCost += cost;
              }
            }
          }
        });
      }

      // 更新状态
      setLaborCost(newLaborCost);
      setCompanyMaterialCost(newCompanyMaterialCost);
      setSelfMaterialCost(newSelfMaterialCost);
      setTotalCost(newLaborCost + newCompanyMaterialCost + newSelfMaterialCost);

      // 调试信息
      console.log(`费用统计 - 施工费: ${newLaborCost}, 甲供材料费: ${newCompanyMaterialCost}, 自购材料费: ${newSelfMaterialCost}, 总费用: ${newLaborCost + newCompanyMaterialCost + newSelfMaterialCost}`);
    } catch (error) {
      console.error('计算费用失败:', error);
    }
  };

  // 当表单值变化时重新计算费用
  useEffect(() => {
    calculateCosts();
  }, [form.getFieldsValue()]);

  // 处理工作内容批量导入模态框打开
  const handleWorkItemsImportModalOpen = () => {
    if (!id) return;
    setWorkItemsImportModalVisible(true);
  };

  // 处理工作内容批量导入模态框关闭
  const handleWorkItemsImportModalClose = () => {
    setWorkItemsImportModalVisible(false);
  };

  // 处理工作内容批量导入成功
  const handleWorkItemsImportSuccess = () => {
    message.success('工作内容批量导入成功');
    setWorkItemsImportModalVisible(false);
    // 重新获取工单数据
    if (id) {
      getTask(parseInt(id)).then(response => {
        setTask(response);
        // 更新表单中的工作内容
        if (response.work_items && response.work_items.length > 0) {
          form.setFieldsValue({ work_items: response.work_items });
          calculateCosts();
        }
      });
    }
  };

  // 处理材料批量导入模态框打开
  const handleMaterialsImportModalOpen = () => {
    if (!id) return;
    setMaterialsImportModalVisible(true);
  };

  // 处理材料批量导入模态框关闭
  const handleMaterialsImportModalClose = () => {
    setMaterialsImportModalVisible(false);
  };

  // 处理材料批量导入成功
  const handleMaterialsImportSuccess = () => {
    message.success('材料批量导入成功');
    setMaterialsImportModalVisible(false);
    // 重新获取工单数据
    if (id) {
      getTask(parseInt(id)).then(response => {
        setTask(response);
        // 更新表单中的材料
        if (response.materials && response.materials.length > 0) {
          form.setFieldsValue({ materials: response.materials });
          calculateCosts();
        }
      });
    }
  };

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
      navigate(`/pc/tasks/${id}`);
    } catch (error) {
      console.error('Failed to complete task:', error);
      message.error('回单失败');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 'calc(100vh - 64px)' }}>
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

      <Card title="工单回单">
        <Title level={4}>{task.title}</Title>
        <p>{task.description || '无描述'}</p>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            materials: [{ category: undefined, material_id: undefined, quantity: 1, is_company_provided: false }],
            work_items: [{ category: undefined, work_item_id: undefined, quantity: 1 }]
          }}
          onValuesChange={calculateCosts}
        >
          <Divider orientation="left">
            <Space>
              工作内容
              <Button
                type="primary"
                size="small"
                icon={<ImportOutlined />}
                onClick={handleWorkItemsImportModalOpen}
              >
                批量导入
              </Button>
            </Space>
          </Divider>

          {/* 工作内容列标题 */}
          <Row gutter={16} style={{ background: '#f5f5f5', padding: '8px 0', fontWeight: 'bold', marginBottom: 16 }}>
            <Col span={4}><Text>项目分类</Text></Col>
            <Col span={4}><Text>编号</Text></Col>
            <Col span={6}><Text>工作内容</Text></Col>
            <Col span={3}><Text>单价</Text></Col>
            <Col span={2}><Text>单位</Text></Col>
            <Col span={3}><Text>数量</Text></Col>
            <Col span={2}><Text>金额</Text></Col>
          </Row>

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

                  // 获取分类
                  const category = workItem?.category || '';

                  // 根据分类筛选工作内容
                  const filteredWorkItems = category
                    ? workItems.filter(item => item.category === category)
                    : workItems;

                  return (
                    <Row key={key} gutter={16} style={{ marginBottom: 8 }} align="middle">
                      <Col span={4}>
                        <Form.Item
                          {...restField}
                          name={[name, 'category']}
                          rules={[{ required: true, message: '请选择项目分类' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Select
                            placeholder="选择项目分类"
                            style={{ width: '100%' }}
                            onChange={() => {
                              // 当分类变化时，清空工作内容选择
                              const fields = form.getFieldsValue();
                              const workItems = fields.work_items || [];
                              workItems[name].work_item_id = undefined;
                              form.setFieldsValue({ work_items: workItems });
                              calculateCosts();
                            }}
                          >
                            {workItemCategories.map(cat => (
                              <Option key={cat} value={cat}>
                                {cat}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      <Col span={4}>
                        <Text>{workItem?.project_number || '-'}</Text>
                      </Col>
                      <Col span={6}>
                        <Form.Item
                          {...restField}
                          name={[name, 'work_item_id']}
                          rules={[{ required: true, message: '请选择工作内容' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Select
                            placeholder="选择工作内容"
                            style={{ width: '100%' }}
                            onChange={() => calculateCosts()}
                            disabled={!category}
                          >
                            {filteredWorkItems.map(workItem => (
                              <Option key={workItem.id} value={workItem.id}>
                                {workItem.name}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      <Col span={3}>
                        <Text>¥{workItem?.unit_price?.toFixed(2) || '0.00'}</Text>
                      </Col>
                      <Col span={2}>
                        <Text>{workItem?.unit || '-'}</Text>
                      </Col>
                      <Col span={3}>
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
                      <Col span={2}>
                        <Text>¥{amount.toFixed(2)}</Text>
                      </Col>
                      <Col span={1}>
                        <DeleteOutlined onClick={() => {
                          remove(name);
                          setTimeout(calculateCosts, 0);
                        }} />
                      </Col>
                    </Row>
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

          <Divider orientation="left">
            <Space>
              使用材料
              <Button
                type="primary"
                size="small"
                icon={<ImportOutlined />}
                onClick={handleMaterialsImportModalOpen}
              >
                批量导入
              </Button>
            </Space>
          </Divider>

          {/* 材料清单列标题 */}
          <Row gutter={16} style={{ background: '#f5f5f5', padding: '8px 0', fontWeight: 'bold', marginBottom: 16 }}>
            <Col span={3}><Text>分类</Text></Col>
            <Col span={3}><Text>编号</Text></Col>
            <Col span={4}><Text>名称</Text></Col>
            <Col span={3}><Text>描述</Text></Col>
            <Col span={2}><Text>单价</Text></Col>
            <Col span={2}><Text>单位</Text></Col>
            <Col span={2}><Text>数量</Text></Col>
            <Col span={2}><Text>金额</Text></Col>
            <Col span={3}><Text>供应方式</Text></Col>
          </Row>

          <Form.List name="materials">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => {
                  // 获取当前行的材料ID和数量
                  const materialId = form.getFieldValue(['materials', name, 'material_id']);
                  const quantity = form.getFieldValue(['materials', name, 'quantity']) || 0;

                  // 查找材料详情
                  const material = materials.find(item => item.id === materialId);

                  // 计算金额
                  const amount = material ? material.unit_price * quantity : 0;

                  // 获取分类
                  const category = material?.category || '';

                  // 根据分类筛选材料
                  const filteredMaterials = category
                    ? materials.filter(item => item.category === category)
                    : materials;

                  return (
                    <Row key={key} gutter={16} style={{ marginBottom: 8 }} align="middle">
                      <Col span={3}>
                        <Form.Item
                          {...restField}
                          name={[name, 'category']}
                          rules={[{ required: true, message: '请选择分类' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Select
                            placeholder="选择分类"
                            style={{ width: '100%' }}
                            onChange={() => {
                              // 当分类变化时，清空材料选择
                              const fields = form.getFieldsValue();
                              const materials = fields.materials || [];
                              materials[name].material_id = undefined;
                              form.setFieldsValue({ materials: materials });
                              calculateCosts();
                            }}
                          >
                            {materialCategories.map(cat => (
                              <Option key={cat} value={cat}>
                                {cat}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      <Col span={3}>
                        <Text>{material?.code || '-'}</Text>
                      </Col>
                      <Col span={4}>
                        <Form.Item
                          {...restField}
                          name={[name, 'material_id']}
                          rules={[{ required: true, message: '请选择材料' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Select
                            placeholder="选择材料"
                            style={{ width: '100%' }}
                            onChange={() => calculateCosts()}
                            disabled={!category}
                          >
                            {filteredMaterials.map(material => (
                              <Option key={material.id} value={material.id}>
                                {material.name}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      <Col span={3}>
                        <Text>{material?.description || '-'}</Text>
                      </Col>
                      <Col span={2}>
                        <Text>¥{material?.unit_price?.toFixed(2) || '0.00'}</Text>
                      </Col>
                      <Col span={2}>
                        <Text>{material?.unit || '-'}</Text>
                      </Col>
                      <Col span={2}>
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
                      <Col span={2}>
                        <Text>¥{amount.toFixed(2)}</Text>
                      </Col>
                      <Col span={3}>
                        <Form.Item
                          {...restField}
                          name={[name, 'is_company_provided']}
                          valuePropName="checked"
                          initialValue={false}
                          style={{ marginBottom: 0 }}
                        >
                          <Switch
                            checkedChildren="甲供"
                            unCheckedChildren="自购"
                            onChange={() => calculateCosts()}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={1}>
                        <DeleteOutlined onClick={() => {
                          remove(name);
                          setTimeout(calculateCosts, 0);
                        }} />
                      </Col>
                    </Row>
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

          <Divider orientation="left">费用统计</Divider>
          <Row gutter={16}>
            <Col span={6}>
              <Card
                size="small"
                title="施工费"
                style={{
                  background: '#f6ffed',
                  borderColor: '#b7eb8f'
                }}
              >
                <div style={{ fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{laborCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card
                size="small"
                title="甲供材料费"
                style={{
                  background: '#e6f7ff',
                  borderColor: '#91d5ff'
                }}
              >
                <div style={{ fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{companyMaterialCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card
                size="small"
                title="自购材料费"
                style={{
                  background: '#fff7e6',
                  borderColor: '#ffd591'
                }}
              >
                <div style={{ fontSize: '16px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{selfMaterialCost.toFixed(2)}
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card
                size="small"
                title="总费用"
                style={{
                  background: '#fff1f0',
                  borderColor: '#ffa39e'
                }}
              >
                <div style={{ fontSize: '18px', fontWeight: 'bold', textAlign: 'center' }}>
                  ¥{totalCost.toFixed(2)}
                </div>
              </Card>
            </Col>
          </Row>

          <Form.Item style={{ marginTop: 24 }}>
            <Button type="primary" htmlType="submit" loading={submitting} size="large">
              提交回单
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 批量导入工作内容模态框 */}
      {id && (
        <ImportModal
          visible={workItemsImportModalVisible}
          title="批量导入工作内容"
          endpoint={`/api/tasks/${id}/work-items/import`}
          templateUrl={`${getApiBaseUrl()}/templates/task_work_items_template.csv`}
          onClose={handleWorkItemsImportModalClose}
          onSuccess={handleWorkItemsImportSuccess}
          acceptedFileTypes=".csv"
          helpText="请上传CSV格式的工作内容数据，包含编号和数量两列。"
        />
      )}

      {/* 批量导入材料模态框 */}
      {id && (
        <ImportModal
          visible={materialsImportModalVisible}
          title="批量导入材料"
          endpoint={`/api/tasks/${id}/materials/import`}
          templateUrl={`${getApiBaseUrl()}/templates/task_materials_template.csv`}
          onClose={handleMaterialsImportModalClose}
          onSuccess={handleMaterialsImportSuccess}
          acceptedFileTypes=".csv"
          helpText="请上传CSV格式的材料数据，包含编号、数量和是否甲供三列。"
        />
      )}
    </div>
  );
};

export default PCTaskComplete;
