import api from './api';

export interface Material {
  id: number;
  category: string;
  code: string;
  name: string;
  description?: string;
  unit: string;
  unit_price: number;
  supply_type: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface MaterialCreateParams {
  category: string;
  code: string;
  name: string;
  description?: string;
  unit: string;
  unit_price: number;
  supply_type?: string;
}

export interface MaterialUpdateParams {
  category?: string;
  code?: string;
  name?: string;
  description?: string;
  unit?: string;
  unit_price?: number;
  supply_type?: string;
  is_active?: boolean;
}

export const getMaterials = async (params?: {
  category?: string;
  code?: string;
  name?: string;
  supply_type?: string;
  is_active?: boolean;
}): Promise<Material[]> => {
  const response = await api.get('/materials/', { params });
  return response as Material[];
};

export const getMaterialCategories = async (): Promise<string[]> => {
  const response = await api.get('/materials/categories');
  return response as string[];
};

export const getMaterialSupplyTypes = async (): Promise<string[]> => {
  const response = await api.get('/materials/supply-types');
  return response as string[];
};

export const getMaterial = async (id: number): Promise<Material> => {
  const response = await api.get(`/materials/${id}`);
  return response as Material;
};

export const createMaterial = async (params: MaterialCreateParams): Promise<Material> => {
  const response = await api.post('/materials/', params);
  return response as Material;
};

export const updateMaterial = async (id: number, params: MaterialUpdateParams): Promise<Material> => {
  const response = await api.put(`/materials/${id}`, params);
  return response as Material;
};

export const deleteMaterial = async (id: number): Promise<void> => {
  await api.delete(`/materials/${id}`);
};
