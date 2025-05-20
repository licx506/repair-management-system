import React, { useEffect, useState } from 'react';
import {
  Card, Table, Tag, Button, Input, Select, Upload,
  Space, Modal, Form, message, Popconfirm, Tooltip, DatePicker, Dropdown,
  Divider, InputNumber, Switch, Row, Col, Typography
} from 'antd';
import {
  PlusOutlined, SearchOutlined, FilterOutlined,
  EditOutlined, DeleteOutlined, EyeOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
  UploadOutlined, DownloadOutlined, MenuOutlined,
  InboxOutlined, MinusCircleOutlined, ImportOutlined
} from '@ant-design/icons';
import {
  getTasks, getTask, createTask, updateTask, deleteTask, completeTask
} from '../../api/tasks';
import type {
  Task, TaskDetail, TaskCreateParams, TaskUpdateParams, TaskCompleteParams
} from '../../api/tasks';
import ImportModal from '../../components/ImportModal';
import { getProjects } from '../../api/projects';
import type { Project } from '../../api/projects';
import { getUsers } from '../../api/users';
import type { User } from '../../api/auth';
import { getTeams } from '../../api/teams';
import type { Team } from '../../api/teams';
import { getMaterials } from '../../api/materials';
import type { Material } from '../../api/materials';
import { getWorkItems } from '../../api/work-items';
import type { WorkItem } from '../../api/work-items';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { Text } = Typography;

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [projectFilter, setProjectFilter] = useState<number | undefined>(undefined);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新建工单');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [currentTask, setCurrentTask] = useState<TaskDetail | null>(null);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [totalCost, setTotalCost] = useState<number>(0);
  const [laborCost, setLaborCost] = useState<number>(0);
  const [companyMaterialCost, setCompanyMaterialCost] = useState<number>(0);
  const [selfMaterialCost, setSelfMaterialCost] = useState<number>(0);
  const [selectedWorkItems, setSelectedWorkItems] = useState<any[]>([]);
  const [selectedMaterials, setSelectedMaterials] = useState<any[]>([]);
  const [fileList, setFileList] = useState<any[]>([]);
  const [workItemsImportModalVisible, setWorkItemsImportModalVisible] = useState(false);
  const [materialsImportModalVisible, setMaterialsImportModalVisible] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<number | null>(null);
  const [workItemCategories, setWorkItemCategories] = useState<string[]>([]);
  const [materialCategories, setMaterialCategories] = useState<string[]>([]);

  useEffect(() => {
    fetchTasks();
    fetchProjects();
    fetchUsers();
    fetchTeams();
    fetchMaterials();
    fetchWorkItems();
  }, []);

  // 计算总费用
  useEffect(() => {
    setTotalCost(laborCost + companyMaterialCost + selfMaterialCost);
  }, [laborCost, companyMaterialCost, selfMaterialCost]);

  // 计算工作内容费用
  const calculateWorkItemsCost = (workItems: any[]) => {
    let cost = 0;
    workItems.forEach(item => {
      if (item && item.work_item_id && item.quantity) {
        const workItem = workItems.find(w => w.id === item.work_item_id);
        if (workItem) {
          cost += workItem.unit_price * item.quantity;
        }
      }
    });
    return cost;
  };

  // 计算材料费用
  const calculateMaterialsCost = (materials: any[]) => {
    let companyCost = 0;
    let selfCost = 0;

    materials.forEach(item => {
      if (item && item.material_id && item.quantity) {
        const material = materials.find(m => m.id === item.material_id);
        if (material) {
          const cost = material.unit_price * item.quantity;
          if (item.is_company_provided) {
            companyCost += cost;
          } else {
            selfCost += cost;
          }
        }
      }
    });

    return { companyCost, selfCost };
  };

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await getTasks();
      setTasks(response);
    } catch (error) {
      console.error('获取工单列表失败:', error);
      message.error('获取工单列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await getProjects();
      setProjects(response);
    } catch (error) {
      console.error('获取项目列表失败:', error);
      message.error('获取项目列表失败');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await getUsers();
      setUsers(response);
    } catch (error) {
      console.error('获取用户列表失败:', error);
      message.error('获取用户列表失败');
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await getTeams();
      setTeams(response);
    } catch (error) {
      console.error('获取团队列表失败:', error);
      message.error('获取团队列表失败');
    }
  };

  const fetchMaterials = async () => {
    try {
      const response = await getMaterials();
      setMaterials(response);

      // 提取所有不重复的材料分类
      const categories = [...new Set(response.map(item => item.category))];
      setMaterialCategories(categories);
    } catch (error) {
      console.error('获取材料列表失败:', error);
      message.error('获取材料列表失败');
    }
  };

  const fetchWorkItems = async () => {
    try {
      const response = await getWorkItems();
      setWorkItems(response);

      // 提取所有不重复的工作内容分类
      const categories = [...new Set(response.map(item => item.category))];
      setWorkItemCategories(categories);
    } catch (error) {
      console.error('获取工作内容列表失败:', error);
      message.error('获取工作内容列表失败');
    }
  };

  const handleCreateTask = () => {
    setModalTitle('新建工单');
    setEditingTask(null);
    form.resetFields();
    setSelectedWorkItems([{ category: undefined, work_item_id: undefined, quantity: 1 }]);
    setSelectedMaterials([{ category: undefined, material_id: undefined, quantity: 1, is_company_provided: true }]);
    setLaborCost(0);
    setCompanyMaterialCost(0);
    setSelfMaterialCost(0);
    setTotalCost(0);
    setFileList([]);
    setModalVisible(true);
  };

  const handleEditTask = async (task: Task) => {
    setModalTitle('编辑工单');
    setEditingTask(task);

    // 设置基本字段
    form.setFieldsValue({
      project_id: task.project_id,
      title: task.title,
      description: task.description,
      attachment: task.attachment,
      status: task.status,
      assigned_to_id: task.assigned_to_id,
      team_id: task.team_id
    });

    // 获取工单详情，包括工作内容和材料
    try {
      const taskDetail = await getTask(task.id);
      if (taskDetail.work_items && taskDetail.work_items.length > 0) {
        const workItemsData = await Promise.all(taskDetail.work_items.map(async item => {
          // 获取工作内容详情，以获取分类
          const workItem = workItems.find(w => w.id === item.work_item_id);
          return {
            category: workItem?.category,
            work_item_id: item.work_item_id,
            quantity: item.quantity
          };
        }));
        setSelectedWorkItems(workItemsData);
        form.setFieldsValue({ work_items: workItemsData });
        setLaborCost(taskDetail.labor_cost || 0);
      } else {
        setSelectedWorkItems([{ category: undefined, work_item_id: undefined, quantity: 1 }]);
        setLaborCost(0);
      }

      if (taskDetail.materials && taskDetail.materials.length > 0) {
        const materialsData = await Promise.all(taskDetail.materials.map(async item => {
          // 获取材料详情，以获取分类
          const material = materials.find(m => m.id === item.material_id);
          return {
            category: material?.category,
            material_id: item.material_id,
            quantity: item.quantity,
            is_company_provided: item.is_company_provided
          };
        }));
        setSelectedMaterials(materialsData);
        form.setFieldsValue({ materials: materialsData });

        // 计算甲供和自购材料费
        let companyCost = 0;
        let selfCost = 0;
        taskDetail.materials.forEach(item => {
          if (item.is_company_provided) {
            companyCost += item.total_price;
          } else {
            selfCost += item.total_price;
          }
        });

        setCompanyMaterialCost(companyCost);
        setSelfMaterialCost(selfCost);
      } else {
        setSelectedMaterials([{ category: undefined, material_id: undefined, quantity: 1, is_company_provided: true }]);
        setCompanyMaterialCost(0);
        setSelfMaterialCost(0);
      }

      // 如果有附件，设置文件列表
      if (task.attachment) {
        setFileList([{
          uid: '-1',
          name: task.attachment.split('/').pop() || '附件',
          status: 'done',
          url: task.attachment
        }]);
      } else {
        setFileList([]);
      }
    } catch (error) {
      console.error('获取工单详情失败:', error);
      message.error('获取工单详情失败');
    }

    setModalVisible(true);
  };

  const handleViewTaskDetail = async (taskId: number) => {
    try {
      const taskDetail = await getTask(taskId);
      setCurrentTask(taskDetail);
      setDetailModalVisible(true);
    } catch (error) {
      console.error('获取工单详情失败:', error);
      message.error('获取工单详情失败');
    }
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await deleteTask(id);
      message.success('删除工单成功');
      fetchTasks();
    } catch (error) {
      console.error('删除工单失败:', error);
      message.error('删除工单失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      // 处理附件
      let attachmentUrl = values.attachment;
      if (fileList.length > 0 && fileList[0].response) {
        attachmentUrl = fileList[0].response.url;
      }

      // 准备工作内容和材料数据
      const workItemsData = values.work_items || [];
      const materialsData = values.materials || [];

      // 计算费用
      const laborCost = calculateWorkItemsCost(workItemsData);
      const { companyCost, selfCost } = calculateMaterialsCost(materialsData);
      const materialCost = companyCost + selfCost;

      // 准备提交的数据
      const taskData = {
        ...values,
        attachment: attachmentUrl,
        labor_cost: laborCost,
        material_cost: materialCost,
        // 将工作内容和材料转换为JSON字符串，以便后端存储
        work_items: JSON.stringify(workItemsData),
        materials: JSON.stringify(materialsData),
        company_material_cost: companyCost,
        self_material_cost: selfCost
      };

      if (editingTask) {
        // 更新工单
        await updateTask(editingTask.id, taskData as TaskUpdateParams);
        message.success('更新工单成功');
      } else {
        // 创建工单
        await createTask(taskData as TaskCreateParams);
        message.success('创建工单成功');
      }

      setModalVisible(false);
      fetchTasks();
    } catch (error) {
      console.error('表单验证失败:', error);
      if (error instanceof Error) {
        message.error(`提交失败: ${error.message}`);
      } else {
        message.error('提交失败，请检查表单数据');
      }
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'pending':
        return <Tag color="blue">待接单</Tag>;
      case 'assigned':
        return <Tag color="orange">已接单</Tag>;
      case 'in_progress':
        return <Tag color="gold">进行中</Tag>;
      case 'completed':
        return <Tag color="green">已完成</Tag>;
      case 'cancelled':
        return <Tag color="red">已取消</Tag>;
      default:
        return <Tag color="default">{status}</Tag>;
    }
  };

  // 过滤工单
  const filteredTasks = tasks.filter(task => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchText.toLowerCase()));

    const matchesStatus = statusFilter ? task.status === statusFilter : true;
    const matchesProject = projectFilter ? task.project_id === projectFilter : true;

    return matchesSearch && matchesStatus && matchesProject;
  });

  // 获取项目名称
  const getProjectName = (projectId: number) => {
    const project = projects.find(p => p.id === projectId);
    return project ? project.title : '未知项目';
  };

  // 获取用户名称
  const getUserName = (userId?: number) => {
    if (!userId) return '未分配';
    const user = users.find(u => u.id === userId);
    return user ? user.username : '未知用户';
  };

  // 获取团队名称
  const getTeamName = (teamId?: number) => {
    if (!teamId) return '未分配';
    const team = teams.find(t => t.id === teamId);
    return team ? team.name : '未知团队';
  };

  const columns = [
    {
      title: '工单ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '工单标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Task) => (
        <a onClick={() => handleViewTaskDetail(record.id)}>{text}</a>
      ),
    },
    {
      title: '所属项目',
      dataIndex: 'project_id',
      key: 'project_id',
      render: (projectId: number) => getProjectName(projectId),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '负责人',
      dataIndex: 'assigned_to_id',
      key: 'assigned_to_id',
      render: (userId?: number) => getUserName(userId),
    },
    {
      title: '施工队伍',
      dataIndex: 'team_id',
      key: 'team_id',
      render: (teamId?: number) => getTeamName(teamId),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '施工费',
      dataIndex: 'labor_cost',
      key: 'labor_cost',
      render: (cost: number) => `¥${cost?.toFixed(2) || '0.00'}`,
    },
    {
      title: '材料费',
      dataIndex: 'material_cost',
      key: 'material_cost',
      render: (cost: number) => `¥${cost?.toFixed(2) || '0.00'}`,
    },
    {
      title: '总费用',
      dataIndex: 'total_cost',
      key: 'total_cost',
      render: (cost: number) => `¥${cost.toFixed(2)}`,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Task) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewTaskDetail(record.id)}
            />
          </Tooltip>
          <Tooltip title="编辑工单">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEditTask(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个工单吗？"
            onConfirm={() => handleDeleteTask(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除工单">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
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
    message.success('工单导入成功');
    fetchTasks();
  };

  // 导入说明文本
  const importHelpText = (
    <div>
      <p>请按照以下格式准备CSV文件：</p>
      <p>1. 必须包含以下列：title(工单主题)</p>
      <p>2. 可选列：project_id(项目ID), description(工单内容), attachment(派单附件), work_list(工作量清单), company_material_list(甲供材清单), self_material_list(自购料清单), labor_cost(施工费), material_cost(材料费)</p>
      <p>3. 如果指定project_id，请确保该项目存在</p>
    </div>
  );

  // 工作内容导入说明文本
  const workItemsImportHelpText = (
    <div>
      <p>请按照以下格式准备CSV文件：</p>
      <p>1. 必须包含以下列：project_number(工作内容编号), quantity(数量)</p>
      <p>2. 请确保工作内容编号存在于系统中</p>
    </div>
  );

  // 材料导入说明文本
  const materialsImportHelpText = (
    <div>
      <p>请按照以下格式准备CSV文件：</p>
      <p>1. 必须包含以下列：code(材料编号), quantity(数量)</p>
      <p>2. 可选列：is_company_provided(是否甲供，值为true/false)</p>
      <p>3. 请确保材料编号存在于系统中</p>
    </div>
  );

  // 处理工作内容导入模态框
  const handleWorkItemsImportModalOpen = () => {
    if (editingTask) {
      setCurrentTaskId(editingTask.id);
      setWorkItemsImportModalVisible(true);
    } else {
      message.error('请先保存工单，然后再导入工作内容');
    }
  };

  const handleWorkItemsImportModalClose = () => {
    setWorkItemsImportModalVisible(false);
  };

  const handleWorkItemsImportSuccess = () => {
    message.success('工作内容导入成功');
    if (editingTask) {
      handleEditTask(editingTask); // 重新加载工单数据
    }
  };

  // 处理材料导入模态框
  const handleMaterialsImportModalOpen = () => {
    if (editingTask) {
      setCurrentTaskId(editingTask.id);
      setMaterialsImportModalVisible(true);
    } else {
      message.error('请先保存工单，然后再导入材料');
    }
  };

  const handleMaterialsImportModalClose = () => {
    setMaterialsImportModalVisible(false);
  };

  const handleMaterialsImportSuccess = () => {
    message.success('材料导入成功');
    if (editingTask) {
      handleEditTask(editingTask); // 重新加载工单数据
    }
  };

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
      onClick: () => window.open('/templates/tasks_template.csv')
    }
  ];

  return (
    <div>
      <Card
        title="工单管理"
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
              onClick={handleCreateTask}
            >
              新建工单
            </Button>
          </Space>
        }
      >
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索工单"
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
            <Option value="pending">待接单</Option>
            <Option value="assigned">已接单</Option>
            <Option value="in_progress">进行中</Option>
            <Option value="completed">已完成</Option>
            <Option value="cancelled">已取消</Option>
          </Select>
          <Select
            placeholder="项目筛选"
            style={{ width: 150 }}
            allowClear
            value={projectFilter}
            onChange={value => setProjectFilter(value)}
          >
            {projects.map(project => (
              <Option key={project.id} value={project.id}>{project.title}</Option>
            ))}
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredTasks.map(task => ({ ...task, key: task.id }))}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建/编辑工单模态框 */}
      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={800}
      >
        <Form form={form} layout="vertical" onValuesChange={(changedValues, allValues) => {
          // 当工作内容或材料变化时，重新计算费用
          if (changedValues.work_items || changedValues.materials) {
            // 计算施工费
            if (changedValues.work_items) {
              const workItemsData = allValues.work_items || [];
              let newLaborCost = 0;
              workItemsData.forEach((item: any) => {
                if (item && item.work_item_id && item.quantity) {
                  const workItem = workItems.find(w => w.id === item.work_item_id);
                  if (workItem) {
                    newLaborCost += workItem.unit_price * item.quantity;
                  }
                }
              });
              setLaborCost(newLaborCost);
            }

            // 计算材料费
            if (changedValues.materials) {
              const materialsData = allValues.materials || [];
              let newCompanyCost = 0;
              let newSelfCost = 0;

              materialsData.forEach((item: any) => {
                if (item && item.material_id && item.quantity) {
                  const material = materials.find(m => m.id === item.material_id);
                  if (material) {
                    const cost = material.unit_price * item.quantity;
                    if (item.is_company_provided) {
                      newCompanyCost += cost;
                    } else {
                      newSelfCost += cost;
                    }
                  }
                }
              });

              setCompanyMaterialCost(newCompanyCost);
              setSelfMaterialCost(newSelfCost);
            }
          }
        }}>
          <Form.Item
            name="project_id"
            label="所属项目"
          >
            <Select placeholder="请选择所属项目" allowClear>
              {projects.map(project => (
                <Option key={project.id} value={project.id}>{project.title}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="title"
            label="工单主题"
            rules={[{ required: true, message: '请输入工单主题' }]}
          >
            <Input placeholder="请输入工单主题" />
          </Form.Item>
          <Form.Item
            name="description"
            label="工单内容"
          >
            <Input.TextArea placeholder="请输入工单内容" rows={4} />
          </Form.Item>

          {/* 派单附件 - 改为上传组件 */}
          <Form.Item
            name="attachment"
            label="派单附件"
          >
            <div>
              <Upload.Dragger
                name="file"
                fileList={fileList}
                beforeUpload={(file) => {
                  setFileList([
                    {
                      uid: '-1',
                      name: file.name,
                      status: 'uploading',
                      percent: 0,
                      originFileObj: file,
                    }
                  ]);

                  // 手动上传文件
                  const formData = new FormData();
                  formData.append('file', file);

                  // 获取token
                  const token = localStorage.getItem('token');

                  // 显示上传中状态
                  const newFileList = [{
                    uid: '-1',
                    name: file.name,
                    status: 'uploading',
                    percent: 50,
                    originFileObj: file,
                  }];
                  setFileList(newFileList);

                  // 发送请求
                  fetch('http://xin.work.gd:8000/api/upload', {
                    method: 'POST',
                    headers: {
                      'Authorization': `Bearer ${token}`
                    },
                    body: formData,
                  })
                  .then(response => {
                    if (!response.ok) {
                      throw new Error(`上传失败: ${response.status} ${response.statusText}`);
                    }
                    return response.json();
                  })
                  .then(data => {
                    console.log('上传成功:', data);

                    // 更新文件列表状态为成功
                    const successFileList = [{
                      uid: '-1',
                      name: file.name,
                      status: 'done',
                      url: data.url,
                      response: data,
                    }];
                    setFileList(successFileList);

                    // 设置表单字段值
                    form.setFieldsValue({ attachment: data.url });

                    message.success('文件上传成功');
                  })
                  .catch(error => {
                    console.error('上传失败:', error);

                    // 更新文件列表状态为失败
                    const errorFileList = [{
                      uid: '-1',
                      name: file.name,
                      status: 'error',
                      error: error.message,
                    }];
                    setFileList(errorFileList);

                    message.error(`文件上传失败: ${error.message}`);
                  });

                  // 阻止默认上传行为
                  return false;
                }}
                onRemove={() => {
                  setFileList([]);
                  form.setFieldsValue({ attachment: undefined });
                  return true;
                }}
                maxCount={1}
              >
                {fileList.length === 0 && (
                  <>
                    <p className="ant-upload-drag-icon">
                      <InboxOutlined />
                    </p>
                    <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                    <p className="ant-upload-hint">支持单个文件上传</p>
                  </>
                )}
              </Upload.Dragger>

              {form.getFieldValue('attachment') && (
                <div style={{ marginTop: 8 }}>
                  <a
                    href={`http://xin.work.gd:8000${form.getFieldValue('attachment')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    查看已上传文件
                  </a>
                </div>
              )}
            </div>
          </Form.Item>

          {/* 工作量清单 - 改为选择工作内容 */}
          <Divider orientation="left">
            <Space>
              工作量清单
              {editingTask && (
                <Button
                  type="primary"
                  size="small"
                  icon={<ImportOutlined />}
                  onClick={handleWorkItemsImportModalOpen}
                >
                  批量导入
                </Button>
              )}
            </Space>
          </Divider>

          <div style={{ marginBottom: 16 }}>
            <Row gutter={16} style={{ background: '#f5f5f5', padding: '8px 0', fontWeight: 'bold' }}>
              <Col span={4}><Text>项目分类</Text></Col>
              <Col span={4}><Text>编号</Text></Col>
              <Col span={4}><Text>工作内容</Text></Col>
              <Col span={3}><Text>单价</Text></Col>
              <Col span={3}><Text>单位</Text></Col>
              <Col span={3}><Text>数量</Text></Col>
              <Col span={3}><Text>金额</Text></Col>
            </Row>
          </div>

          <Form.List name="work_items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => {
                  // 获取当前行的分类和工作内容ID
                  const category = form.getFieldValue(['work_items', name, 'category']);
                  const workItemId = form.getFieldValue(['work_items', name, 'work_item_id']);
                  const quantity = form.getFieldValue(['work_items', name, 'quantity']) || 0;

                  // 根据分类筛选工作内容
                  const filteredWorkItems = category
                    ? workItems.filter(item => item.category === category)
                    : workItems;

                  // 查找工作内容详情
                  const workItem = workItems.find(item => item.id === workItemId);

                  // 计算金额
                  const amount = workItem ? workItem.unit_price * quantity : 0;

                  return (
                    <Row key={key} gutter={16} style={{ marginBottom: 8 }}>
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
                            onChange={(value) => {
                              // 当分类变化时，清空工作内容选择
                              const fields = form.getFieldsValue();
                              const workItems = fields.work_items || [];
                              workItems[name].work_item_id = undefined;
                              form.setFieldsValue({ work_items: workItems });
                              form.validateFields();
                            }}
                          >
                            {workItemCategories.map(category => (
                              <Option key={category} value={category}>
                                {category}
                              </Option>
                            ))}
                          </Select>
                        </Form.Item>
                      </Col>
                      <Col span={4}>
                        <Text>{workItem?.project_number || '-'}</Text>
                      </Col>
                      <Col span={4}>
                        <Form.Item
                          {...restField}
                          name={[name, 'work_item_id']}
                          rules={[{ required: true, message: '请选择工作内容' }]}
                          style={{ marginBottom: 0 }}
                        >
                          <Select
                            placeholder="选择工作内容"
                            style={{ width: '100%' }}
                            onChange={() => form.validateFields()}
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
                      <Col span={3}>
                        <Text>{workItem?.unit || '-'}</Text>
                      </Col>
                      <Col span={3}>
                        <Form.Item
                          {...restField}
                          name={[name, 'quantity']}
                          rules={[{ required: true, message: '请输入数量' }]}
                          initialValue={1}
                          style={{ marginBottom: 0 }}
                        >
                          <InputNumber
                            placeholder="数量"
                            min={0.01}
                            step={0.01}
                            style={{ width: '100%' }}
                            onChange={() => form.validateFields()}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={2}>
                        <Text>¥{amount.toFixed(2)}</Text>
                      </Col>
                      <Col span={1}>
                        <MinusCircleOutlined onClick={() => remove(name)} style={{ color: '#ff4d4f' }} />
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

          {/* 材料清单 - 改为选择材料 */}
          <Divider orientation="left">
            <Space>
              材料清单
              {editingTask && (
                <Button
                  type="primary"
                  size="small"
                  icon={<ImportOutlined />}
                  onClick={handleMaterialsImportModalOpen}
                >
                  批量导入
                </Button>
              )}
            </Space>
          </Divider>

          <div style={{ marginBottom: 16 }}>
            <Row gutter={16} style={{ background: '#f5f5f5', padding: '8px 0', fontWeight: 'bold' }}>
              <Col span={3}><Text>分类</Text></Col>
              <Col span={3}><Text>编号</Text></Col>
              <Col span={4}><Text>名称</Text></Col>
              <Col span={3}><Text>描述</Text></Col>
              <Col span={2}><Text>单价</Text></Col>
              <Col span={2}><Text>单位</Text></Col>
              <Col span={2}><Text>数量</Text></Col>
              <Col span={2}><Text>金额</Text></Col>
              <Col span={2}><Text>供应方式</Text></Col>
            </Row>
          </div>

          <Form.List name="materials">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => {
                  // 获取当前行的分类、材料ID、数量和供应方式
                  const category = form.getFieldValue(['materials', name, 'category']);
                  const materialId = form.getFieldValue(['materials', name, 'material_id']);
                  const quantity = form.getFieldValue(['materials', name, 'quantity']) || 0;
                  const isCompanyProvided = form.getFieldValue(['materials', name, 'is_company_provided']);

                  // 根据分类筛选材料
                  const filteredMaterials = category
                    ? materials.filter(item => item.category === category)
                    : materials;

                  // 查找材料详情
                  const material = materials.find(item => item.id === materialId);

                  // 计算金额
                  const amount = material ? material.unit_price * quantity : 0;

                  return (
                    <Row key={key} gutter={16} style={{ marginBottom: 8 }}>
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
                            onChange={(value) => {
                              // 当分类变化时，清空材料选择
                              const fields = form.getFieldsValue();
                              const materials = fields.materials || [];
                              materials[name].material_id = undefined;
                              form.setFieldsValue({ materials: materials });
                              form.validateFields();
                            }}
                          >
                            {materialCategories.map(category => (
                              <Option key={category} value={category}>
                                {category}
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
                            onChange={() => form.validateFields()}
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
                          initialValue={1}
                          style={{ marginBottom: 0 }}
                        >
                          <InputNumber
                            placeholder="数量"
                            min={0.01}
                            step={0.01}
                            style={{ width: '100%' }}
                            onChange={() => form.validateFields()}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={2}>
                        <Text>¥{amount.toFixed(2)}</Text>
                      </Col>
                      <Col span={2}>
                        <Form.Item
                          {...restField}
                          name={[name, 'is_company_provided']}
                          valuePropName="checked"
                          initialValue={true}
                          style={{ marginBottom: 0 }}
                        >
                          <Switch checkedChildren="甲供" unCheckedChildren="自购" />
                        </Form.Item>
                      </Col>
                      <Col span={1}>
                        <MinusCircleOutlined onClick={() => remove(name)} style={{ color: '#ff4d4f' }} />
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

          {/* 费用统计 */}
          <Divider orientation="left">费用统计</Divider>
          <Row gutter={16}>
            <Col span={6}>
              <Card size="small" title="施工费">
                ¥{laborCost.toFixed(2)}
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="甲供材料费">
                ¥{companyMaterialCost.toFixed(2)}
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="自购材料费">
                ¥{selfMaterialCost.toFixed(2)}
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="总费用">
                ¥{totalCost.toFixed(2)}
              </Card>
            </Col>
          </Row>

          {editingTask && (
            <>
              <Divider orientation="left">工单状态</Divider>
              <Form.Item
                name="status"
                label="工单状态"
              >
                <Select placeholder="请选择工单状态">
                  <Option value="pending">待接单</Option>
                  <Option value="assigned">已接单</Option>
                  <Option value="in_progress">进行中</Option>
                  <Option value="completed">已完成</Option>
                  <Option value="cancelled">已取消</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="assigned_to_id"
                label="负责人"
              >
                <Select placeholder="请选择负责人" allowClear>
                  {users.map(user => (
                    <Option key={user.id} value={user.id}>{user.username}</Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="team_id"
                label="施工队伍"
              >
                <Select placeholder="请选择施工队伍" allowClear>
                  {teams.map(team => (
                    <Option key={team.id} value={team.id}>{team.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>

      {/* 工单详情模态框 */}
      <Modal
        title="工单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        {currentTask && (
          <div>
            <h3>{currentTask.title}</h3>
            <p><strong>状态：</strong>{getStatusTag(currentTask.status)}</p>
            <p><strong>所属项目：</strong>{getProjectName(currentTask.project_id)}</p>
            <p><strong>负责人：</strong>{getUserName(currentTask.assigned_to_id)}</p>
            <p><strong>施工队伍：</strong>{getTeamName(currentTask.team_id)}</p>
            <p><strong>创建时间：</strong>{dayjs(currentTask.created_at).format('YYYY-MM-DD HH:mm')}</p>
            {currentTask.assigned_at && (
              <p><strong>接单时间：</strong>{dayjs(currentTask.assigned_at).format('YYYY-MM-DD HH:mm')}</p>
            )}
            {currentTask.completed_at && (
              <p><strong>完成时间：</strong>{dayjs(currentTask.completed_at).format('YYYY-MM-DD HH:mm')}</p>
            )}
            <p><strong>施工费：</strong>¥{currentTask.labor_cost?.toFixed(2) || '0.00'}</p>
            <p><strong>材料费：</strong>¥{currentTask.material_cost?.toFixed(2) || '0.00'}</p>
            <p><strong>总费用：</strong>¥{currentTask.total_cost.toFixed(2)}</p>
            <p><strong>工单内容：</strong>{currentTask.description || '无'}</p>
            {currentTask.attachment && (
              <p>
                <strong>派单附件：</strong>
                <a href={`http://xin.work.gd:8000${currentTask.attachment}`} target="_blank" rel="noopener noreferrer">
                  查看附件
                </a>
              </p>
            )}
            {currentTask.work_list && (
              <p><strong>工作量清单：</strong>{currentTask.work_list}</p>
            )}
            {currentTask.company_material_list && (
              <p><strong>甲供材清单：</strong>{currentTask.company_material_list}</p>
            )}
            {currentTask.self_material_list && (
              <p><strong>自购料清单：</strong>{currentTask.self_material_list}</p>
            )}

            {currentTask.materials.length > 0 && (
              <>
                <h4>使用材料</h4>
                <Table
                  size="small"
                  pagination={false}
                  dataSource={currentTask.materials.map((m, index) => ({ ...m, key: index }))}
                  columns={[
                    {
                      title: '材料名称',
                      dataIndex: 'material_id',
                      key: 'material_name',
                      render: (id: number) => {
                        const material = materials.find(m => m.id === id);
                        return material ? material.name : '未知材料';
                      }
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
                      render: (price: number) => `¥${price.toFixed(2)}`
                    },
                    {
                      title: '总价',
                      dataIndex: 'total_price',
                      key: 'total_price',
                      render: (price: number) => `¥${price.toFixed(2)}`
                    },
                    {
                      title: '供应方式',
                      dataIndex: 'is_company_provided',
                      key: 'is_company_provided',
                      render: (isCompanyProvided: boolean) =>
                        isCompanyProvided ? <Tag color="blue">甲供</Tag> : <Tag color="green">自购</Tag>
                    }
                  ]}
                />
              </>
            )}

            {currentTask.work_items.length > 0 && (
              <>
                <h4 style={{ marginTop: 16 }}>工作内容</h4>
                <Table
                  size="small"
                  pagination={false}
                  dataSource={currentTask.work_items.map((w, index) => ({ ...w, key: index }))}
                  columns={[
                    {
                      title: '工作内容',
                      dataIndex: 'work_item_id',
                      key: 'work_item_name',
                      render: (id: number) => {
                        const workItem = workItems.find(w => w.id === id);
                        return workItem ? workItem.name : '未知工作内容';
                      }
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
                      render: (price: number) => `¥${price.toFixed(2)}`
                    },
                    {
                      title: '总价',
                      dataIndex: 'total_price',
                      key: 'total_price',
                      render: (price: number) => `¥${price.toFixed(2)}`
                    }
                  ]}
                />
              </>
            )}
          </div>
        )}
      </Modal>

      {/* 批量导入工单模态框 */}
      <ImportModal
        visible={importModalVisible}
        title="批量导入工单"
        endpoint="/api/tasks/import"
        templateUrl="http://xin.work.gd:8000/templates/tasks_template.csv"
        onClose={handleImportModalClose}
        onSuccess={handleImportSuccess}
        acceptedFileTypes=".csv"
        helpText={importHelpText}
      />

      {/* 批量导入工作内容模态框 */}
      {currentTaskId && (
        <ImportModal
          visible={workItemsImportModalVisible}
          title="批量导入工作内容"
          endpoint={`/api/tasks/${currentTaskId}/work-items/import`}
          templateUrl="http://xin.work.gd:8000/templates/task_work_items_template.csv"
          onClose={handleWorkItemsImportModalClose}
          onSuccess={handleWorkItemsImportSuccess}
          acceptedFileTypes=".csv"
          helpText={workItemsImportHelpText}
        />
      )}

      {/* 批量导入材料模态框 */}
      {currentTaskId && (
        <ImportModal
          visible={materialsImportModalVisible}
          title="批量导入材料"
          endpoint={`/api/tasks/${currentTaskId}/materials/import`}
          templateUrl="http://xin.work.gd:8000/templates/task_materials_template.csv"
          onClose={handleMaterialsImportModalClose}
          onSuccess={handleMaterialsImportSuccess}
          acceptedFileTypes=".csv"
          helpText={materialsImportHelpText}
        />
      )}
    </div>
  );
};

export default Tasks;
