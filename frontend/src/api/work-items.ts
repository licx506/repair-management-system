import api from './api';

export interface WorkItem {
  id: number;
  category: string;
  project_number: string;
  name: string;
  description?: string;
  unit: string;
  skilled_labor_days: number;
  unskilled_labor_days: number;
  unit_price: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface WorkItemCreateParams {
  category: string;
  project_number: string;
  name: string;
  description?: string;
  unit: string;
  skilled_labor_days?: number;
  unskilled_labor_days?: number;
  unit_price: number;
}

export interface WorkItemUpdateParams {
  category?: string;
  project_number?: string;
  name?: string;
  description?: string;
  unit?: string;
  skilled_labor_days?: number;
  unskilled_labor_days?: number;
  unit_price?: number;
  is_active?: boolean;
}

export const getWorkItems = async (params?: {
  category?: string;
  project_number?: string;
  name?: string;
  is_active?: boolean;
}): Promise<WorkItem[]> => {
  const response = await api.get('/work-items/', { params });
  return response as WorkItem[];
};

export const getWorkItem = async (id: number): Promise<WorkItem> => {
  const response = await api.get(`/work-items/${id}`);
  return response as WorkItem;
};

export const createWorkItem = async (params: WorkItemCreateParams): Promise<WorkItem> => {
  const response = await api.post('/work-items/', params);
  return response as WorkItem;
};

export const updateWorkItem = async (id: number, params: WorkItemUpdateParams): Promise<WorkItem> => {
  const response = await api.put(`/work-items/${id}`, params);
  return response as WorkItem;
};

export const deleteWorkItem = async (id: number): Promise<void> => {
  await api.delete(`/work-items/${id}`);
};

export const getWorkItemCategories = async (): Promise<string[]> => {
  const response = await api.get('/work-items/categories');
  return response as string[];
};
