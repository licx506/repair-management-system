import api from './api';

export interface Project {
  id: number;
  title: string;
  description?: string;
  location: string;
  contact_name: string;
  contact_phone: string;
  status: string;
  priority: number;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  created_by_id: number;
}

export interface ProjectDetail extends Project {
  tasks_count: number;
  completed_tasks_count: number;
}

export interface ProjectCreateParams {
  title: string;
  description?: string;
  location: string;
  contact_name: string;
  contact_phone: string;
  priority?: number;
}

export interface ProjectUpdateParams {
  title?: string;
  description?: string;
  location?: string;
  contact_name?: string;
  contact_phone?: string;
  status?: string;
  priority?: number;
}

export const getProjects = async (params?: { status?: string }): Promise<Project[]> => {
  const response = await api.get('/projects/', { params });
  return response as Project[];
};

export const getProject = async (id: number): Promise<ProjectDetail> => {
  const response = await api.get(`/projects/${id}`);
  return response as ProjectDetail;
};

export const createProject = async (params: ProjectCreateParams): Promise<Project> => {
  const response = await api.post('/projects/', params);
  return response as Project;
};

export const updateProject = async (id: number, params: ProjectUpdateParams): Promise<Project> => {
  const response = await api.put(`/projects/${id}`, params);
  return response as Project;
};

export const deleteProject = async (id: number): Promise<void> => {
  await api.delete(`/projects/${id}`);
};
