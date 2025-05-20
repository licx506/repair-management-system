// 系统配置管理工具

// 默认配置
const defaultConfig = {
  // API服务器地址
  apiBaseUrl: 'http://localhost:8458',
  // 模板文件服务器地址
  templateBaseUrl: 'http://localhost:8458',
  // 其他配置项可以在这里添加
};

// 配置存储键名
const CONFIG_STORAGE_KEY = 'repair_management_config';

// 获取完整配置
export const getConfig = () => {
  try {
    const storedConfig = localStorage.getItem(CONFIG_STORAGE_KEY);
    if (storedConfig) {
      return { ...defaultConfig, ...JSON.parse(storedConfig) };
    }
  } catch (error) {
    console.error('读取配置失败:', error);
  }
  return defaultConfig;
};

// 获取特定配置项
export const getConfigItem = (key: keyof typeof defaultConfig) => {
  const config = getConfig();
  return config[key];
};

// 更新配置
export const updateConfig = (newConfig: Partial<typeof defaultConfig>) => {
  try {
    const currentConfig = getConfig();
    const updatedConfig = { ...currentConfig, ...newConfig };
    localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(updatedConfig));
    return updatedConfig;
  } catch (error) {
    console.error('保存配置失败:', error);
    return getConfig();
  }
};

// 重置配置为默认值
export const resetConfig = () => {
  localStorage.removeItem(CONFIG_STORAGE_KEY);
  return defaultConfig;
};

// 获取API基础URL
export const getApiBaseUrl = () => getConfigItem('apiBaseUrl');

// 获取模板文件基础URL
export const getTemplateBaseUrl = () => getConfigItem('templateBaseUrl');
