# 架构文档

本文档描述了维修项目管理系统的代码架构和项目结构。

## 代码架构

### 后端架构

后端采用分层架构设计，主要包括以下几层：

1. **路由层（Routers）**：处理HTTP请求，定义API端点
   - 负责接收和响应HTTP请求
   - 处理请求参数验证
   - 调用相应的业务逻辑
   - 返回适当的HTTP响应

2. **模式层（Schemas）**：使用Pydantic定义数据验证和序列化模型
   - 定义请求和响应的数据结构
   - 提供数据验证和类型转换
   - 支持文档自动生成

3. **模型层（Models）**：使用SQLAlchemy定义数据库模型和关系
   - 定义数据库表结构
   - 定义表之间的关系
   - 提供ORM功能，简化数据库操作

4. **工具层（Utils）**：提供认证、权限等通用功能
   - 认证和授权
   - 密码哈希
   - 数据导入导出
   - 其他通用工具函数

### 前端架构

前端采用组件化架构，主要包括以下几部分：

1. **API层**：封装与后端的通信
   - 定义API请求函数
   - 处理请求和响应拦截
   - 统一错误处理

2. **上下文（Contexts）**：管理全局状态，如用户认证
   - 提供全局状态管理
   - 实现状态共享和更新

3. **布局组件（Layouts）**：提供不同设备的页面布局
   - 管理页面整体结构
   - 提供响应式布局支持

4. **页面组件（Pages）**：实现具体的业务功能
   - 实现具体的业务逻辑
   - 处理用户交互
   - 展示数据和UI

5. **工具函数（Utils）**：提供通用功能
   - 认证工具
   - 设备检测
   - 日期处理
   - 其他通用工具函数

### 响应式设计

系统根据设备类型提供不同的用户界面：

1. **移动端**：使用`MobileLayout`和`mobile/`目录下的组件
   - 针对小屏幕设备优化
   - 简化操作流程
   - 专注于核心功能

2. **PC端**：使用`PCLayout`和`pc/`目录下的组件
   - 提供完整功能
   - 支持复杂操作
   - 优化大屏幕显示

3. **管理端**：使用`AdminLayout`和`admin/`目录下的组件
   - 提供管理功能
   - 支持批量操作
   - 提供数据分析和统计

## 项目结构

```
.
├── backend/                # 后端代码
│   ├── main.py            # 主应用入口
│   ├── database.py        # 数据库配置
│   ├── models/            # 数据模型
│   │   ├── __init__.py    # 模型导入
│   │   ├── user.py        # 用户模型
│   │   ├── project.py     # 维修项目模型
│   │   ├── task.py        # 工单模型
│   │   ├── material.py    # 材料模型
│   │   ├── work_item.py   # 工作内容模型
│   │   ├── team.py        # 施工队伍模型
│   │   ├── project_team.py # 项目-队伍关联
│   │   └── task_worker.py # 工单-工人关联
│   ├── routers/           # API路由
│   │   ├── __init__.py    # 路由导入
│   │   ├── auth.py        # 认证相关
│   │   ├── projects.py    # 维修项目管理
│   │   ├── tasks.py       # 工单管理
│   │   ├── materials.py   # 材料管理
│   │   ├── work_items.py  # 工作内容管理
│   │   ├── teams.py       # 施工队伍管理
│   │   ├── statistics.py  # 统计相关
│   │   └── users.py       # 用户管理
│   ├── schemas/           # Pydantic模型
│   │   ├── __init__.py    # 模式导入
│   │   ├── user.py        # 用户模式
│   │   ├── project.py     # 项目模式
│   │   ├── task.py        # 工单模式
│   │   ├── material.py    # 材料模式
│   │   ├── work_item.py   # 工作内容模式
│   │   └── team.py        # 团队模式
│   ├── utils/             # 工具函数
│   │   ├── __init__.py    # 工具导入
│   │   ├── auth.py        # 认证工具
│   │   └── import_utils.py # 导入工具
│   ├── static/            # 静态文件
│       └── templates/     # 模板文件
│           ├── work_items_template.csv # 工作内容导入模板
│           ├── materials_template.csv  # 材料导入模板
│           ├── tasks_template.csv      # 工单导入模板
│           └── users_template.csv      # 用户导入模板
├── frontend/              # 前端代码
│   ├── src/               # 源代码
│   │   ├── api/           # API调用
│   │   │   ├── api.ts     # API基础配置
│   │   │   ├── auth.ts    # 认证API
│   │   │   ├── projects.ts # 项目API
│   │   │   ├── tasks.ts   # 工单API
│   │   │   ├── materials.ts # 材料API
│   │   │   ├── work-items.ts # 工作内容API
│   │   │   ├── teams.ts   # 团队API
│   │   │   ├── users.ts   # 用户API
│   │   │   └── statistics.ts # 统计API
│   │   ├── contexts/      # 上下文
│   │   │   └── AuthContext.tsx # 认证上下文
│   │   ├── layouts/       # 布局组件
│   │   │   ├── AdminLayout.tsx # 管理员布局
│   │   │   ├── MobileLayout.tsx # 移动端布局
│   │   │   └── PCLayout.tsx # PC端布局
│   │   ├── pages/         # 页面组件
│   │   │   ├── admin/     # 管理员页面
│   │   │   │   ├── Dashboard.tsx # 仪表盘
│   │   │   │   ├── Projects.tsx # 项目管理
│   │   │   │   ├── Materials.tsx # 材料管理
│   │   │   │   ├── WorkItems.tsx # 工作内容管理
│   │   │   │   ├── Teams.tsx # 团队管理
│   │   │   │   ├── Statistics.tsx # 统计分析
│   │   │   │   └── Users.tsx # 用户管理
│   │   │   ├── mobile/    # 移动端页面
│   │   │   │   ├── MobileHome.tsx # 首页
│   │   │   │   ├── MobileTasks.tsx # 工单列表
│   │   │   │   ├── MobileTaskDetail.tsx # 工单详情
│   │   │   │   ├── MobileTaskComplete.tsx # 工单完成
│   │   │   │   └── MobileCompleted.tsx # 已完成工单
│   │   │   ├── pc/        # PC端页面
│   │   │   │   ├── PCHome.tsx # 首页
│   │   │   │   ├── PCTasks.tsx # 工单列表
│   │   │   │   └── PCTaskDetail.tsx # 工单详情
│   │   │   ├── Login.tsx  # 登录页面
│   │   │   └── Register.tsx # 注册页面
│   │   ├── components/    # 通用组件
│   │   │   └── ImportModal.tsx # 批量导入模态框
│   │   ├── utils/         # 工具函数
│   │   │   ├── auth.ts    # 认证工具
│   │   │   └── device.ts  # 设备检测
│   │   ├── App.tsx        # 应用入口
│   │   └── main.tsx       # 主渲染文件
│   ├── public/            # 静态资源
│   └── vite.config.ts     # Vite配置
├── logs/                  # 日志文件
├── requirements.txt       # Python依赖
├── run.py                 # 启动脚本
├── test.py                # 测试脚本
├── check_db_structure.py  # 数据库结构检查工具
├── fix_db_structure.py    # 数据库结构修复工具
├── check_work_items.py    # 工作内容检查工具
├── init_work_items.py     # 工作内容初始化工具
└── batch_add_work_items.py # 批量添加工作内容工具
```

## 数据流

### 前端到后端的数据流

1. 用户在前端界面进行操作
2. 前端组件调用API层的函数
3. API层发送HTTP请求到后端
4. 后端路由层接收请求
5. 路由层使用模式层验证请求数据
6. 路由层调用模型层进行数据库操作
7. 模型层返回结果给路由层
8. 路由层使用模式层序列化响应数据
9. 路由层返回HTTP响应
10. 前端API层接收响应
11. 前端组件更新UI

### 批量导入数据流

1. 用户在前端选择CSV文件
2. 前端发送文件到后端导入API
3. 后端接收文件并解析CSV数据
4. 后端验证数据格式和内容
5. 后端将数据保存到数据库
6. 后端返回导入结果
7. 前端显示导入结果

## 组件交互

### 认证流程

1. 用户输入用户名和密码
2. 前端发送登录请求
3. 后端验证用户名和密码
4. 后端生成JWT令牌
5. 前端保存令牌到localStorage
6. 前端更新认证上下文
7. 前端根据用户角色导航到相应页面

### 工单管理流程

1. 用户创建工单
2. 系统分配工单给施工人员
3. 施工人员接单
4. 施工人员完成工作
5. 施工人员提交完成信息
6. 系统更新工单状态
7. 系统计算费用

## 技术选择理由

### 后端技术

- **FastAPI**: 高性能、易于使用的现代Python Web框架，支持异步请求处理和自动文档生成
- **SQLAlchemy**: 功能强大的ORM工具，简化数据库操作，支持复杂查询和关系定义
- **Pydantic**: 提供数据验证和序列化功能，与FastAPI无缝集成
- **JWT**: 提供无状态的用户认证机制，适合前后端分离架构

### 前端技术

- **React**: 组件化UI库，支持函数式组件和Hooks，提高代码复用性和可维护性
- **TypeScript**: 提供静态类型检查，减少运行时错误，提高代码质量
- **Ant Design**: 提供丰富的UI组件，支持响应式设计，加速开发
- **Vite**: 现代前端构建工具，提供快速的开发体验和优化的生产构建
