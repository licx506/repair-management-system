import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Select, Tag,
  Space, Modal, Form, message, Popconfirm, InputNumber, Dropdown
} from 'antd';
import {
  PlusOutlined, SearchOutlined, FilterOutlined,
  EditOutlined, DeleteOutlined, UploadOutlined,
  DownloadOutlined, MenuOutlined
} from '@ant-design/icons';
import {
  getMaterials, createMaterial, updateMaterial, deleteMaterial,
  getMaterialCategories, getMaterialSupplyTypes
} from '../../api/materials';
import type { Material, MaterialCreateParams, MaterialUpdateParams } from '../../api/materials';
import ImportModal from '../../components/ImportModal';

const { Option } = Select;

const Materials: React.FC = () => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [supplyTypes, setSupplyTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>(undefined);
  const [supplyTypeFilter, setSupplyTypeFilter] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建材料');
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchMaterials();
    fetchCategories();
    fetchSupplyTypes();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await getMaterialCategories();
      setCategories(response);
    } catch (error) {
      console.error('获取材料分类失败:', error);
      message.error('获取材料分类失败');
    }
  };

  const fetchSupplyTypes = async () => {
    try {
      const response = await getMaterialSupplyTypes();
      setSupplyTypes(response);
    } catch (error) {
      console.error('获取供应类型失败:', error);
      message.error('获取供应类型失败');
    }
  };

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const response = await getMaterials({
        category: categoryFilter,
        supply_type: supplyTypeFilter,
        is_active: statusFilter
      });
      setMaterials(response);
    } catch (error) {
      console.error('获取材料列表失败:', error);
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
      category: material.category,
      code: material.code,
      name: material.name,
      description: material.description,
      unit: material.unit,
      unit_price: material.unit_price,
      supply_type: material.supply_type,
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

      // 确保数值字段有默认值，并设置默认的供应类型
      const formattedValues = {
        ...values,
        unit_price: values.unit_price || 0,
        supply_type: values.supply_type || '两者皆可'
      };

      if (editingMaterial) {
        // 更新材料
        await updateMaterial(editingMaterial.id, formattedValues as MaterialUpdateParams);
        message.success('更新材料成功');
      } else {
        // 创建材料
        try {
          await createMaterial(formattedValues as MaterialCreateParams);
          message.success('创建材料成功');
        } catch (error: any) {
          console.error('创建材料失败:', error);
          if (error.response && error.response.data) {
            message.error(`创建材料失败: ${error.response.data}`);
          } else {
            message.error('创建材料失败，请检查材料编号是否重复');
          }
          return; // 创建失败时不关闭模态框
        }
      }

      setModalVisible(false);
      fetchMaterials();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const filteredMaterials = materials.filter(material => {
    const matchesSearch =
      material.name.toLowerCase().includes(searchText.toLowerCase()) ||
      material.code.toLowerCase().includes(searchText.toLowerCase()) ||
      (material.description && material.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesCategory = categoryFilter === undefined || material.category === categoryFilter;
    const matchesSupplyType = supplyTypeFilter === undefined || material.supply_type === supplyTypeFilter;
    const matchesStatus = statusFilter === undefined || material.is_active === statusFilter;

    return matchesSearch && matchesCategory && matchesSupplyType && matchesStatus;
  });

  const columns = [
    {
      title: '材料ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (category: string) => (
        <Tag color="blue">{category}</Tag>
      ),
    },
    {
      title: '编号',
      dataIndex: 'code',
      key: 'code',
      width: 100,
    },
    {
      title: '材料名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
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
      title: '供应类型',
      dataIndex: 'supply_type',
      key: 'supply_type',
      width: 100,
      render: (type: string) => {
        let color = 'default';
        if (type === '甲供') color = 'green';
        else if (type === '自购') color = 'orange';
        else if (type === '两者皆可') color = 'blue';
        return <Tag color={color}>{type}</Tag>;
      },
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

  // 处理导入模态框
  const handleImportModalOpen = () => {
    setImportModalVisible(true);
  };

  const handleImportModalClose = () => {
    setImportModalVisible(false);
  };

  const handleImportSuccess = () => {
    message.success('材料导入成功');
    fetchMaterials();
  };

  // 导入说明文本
  const importHelpText = (
    <div>
      <p>请按照以下格式准备CSV文件：</p>
      <p>1. 必须包含以下列：category(分类), code(编号), name(名称), unit(单位), unit_price(单价)</p>
      <p>2. 可选列：description(描述), supply_type(供应类型)</p>
      <p>3. 材料编号必须唯一，否则导入将失败</p>
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
      onClick: () => window.open('/templates/materials_template.csv')
    }
  ];

  return (
    <div>
      <Card
        title="材料管理"
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
              onClick={handleCreateMaterial}
            >
              新建材料
            </Button>
          </Space>
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
            placeholder="分类筛选"
            style={{ width: 120 }}
            allowClear
            value={categoryFilter}
            onChange={value => {
              setCategoryFilter(value);
              fetchMaterials();
            }}
          >
            {categories.map(category => (
              <Option key={category} value={category}>{category}</Option>
            ))}
          </Select>
          <Select
            placeholder="供应类型"
            style={{ width: 120 }}
            allowClear
            value={supplyTypeFilter}
            onChange={value => {
              setSupplyTypeFilter(value);
              fetchMaterials();
            }}
          >
            {supplyTypes.map(type => (
              <Option key={type} value={type}>{type}</Option>
            ))}
          </Select>
          <Select
            placeholder="状态筛选"
            style={{ width: 120 }}
            allowClear
            value={statusFilter}
            onChange={value => {
              setStatusFilter(value);
              fetchMaterials();
            }}
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
            name="category"
            label="材料分类"
            initialValue="其他"
            rules={[{ required: true, message: '请选择材料分类' }]}
          >
            <Select placeholder="请选择材料分类">
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="code"
            label="材料编号"
            rules={[
              { required: true, message: '请输入材料编号' },
              { max: 20, message: '材料编号最多20个字符' }
            ]}
          >
            <Input placeholder="请输入材料编号" />
          </Form.Item>
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
          <Form.Item
            name="supply_type"
            label="供应类型"
            initialValue="两者皆可"
            rules={[{ required: true, message: '请选择供应类型' }]}
          >
            <Select placeholder="请选择供应类型">
              {supplyTypes.map(type => (
                <Option key={type} value={type}>{type}</Option>
              ))}
            </Select>
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

      {/* 批量导入模态框 */}
      <ImportModal
        visible={importModalVisible}
        title="批量导入材料"
        endpoint="/api/materials/import"
        templateUrl="http://localhost:8000/templates/materials_template.csv"
        onClose={handleImportModalClose}
        onSuccess={handleImportSuccess}
        acceptedFileTypes=".csv"
        helpText={importHelpText}
      />
    </div>
  );
};

export default Materials;
