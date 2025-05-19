import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select,
  Space, Modal, Form, message, Popconfirm, InputNumber, Tag
} from 'antd';
import {
  PlusOutlined, SearchOutlined,
  EditOutlined, DeleteOutlined, FilterOutlined
} from '@ant-design/icons';
import {
  getWorkItems, createWorkItem, updateWorkItem, deleteWorkItem, getWorkItemCategories
} from '../../api/work-items';
import type { WorkItem, WorkItemCreateParams, WorkItemUpdateParams } from '../../api/work-items';

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
    try {
      const response = await getWorkItems({
        category: categoryFilter,
        is_active: statusFilter
      });
      setWorkItems(response);
    } catch (error) {
      console.error('Failed to fetch work items:', error);
      message.error('获取工作内容列表失败');
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

      if (editingWorkItem) {
        // 更新工作内容
        await updateWorkItem(editingWorkItem.id, values as WorkItemUpdateParams);
        message.success('更新工作内容成功');
      } else {
        // 创建工作内容
        await createWorkItem(values as WorkItemCreateParams);
        message.success('创建工作内容成功');
      }

      setModalVisible(false);
      fetchWorkItems();
    } catch (error) {
      console.error('Form validation failed:', error);
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

  return (
    <div>
      <Card
        title="工作内容管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateWorkItem}
          >
            新建工作内容
          </Button>
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
    </div>
  );
};

export default WorkItems;
