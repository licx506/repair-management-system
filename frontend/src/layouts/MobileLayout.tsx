import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Button } from 'antd';
import {
  HomeOutlined,
  UnorderedListOutlined,
  CheckCircleOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Header, Content, Footer } = Layout;

interface MobileLayoutProps {
  children: React.ReactNode;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => navigate('/mobile/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        position: 'fixed', 
        zIndex: 1, 
        width: '100%', 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px'
      }}>
        <div style={{ color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
          维修项目管理
        </div>
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
        </Dropdown>
      </Header>
      <Content style={{ marginTop: 64, padding: '16px', overflow: 'auto' }}>
        {children}
      </Content>
      <Footer style={{ 
        position: 'fixed', 
        bottom: 0, 
        width: '100%', 
        padding: 0,
        backgroundColor: '#fff',
        boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.15)'
      }}>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ display: 'flex', justifyContent: 'space-around' }}
          items={[
            {
              key: '/mobile',
              icon: <HomeOutlined />,
              label: <Link to="/mobile">首页</Link>,
            },
            {
              key: '/mobile/tasks',
              icon: <UnorderedListOutlined />,
              label: <Link to="/mobile/tasks">工单</Link>,
            },
            {
              key: '/mobile/completed',
              icon: <CheckCircleOutlined />,
              label: <Link to="/mobile/completed">已完成</Link>,
            },
          ]}
        />
      </Footer>
    </Layout>
  );
};

export default MobileLayout;
