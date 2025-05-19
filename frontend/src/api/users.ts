import api from './api';
import type { User } from './auth';

export const getUsers = async (params?: { role?: string; is_active?: boolean }): Promise<User[]> => {
  const response = await api.get('/users/', { params });
  return response as User[];
};

export const getUser = async (id: number): Promise<User> => {
  const response = await api.get(`/users/${id}`);
  return response as User;
};

export interface UserUpdateParams {
  email?: string;
  full_name?: string;
  phone?: string;
  role?: string;
  is_active?: boolean;
}

export const updateUser = async (id: number, params: UserUpdateParams): Promise<User> => {
  const response = await api.put(`/users/${id}`, params);
  return response as User;
};

export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/users/${id}`);
};
