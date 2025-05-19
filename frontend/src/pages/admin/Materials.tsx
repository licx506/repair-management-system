import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select,
  Space, Modal, Form, message, Popconfirm, InputNumber
} from 'antd';
import {
  PlusOutlined, SearchOutlined,
  EditOutlined, DeleteOutlined
} from '@ant-design/icons';
import {
  getMaterials, createMaterial, updateMaterial, deleteMaterial
} from '../../api/materials';
import type { Material, MaterialCreateParams, MaterialUpdateParams } from '../../api/materials';

const { Option } = Select;

const Materials: React.FC = () => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建材料');
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const response = await getMaterials();
      setMaterials(response);
    } catch (error) {
      console.error('Failed to fetch materials:', error);
      message.error('获取材料列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMaterial = () => {
    setModalTitle('新建材料');
    setEditingMaterial(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditMaterial = (material: Material) => {
    setModalTitle('编辑材料');
    setEditingMaterial(material);
    form.setFieldsValue({
      name: material.name,
      description: material.description,
      unit: material.unit,
      unit_price: material.unit_price,
      is_active: material.is_active
    });
    setModalVisible(true);
  };

  const handleDeleteMaterial = async (id: number) => {
    try {
      await deleteMaterial(id);
      message.success('删除材料成功');
      fetchMaterials();
    } catch (error) {
      console.error('Failed to delete material:', error);
      message.error('删除材料失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingMaterial) {
        // 更新材料
        await updateMaterial(editingMaterial.id, values as MaterialUpdateParams);
        message.success('更新材料成功');
      } else {
        // 创建材料
        await createMaterial(values as MaterialCreateParams);
        message.success('创建材料成功');
      }

      setModalVisible(false);
      fetchMaterials();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const filteredMaterials = materials.filter(material => {
    const matchesSearch =
      material.name.toLowerCase().includes(searchText.toLowerCase()) ||
      (material.description && material.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = statusFilter === undefined || material.is_active === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      title: '材料ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '材料名称',
      dataIndex: 'name',
      key: 'name',
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
    },
    {
      title: '单价(元)',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        active ? <span style={{ color: '#52c41a' }}>启用</span> : <span style={{ color: '#ff4d4f' }}>禁用</span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Material) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditMaterial(record)}
          />
          <Popconfirm
            title="确定要删除这个材料吗？"
            onConfirm={() => handleDeleteMaterial(record.id)}
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
        title="材料管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateMaterial}
          >
            新建材料
          </Button>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索材料"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Select
            placeholder="状态筛选"
            style={{ width: 120 }}
            allowClear
            value={statusFilter}
            onChange={value => setStatusFilter(value)}
          >
            <Option value={true}>启用</Option>
            <Option value={false}>禁用</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredMaterials.map(material => ({ ...material, key: material.id }))}
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
            name="name"
            label="材料名称"
            rules={[{ required: true, message: '请输入材料名称' }]}
          >
            <Input placeholder="请输入材料名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="材料描述"
          >
            <Input.TextArea placeholder="请输入材料描述" rows={4} />
          </Form.Item>
          <Form.Item
            name="unit"
            label="计量单位"
            rules={[{ required: true, message: '请输入计量单位' }]}
          >
            <Input placeholder="请输入计量单位，如：个、米、kg等" />
          </Form.Item>
          <Form.Item
            name="unit_price"
            label="单价(元)"
            rules={[{ required: true, message: '请输入单价' }]}
          >
            <InputNumber
              min={0}
              precision={2}
              style={{ width: '100%' }}
              placeholder="请输入单价"
            />
          </Form.Item>
          {editingMaterial && (
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

export default Materials;
