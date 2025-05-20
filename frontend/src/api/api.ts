import axios from 'axios';
import { getApiBaseUrl } from '../utils/config';

// 创建axios实例
const createApi = () => {
  const baseURL = `${getApiBaseUrl()}/api`;
  console.log(`创建API实例，基础URL: ${baseURL}`);

  return axios.create({
    baseURL, // 使用配置中的API服务器地址
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

let api = createApi();

// 提供一个重新创建API实例的函数，以便在配置更改时使用
export const refreshApiInstance = () => {
  api = createApi();
  return api;
};

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应成功:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      data: response.data
    });
    // 返回响应数据，并使用 as any 来避免类型检查错误
    return response.data as any;
  },
  (error) => {
    // 详细记录错误信息
    console.error('API响应错误:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
      code: error.code,
      stack: error.stack
    });

    // 网络错误特殊处理
    if (error.code === 'ERR_NETWORK') {
      console.error('网络连接错误，请检查服务器是否可用');
    }

    // 服务器错误特殊处理
    if (error.response && error.response.status >= 500) {
      console.error('服务器内部错误，请联系管理员');
    }

    if (error.response && error.response.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
