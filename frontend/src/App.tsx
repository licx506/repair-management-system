import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';
import { AuthProvider } from './contexts/AuthContext';
import { isLoggedIn, isAdmin } from './utils/auth';
import { isMobile } from './utils/device';

// 布局
import AdminLayout from './layouts/AdminLayout';
import MobileLayout from './layouts/MobileLayout';
import PCLayout from './layouts/PCLayout';

// 公共页面
import Login from './pages/Login';
import Register from './pages/Register';

// 移动端页面
import MobileHome from './pages/mobile/MobileHome';
import MobileTasks from './pages/mobile/MobileTasks';
import MobileTaskDetail from './pages/mobile/MobileTaskDetail';
import MobileTaskComplete from './pages/mobile/MobileTaskComplete';
import MobileCompleted from './pages/mobile/MobileCompleted';

// PC端页面
import PCHome from './pages/pc/PCHome';
import PCTasks from './pages/pc/PCTasks';
import PCTaskDetail from './pages/pc/PCTaskDetail';
import PCTaskComplete from './pages/pc/PCTaskComplete';

// 管理员页面
import Dashboard from './pages/admin/Dashboard';
import Projects from './pages/admin/Projects';
import Tasks from './pages/admin/Tasks';
import Materials from './pages/admin/Materials';
import WorkItems from './pages/admin/WorkItems';
import Teams from './pages/admin/Teams';
import Statistics from './pages/admin/Statistics';
import Users from './pages/admin/Users';
import Settings from './pages/admin/Settings';

// 路由守卫组件
const ProtectedRoute = ({ children, requiredAuth = true, adminOnly = false }: {
  children: JSX.Element,
  requiredAuth?: boolean,
  adminOnly?: boolean
}) => {
  const authenticated = isLoggedIn();
  const admin = isAdmin();

  if (requiredAuth && !authenticated) {
    return <Navigate to="/login" />;
  }

  if (adminOnly && !admin) {
    return <Navigate to="/" />;
  }

  return children;
};

// 设备检测和重定向
const DeviceRedirect = () => {
  const mobile = isMobile();

  if (isAdmin()) {
    return <Navigate to="/admin/dashboard" />;
  }

  if (mobile) {
    return <Navigate to="/mobile" />;
  } else {
    return <Navigate to="/pc" />;
  }
};

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* 公共路由 */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<DeviceRedirect />} />

            {/* 移动端路由 */}
            <Route path="/mobile" element={
              <ProtectedRoute>
                <MobileLayout>
                  <MobileHome />
                </MobileLayout>
              </ProtectedRoute>
            } />
            <Route path="/mobile/tasks" element={
              <ProtectedRoute>
                <MobileLayout>
                  <MobileTasks />
                </MobileLayout>
              </ProtectedRoute>
            } />
            <Route path="/mobile/tasks/:id" element={
              <ProtectedRoute>
                <MobileLayout>
                  <MobileTaskDetail />
                </MobileLayout>
              </ProtectedRoute>
            } />
            <Route path="/mobile/tasks/:id/complete" element={
              <ProtectedRoute>
                <MobileLayout>
                  <MobileTaskComplete />
                </MobileLayout>
              </ProtectedRoute>
            } />
            <Route path="/mobile/completed" element={
              <ProtectedRoute>
                <MobileLayout>
                  <MobileCompleted />
                </MobileLayout>
              </ProtectedRoute>
            } />

            {/* PC端路由 */}
            <Route path="/pc" element={
              <ProtectedRoute>
                <PCLayout>
                  <PCHome />
                </PCLayout>
              </ProtectedRoute>
            } />
            <Route path="/pc/tasks" element={
              <ProtectedRoute>
                <PCLayout>
                  <PCTasks />
                </PCLayout>
              </ProtectedRoute>
            } />
            <Route path="/pc/tasks/:id" element={
              <ProtectedRoute>
                <PCLayout>
                  <PCTaskDetail />
                </PCLayout>
              </ProtectedRoute>
            } />
            <Route path="/pc/tasks/:id/complete" element={
              <ProtectedRoute>
                <PCLayout>
                  <PCTaskComplete />
                </PCLayout>
              </ProtectedRoute>
            } />

            {/* 管理员路由 */}
            <Route path="/admin/dashboard" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Dashboard />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/projects" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Projects />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/tasks" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Tasks />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/materials" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Materials />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/work-items" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <WorkItems />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/teams" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Teams />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/statistics" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Statistics />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/users" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Users />
                </AdminLayout>
              </ProtectedRoute>
            } />
            <Route path="/admin/settings" element={
              <ProtectedRoute adminOnly={true}>
                <AdminLayout>
                  <Settings />
                </AdminLayout>
              </ProtectedRoute>
            } />

            {/* 404页面 */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
