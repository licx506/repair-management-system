import type { User } from '../api/auth';

// 保存token到localStorage
export const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

// 从localStorage获取token
export const getToken = () => {
  return localStorage.getItem('token');
};

// 清除token
export const clearToken = () => {
  localStorage.removeItem('token');
};

// 保存用户信息到localStorage
export const setUser = (user: User) => {
  localStorage.setItem('user', JSON.stringify(user));
};

// 从localStorage获取用户信息
export const getUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      return null;
    }
  }
  return null;
};

// 清除用户信息
export const clearUser = () => {
  localStorage.removeItem('user');
};

// 判断用户是否已登录
export const isLoggedIn = () => {
  return !!getToken();
};

// 判断用户是否是管理员
export const isAdmin = () => {
  const user = getUser();
  return user && user.role === 'admin';
};

// 判断用户是否是项目经理
export const isManager = () => {
  const user = getUser();
  return user && user.role === 'manager';
};

// 判断用户是否是施工人员
export const isWorker = () => {
  const user = getUser();
  return user && user.role === 'worker';
};

// 登出
export const logout = () => {
  clearToken();
  clearUser();
  window.location.href = '/login';
};
