import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Button, DatePicker } from 'antd';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ToolOutlined,
  ProjectOutlined,
  TeamOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { getTasks } from '../../api/tasks';
import type { Task } from '../../api/tasks';
import { getProjects } from '../../api/projects';
import {
  getProjectStatistics,
  getTaskStatistics,
  getMaterialStatistics,
  getWorkItemStatistics
} from '../../api/statistics';
import ReactECharts from 'echarts-for-react';

const { RangePicker } = DatePicker;

const Dashboard: React.FC = () => {
  const [projectStats, setProjectStats] = useState<any>(null);
  const [taskStats, setTaskStats] = useState<any>(null);
  const [materialStats, setMaterialStats] = useState<any>(null);
  const [workItemStats, setWorkItemStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'day'),
    dayjs()
  ]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {
        start_date: dateRange[0].format('YYYY-MM-DDTHH:mm:ss.SSSZ'),
        end_date: dateRange[1].format('YYYY-MM-DDTHH:mm:ss.SSSZ')
      };

      const [
        projectStatsResponse,
        taskStatsResponse,
        materialStatsResponse,
        workItemStatsResponse
      ] = await Promise.all([
        getProjectStatistics(params),
        getTaskStatistics(params),
        getMaterialStatistics(params),
        getWorkItemStatistics(params)
      ]);

      setProjectStats(projectStatsResponse);
      setTaskStats(taskStatsResponse);
      setMaterialStats(materialStatsResponse);
      setWorkItemStats(workItemStatsResponse);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const projectPieOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: ['已完成', '进行中', '待处理']
    },
    series: [
      {
        name: '项目状态',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: projectStats?.completed_projects || 0, name: '已完成' },
          { value: projectStats?.in_progress_projects || 0, name: '进行中' },
          { value: projectStats?.pending_projects || 0, name: '待处理' }
        ]
      }
    ]
  };

  const taskPieOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: ['已完成', '进行中', '待处理']
    },
    series: [
      {
        name: '工单状态',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: taskStats?.completed_tasks || 0, name: '已完成' },
          { value: taskStats?.in_progress_tasks || 0, name: '进行中' },
          { value: taskStats?.pending_tasks || 0, name: '待处理' }
        ]
      }
    ]
  };

  const materialBarOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['材料费用']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01]
    },
    yAxis: {
      type: 'category',
      data: materialStats?.most_used_materials?.slice(0, 5).map((m: any) => m.name) || []
    },
    series: [
      {
        name: '材料费用',
        type: 'bar',
        data: materialStats?.most_used_materials?.slice(0, 5).map((m: any) => m.total_cost) || []
      }
    ]
  };

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col>
            <span>选择日期范围：</span>
          </Col>
          <Col>
            <RangePicker
              value={dateRange}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                }
              }}
            />
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={projectStats?.total_projects || 0}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="工单总数"
              value={taskStats?.total_tasks || 0}
              valueStyle={{ color: '#faad14' }}
              prefix={<ToolOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="材料总费用"
              value={materialStats?.total_material_cost || 0}
              precision={2}
              valueStyle={{ color: '#52c41a' }}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="工作内容总费用"
              value={workItemStats?.total_work_item_cost || 0}
              precision={2}
              valueStyle={{ color: '#722ed1' }}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="项目状态分布">
            <ReactECharts option={projectPieOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="工单状态分布">
            <ReactECharts option={taskPieOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="最常用材料费用统计">
            <ReactECharts option={materialBarOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
