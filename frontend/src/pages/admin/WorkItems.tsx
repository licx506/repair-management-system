import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select,
  Space, Modal, Form, message, Popconfirm, InputNumber, Tag, Dropdown
} from 'antd';
import {
  PlusOutlined, SearchOutlined,
  EditOutlined, DeleteOutlined, FilterOutlined,
  UploadOutlined, DownloadOutlined, MenuOutlined
} from '@ant-design/icons';
import {
  getWorkItems, createWorkItem, updateWorkItem, deleteWorkItem, getWorkItemCategories
} from '../../api/work-items';
import type { WorkItem, WorkItemCreateParams, WorkItemUpdateParams } from '../../api/work-items';
import ImportModal from '../../components/ImportModal';
import { getTemplateBaseUrl } from '../../utils/config';

const { Option } = Select;

const WorkItems: React.FC = () => {
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建工作内容');
  const [editingWorkItem, setEditingWorkItem] = useState<WorkItem | null>(null);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchWorkItems();
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await getWorkItemCategories();
      setCategories(response);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      message.error('获取工作内容分类失败');
    }
  };

  const fetchWorkItems = async () => {
    setLoading(true);
    console.log('开始获取工作内容列表，参数:', {
      category: categoryFilter,
      is_active: statusFilter
    });

    try {
      // 添加重试逻辑
      let retries = 3;
      let response;

      while (retries > 0) {
        try {
          response = await getWorkItems({
            category: categoryFilter,
            is_active: statusFilter
          });
          break; // 如果成功，跳出循环
        } catch (retryError: any) {
          retries--;
          if (retries === 0) {
            throw retryError; // 重试次数用完，抛出错误
          }
          console.warn(`获取工作内容列表失败，剩余重试次数: ${retries}`);
          await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
        }
      }

      console.log('获取工作内容列表成功:', response);

      if (Array.isArray(response)) {
        setWorkItems(response);
        console.log(`设置工作内容列表，共 ${response.length} 条数据`);

        // 如果列表为空，显示提示
        if (response.length === 0) {
          message.info('工作内容列表为空，可以添加新的工作内容');
        }
      } else {
        console.error('获取工作内容列表返回格式错误，期望数组但收到:', response);
        setWorkItems([]);
        message.error('获取工作内容列表格式错误');
      }
    } catch (error: any) {
      console.error('获取工作内容列表失败:', error);

      // 详细记录错误信息
      if (error.response) {
        console.error('错误响应:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      } else {
        console.error('网络错误:', {
          message: error.message,
          code: error.code,
          stack: error.stack
        });
      }

      if (error.code === 'ERR_NETWORK') {
        message.error('网络连接错误，请检查服务器是否可用');
      } else if (error.response && error.response.data && error.response.data.detail) {
        message.error(`获取工作内容列表失败: ${error.response.data.detail}`);
      } else {
        message.error('获取工作内容列表失败，请刷新页面重试');
      }

      // 设置空数组，避免页面崩溃
      setWorkItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkItem = () => {
    setModalTitle('新建工作内容');
    setEditingWorkItem(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditWorkItem = (workItem: WorkItem) => {
    setModalTitle('编辑工作内容');
    setEditingWorkItem(workItem);
    form.setFieldsValue({
      category: workItem.category,
      project_number: workItem.project_number,
      name: workItem.name,
      description: workItem.description,
      unit: workItem.unit,
      skilled_labor_days: workItem.skilled_labor_days,
      unskilled_labor_days: workItem.unskilled_labor_days,
      unit_price: workItem.unit_price,
      is_active: workItem.is_active
    });
    setModalVisible(true);
  };

  const handleDeleteWorkItem = async (id: number) => {
    try {
      await deleteWorkItem(id);
      message.success('删除工作内容成功');
      fetchWorkItems();
    } catch (error) {
      console.error('Failed to delete work item:', error);
      message.error('删除工作内容失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      // 确保数值字段有默认值
      const formattedValues = {
        ...values,
        skilled_labor_days: values.skilled_labor_days !== undefined ? values.skilled_labor_days : 0,
        unskilled_labor_days: values.unskilled_labor_days !== undefined ? values.unskilled_labor_days : 0,
        unit_price: values.unit_price !== undefined ? values.unit_price : 0
      };

      if (editingWorkItem) {
        // 更新工作内容
        try {
          await updateWorkItem(editingWorkItem.id, formattedValues as WorkItemUpdateParams);
          message.success('更新工作内容成功');
          setModalVisible(false);
          fetchWorkItems();
        } catch (error: any) {
          console.error('更新工作内容失败:', error);
          if (error.response && error.response.data) {
            message.error(`更新工作内容失败: ${error.response.data}`);
          } else {
            message.error('更新工作内容失败，请检查输入是否正确');
          }
        }
      } else {
        // 创建工作内容
        try {
          console.log('准备创建工作内容，数据:', formattedValues);
          const result = await createWorkItem(formattedValues as WorkItemCreateParams);
          console.log('创建工作内容成功，返回结果:', result);
          message.success('创建工作内容成功');
          setModalVisible(false);
          fetchWorkItems();
        } catch (error: any) {
          console.error('创建工作内容失败:', error);

          // 详细记录错误信息
          if (error.response) {
            console.error('错误响应详情:', {
              status: error.response.status,
              data: error.response.data,
              headers: error.response.headers
            });
          } else {
            console.error('网络错误详情:', {
              message: error.message,
              code: error.code,
              stack: error.stack
            });
          }

          if (error.code === 'ERR_NETWORK') {
            message.error('网络连接错误，请检查服务器是否可用');
          } else if (error.response && error.response.status === 400) {
            message.error(`创建工作内容失败: ${error.response.data.detail || '项目编号可能已存在'}`);
          } else if (error.response && error.response.status >= 500) {
            message.error('服务器内部错误，请联系管理员');
          } else if (error.response && error.response.data) {
            message.error(`创建工作内容失败: ${error.response.data.detail || error.response.data}`);
          } else {
            message.error('创建工作内容失败，请检查输入是否正确');
          }
        }
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const filteredWorkItems = workItems.filter(workItem => {
    const matchesSearch =
      workItem.name.toLowerCase().includes(searchText.toLowerCase()) ||
      workItem.project_number.toLowerCase().includes(searchText.toLowerCase()) ||
      (workItem.description && workItem.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesCategory = categoryFilter === undefined || workItem.category === categoryFilter;
    const matchesStatus = statusFilter === undefined || workItem.is_active === statusFilter;

    return matchesSearch && matchesCategory && matchesStatus;
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '项目分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) => (
        <Tag color="blue">{category}</Tag>
      ),
    },
    {
      title: '项目编号',
      dataIndex: 'project_number',
      key: 'project_number',
      width: 120,
    },
    {
      title: '工作内容名称',
      dataIndex: 'name',
      key: 'name',
      width: 180,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '单位',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: '技工工日',
      dataIndex: 'skilled_labor_days',
      key: 'skilled_labor_days',
      width: 100,
      render: (days: number) => days.toFixed(1),
    },
    {
      title: '普工工日',
      dataIndex: 'unskilled_labor_days',
      key: 'unskilled_labor_days',
      width: 100,
      render: (days: number) => days.toFixed(1),
    },
    {
      title: '单价(元)',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active: boolean) => (
        active ? <span style={{ color: '#52c41a' }}>启用</span> : <span style={{ color: '#ff4d4f' }}>禁用</span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: WorkItem) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditWorkItem(record)}
          />
          <Popconfirm
            title="确定要删除这个工作内容吗？"
            onConfirm={() => handleDeleteWorkItem(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 处理导入模态框
  const handleImportModalOpen = () => {
    setImportModalVisible(true);
  };

  const handleImportModalClose = () => {
    setImportModalVisible(false);
  };

  const handleImportSuccess = () => {
    message.success('工作内容导入成功');
    fetchWorkItems();
  };

  // 导入说明文本
  const importHelpText = (
    <div>
      <p>请按照以下格式准备CSV文件：</p>
      <p>1. 必须包含以下列：category(分类), project_number(项目编号), name(名称), unit(单位), unit_price(单价)</p>
      <p>2. 可选列：description(描述), skilled_labor_days(技工工日), unskilled_labor_days(普工工日)</p>
      <p>3. 项目编号必须唯一，否则导入将失败</p>
    </div>
  );

  // 下拉菜单项
  const actionItems = [
    {
      key: 'import',
      label: '批量导入',
      icon: <UploadOutlined />,
      onClick: handleImportModalOpen
    },
    {
      key: 'download-template',
      label: '下载模板',
      icon: <DownloadOutlined />,
      onClick: () => window.open(`${getTemplateBaseUrl()}/templates/work_items_template.csv`)
    }
  ];

  return (
    <div>
      <Card
        title="工作内容管理"
        extra={
          <Space>
            <Dropdown menu={{ items: actionItems }}>
              <Button icon={<MenuOutlined />}>
                批量操作
              </Button>
            </Dropdown>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateWorkItem}
            >
              新建工作内容
            </Button>
          </Space>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索工作内容"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Select
            placeholder="项目分类"
            style={{ width: 150 }}
            allowClear
            value={categoryFilter}
            onChange={value => {
              setCategoryFilter(value);
              fetchWorkItems();
            }}
          >
            {categories.map(category => (
              <Option key={category} value={category}>{category}</Option>
            ))}
          </Select>
          <Select
            placeholder="状态筛选"
            style={{ width: 120 }}
            allowClear
            value={statusFilter}
            onChange={value => {
              setStatusFilter(value);
              fetchWorkItems();
            }}
          >
            <Option value={true}>启用</Option>
            <Option value={false}>禁用</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredWorkItems.map(workItem => ({ ...workItem, key: workItem.id }))}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="category"
            label="项目分类"
            rules={[{ required: true, message: '请选择项目分类' }]}
          >
            <Select placeholder="请选择项目分类">
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="project_number"
            label="项目编号"
            rules={[
              { required: true, message: '请输入项目编号' },
              { max: 20, message: '项目编号最多20个字符' }
            ]}
          >
            <Input placeholder="请输入项目编号" />
          </Form.Item>
          <Form.Item
            name="name"
            label="工作内容名称"
            rules={[
              { required: true, message: '请输入工作内容名称' },
              { max: 50, message: '工作内容名称最多50个字符' }
            ]}
          >
            <Input placeholder="请输入工作内容名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="工作内容描述"
          >
            <Input.TextArea placeholder="请输入工作内容描述" rows={4} />
          </Form.Item>
          <Form.Item
            name="unit"
            label="计量单位"
            rules={[
              { required: true, message: '请输入计量单位' },
              { max: 20, message: '计量单位最多20个字符' }
            ]}
          >
            <Input placeholder="请输入计量单位，如：次、小时、平方米等" />
          </Form.Item>

          <div style={{ display: 'flex', gap: '16px' }}>
            <Form.Item
              name="skilled_labor_days"
              label="技工工日"
              style={{ flex: 1 }}
              initialValue={0}
              rules={[
                { type: 'number', min: 0, message: '技工工日必须大于等于0' }
              ]}
            >
              <InputNumber
                min={0}
                precision={1}
                style={{ width: '100%' }}
                placeholder="请输入技工工日"
              />
            </Form.Item>

            <Form.Item
              name="unskilled_labor_days"
              label="普工工日"
              style={{ flex: 1 }}
              initialValue={0}
              rules={[
                { type: 'number', min: 0, message: '普工工日必须大于等于0' }
              ]}
            >
              <InputNumber
                min={0}
                precision={1}
                style={{ width: '100%' }}
                placeholder="请输入普工工日"
              />
            </Form.Item>
          </div>

          <Form.Item
            name="unit_price"
            label="单价(元)"
            rules={[
              { required: true, message: '请输入单价' },
              { type: 'number', min: 0, message: '单价必须大于等于0' }
            ]}
          >
            <InputNumber
              min={0}
              precision={2}
              style={{ width: '100%' }}
              placeholder="请输入单价"
            />
          </Form.Item>
          {editingWorkItem && (
            <Form.Item
              name="is_active"
              label="状态"
              initialValue={true}
            >
              <Select>
                <Option value={true}>启用</Option>
                <Option value={false}>禁用</Option>
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* 批量导入模态框 */}
      <ImportModal
        visible={importModalVisible}
        title="批量导入工作内容"
        endpoint="/api/work-items/import"
        templateUrl={`${getTemplateBaseUrl()}/templates/work_items_template.csv`}
        onClose={handleImportModalClose}
        onSuccess={handleImportSuccess}
        acceptedFileTypes=".csv"
        helpText={importHelpText}
      />
    </div>
  );
};

export default WorkItems;
