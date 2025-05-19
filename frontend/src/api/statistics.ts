import api from './api';

export interface ProjectStatistics {
  total_projects: number;
  completed_projects: number;
  in_progress_projects: number;
  pending_projects: number;
  completion_rate: number;
}

export interface TaskStatistics {
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  avg_completion_time_hours: number;
}

export interface MaterialUsage {
  id: number;
  name: string;
  total_quantity: number;
  total_cost: number;
}

export interface MaterialStatistics {
  total_material_cost: number;
  company_provided_cost: number;
  self_purchased_cost: number;
  most_used_materials: MaterialUsage[];
}

export interface WorkItemUsage {
  id: number;
  name: string;
  total_quantity: number;
  total_cost: number;
}

export interface WorkItemStatistics {
  total_work_item_cost: number;
  most_performed_work_items: WorkItemUsage[];
}

export interface TeamStatistics {
  id: number;
  name: string;
  completed_tasks_count: number;
  total_tasks_count: number;
  completion_rate: number;
  total_income: number;
  members_count: number;
  avg_income_per_member: number;
}

export const getProjectStatistics = async (params?: { start_date?: string; end_date?: string }): Promise<ProjectStatistics> => {
  const response = await api.get('/statistics/projects', { params });
  return response as ProjectStatistics;
};

export const getTaskStatistics = async (params?: { start_date?: string; end_date?: string }): Promise<TaskStatistics> => {
  const response = await api.get('/statistics/tasks', { params });
  return response as TaskStatistics;
};

export const getMaterialStatistics = async (params?: { start_date?: string; end_date?: string }): Promise<MaterialStatistics> => {
  const response = await api.get('/statistics/materials', { params });
  return response as MaterialStatistics;
};

export const getWorkItemStatistics = async (params?: { start_date?: string; end_date?: string }): Promise<WorkItemStatistics> => {
  const response = await api.get('/statistics/work-items', { params });
  return response as WorkItemStatistics;
};

export const getTeamStatistics = async (params?: { start_date?: string; end_date?: string }): Promise<TeamStatistics[]> => {
  const response = await api.get('/statistics/teams', { params });
  return response as TeamStatistics[];
};
