import api from './api';

export interface Task {
  id: number;
  project_id: number;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  assigned_at?: string;
  completed_at?: string;
  created_by_id: number;
  assigned_to_id?: number;
  team_id?: number;
  total_cost: number;
}

export interface TaskMaterial {
  id: number;
  task_id: number;
  material_id: number;
  quantity: number;
  is_company_provided: boolean;
  unit_price: number;
  total_price: number;
}

export interface TaskWorkItem {
  id: number;
  task_id: number;
  work_item_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface TaskDetail extends Task {
  materials: TaskMaterial[];
  work_items: TaskWorkItem[];
}

export interface TaskCreateParams {
  project_id: number;
  title: string;
  description?: string;
}

export interface TaskUpdateParams {
  title?: string;
  description?: string;
  status?: string;
  assigned_to_id?: number;
  team_id?: number;
}

export interface TaskMaterialCreateParams {
  material_id: number;
  quantity: number;
  is_company_provided: boolean;
}

export interface TaskWorkItemCreateParams {
  work_item_id: number;
  quantity: number;
}

export interface TaskCompleteParams {
  materials: TaskMaterialCreateParams[];
  work_items: TaskWorkItemCreateParams[];
}

export const getTasks = async (params?: { status?: string; project_id?: number }): Promise<Task[]> => {
  const response = await api.get('/tasks/', { params });
  return response as Task[];
};

export const getMyTasks = async (params?: { status?: string }): Promise<Task[]> => {
  const response = await api.get('/tasks/my-tasks', { params });
  return response as Task[];
};

export const getTask = async (id: number): Promise<TaskDetail> => {
  const response = await api.get(`/tasks/${id}`);
  return response as TaskDetail;
};

export const createTask = async (params: TaskCreateParams): Promise<Task> => {
  const response = await api.post('/tasks/', params);
  return response as Task;
};

export const updateTask = async (id: number, params: TaskUpdateParams): Promise<Task> => {
  const response = await api.put(`/tasks/${id}`, params);
  return response as Task;
};

export const completeTask = async (id: number, params: TaskCompleteParams): Promise<TaskDetail> => {
  const response = await api.post(`/tasks/${id}/complete`, params);
  return response as TaskDetail;
};

export const deleteTask = async (id: number): Promise<void> => {
  await api.delete(`/tasks/${id}`);
};
