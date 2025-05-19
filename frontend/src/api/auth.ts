import api from './api';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  password: string;
  email: string;
  full_name?: string;
  phone?: string;
  role?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const login = async (params: LoginParams): Promise<TokenResponse> => {
  const formData = new FormData();
  formData.append('username', params.username);
  formData.append('password', params.password);

  const response = await api.post('/auth/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response as TokenResponse;
};

export const register = async (params: RegisterParams): Promise<User> => {
  const response = await api.post('/auth/register', params);
  return response as User;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/auth/me');
  return response as User;
};
