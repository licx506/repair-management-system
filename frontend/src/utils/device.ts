// 判断是否是移动设备
export const isMobile = () => {
  return window.innerWidth <= 768;
};

// 判断是否是平板设备
export const isTablet = () => {
  return window.innerWidth > 768 && window.innerWidth <= 1024;
};

// 判断是否是桌面设备
export const isDesktop = () => {
  return window.innerWidth > 1024;
};

// 获取设备类型
export const getDeviceType = () => {
  if (isMobile()) {
    return 'mobile';
  } else if (isTablet()) {
    return 'tablet';
  } else {
    return 'desktop';
  }
};
