import React from 'react';
import { Layout, Menu, Avatar, Dropdown, theme } from 'antd';
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

interface PCLayoutProps {
  children: React.ReactNode;
}

const PCLayout: React.FC<PCLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => navigate('/pc/profile'),
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
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ color: '#fff', fontSize: 20, fontWeight: 'bold' }}>
          维修项目管理系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ flex: 1, minWidth: 0, marginLeft: 30 }}
          items={[
            {
              key: '/pc',
              icon: <HomeOutlined />,
              label: <Link to="/pc">首页</Link>,
            },
            {
              key: '/pc/tasks',
              icon: <UnorderedListOutlined />,
              label: <Link to="/pc/tasks">工单管理</Link>,
            },
            {
              key: '/pc/completed',
              icon: <CheckCircleOutlined />,
              label: <Link to="/pc/completed">已完成工单</Link>,
            },
          ]}
        />
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
            <Avatar icon={<UserOutlined />} />
            <span style={{ marginLeft: 8, color: '#fff' }}>{user?.username}</span>
          </div>
        </Dropdown>
      </Header>
      <Content style={{ padding: '24px 50px' }}>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            minHeight: 'calc(100vh - 64px - 48px - 69px)',
          }}
        >
          {children}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        维修项目管理系统 ©{new Date().getFullYear()} Created by Your Company
      </Footer>
    </Layout>
  );
};

export default PCLayout;
