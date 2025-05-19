# 维修项目管理系统

这是一个维修项目管理的Web应用，支持PC端和移动端，具有工单管理、材料跟踪和管理功能。

> **最新更新**: 前端服务端口已更改为8458，详细更新内容请查看[最新更新内容](#最新更新内容)部分。

## 功能特点

- 响应式设计，适配手机端和PC端
- 工单管理：查看维修列表，接单，转派，回单
- 材料管理：支持甲供和自购材料
- 工作内容管理：可配置工作内容清单
- 统计分析：项目完成情况，工作量汇总，材料汇总
- 施工队管理：管理施工人员和施工队伍

## 技术栈

- 前端：React + TypeScript + Ant Design
- 后端：Python + FastAPI + SQLAlchemy
- 数据库：SQLite

## 安装和运行

### 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

### 安装依赖

1. 安装后端依赖

```bash
pip install -r requirements.txt
```

2. 安装前端依赖

```bash
cd frontend
npm install
```

### 环境准备

为了确保系统能够正常运行，请确保安装了以下关键依赖：

1. 后端关键依赖：
   - FastAPI: Web框架
   - SQLAlchemy: ORM工具
   - Uvicorn: ASGI服务器
   - Passlib: 密码哈希
   - Email-validator: 邮箱验证

2. 前端关键依赖：
   - React: UI库
   - Ant Design: 组件库
   - Axios: HTTP客户端
   - React Router: 路由管理
   - Dayjs: 日期处理库
   - ECharts: 图表库

如果在运行过程中遇到依赖相关的错误，可以尝试手动安装缺失的依赖：

```bash
# 后端依赖
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart email-validator

# 前端依赖
cd frontend
npm install dayjs axios react-router-dom antd @ant-design/icons @ant-design/pro-components echarts echarts-for-react
```

### 运行应用

使用提供的启动脚本一键启动：

```bash
python run.py
```

或者分别启动前后端：

```bash
# 只启动后端
python run.py --backend-only

# 只启动前端
python run.py --frontend-only
```

启动后，可通过以下地址访问：
- 前端: http://localhost:8458 (已从默认的5173端口更改)
- 后端: http://localhost:8000

### 创建管理员用户

```bash
python run.py --create-admin
```

这将创建一个管理员用户，用户名：`admin`，密码：`admin123`

## 测试

运行测试脚本：

```bash
python test.py
```

## 常见问题及修复

### 1. 导入路径问题

如果遇到 `ModuleNotFoundError: No module named 'backend'` 错误，需要修复后端代码中的导入路径。

可以使用提供的修复脚本：

```bash
python fix_imports.py
```

这个脚本会自动将所有 `from backend.xxx` 的导入修改为 `from xxx`。

### 2. 类型导入问题

如果遇到 `The requested module does not provide an export named 'XXX'` 错误，需要修改前端代码中的类型导入方式。

例如，将：
```typescript
import { Task } from '../../api/tasks';
```

修改为：
```typescript
import type { Task } from '../../api/tasks';
```

### 3. 日期验证问题

如果遇到 `Uncaught TypeError: date.isValid is not a function` 错误，需要确保正确使用 dayjs 处理日期。

1. 确保已安装 dayjs：
```bash
cd frontend
npm install dayjs
```

2. 在使用 DatePicker 组件的文件中导入 dayjs：
```typescript
import dayjs from 'dayjs';
```

3. 使用 dayjs 对象而不是 JavaScript 的 Date 对象：
```typescript
// 修改前
const [dateRange, setDateRange] = useState<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 30)),
  new Date()
]);

// 修改后
const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
  dayjs().subtract(30, 'day'),
  dayjs()
]);
```

4. 在 RangePicker 组件中直接使用 dayjs 对象：
```typescript
<RangePicker
  value={dateRange}
  onChange={(dates) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([dates[0], dates[1]]);
    }
  }}
/>
```

## 数据库关系

系统中的主要实体之间存在以下关系：

1. **维修项目 ↔ 工单**：一对多关系
   - 一个维修项目可以包含多个工单
   - 每个工单必须属于一个维修项目

2. **施工人员 ↔ 施工队伍**：多对一关系
   - 一个施工队伍可以包含多个施工人员
   - 每个施工人员只能属于一个施工队伍

3. **维修项目 ↔ 施工队伍**：多对多关系
   - 一个维修项目可以由多个施工队伍负责
   - 一个施工队伍可以负责多个维修项目

4. **工单 ↔ 施工人员**：多对多关系
   - 一个工单可以由多个施工人员共同完成
   - 一个施工人员可以同时处理多个工单

## 项目结构

```
.
├── backend/                # 后端代码
│   ├── main.py            # 主应用入口
│   ├── database.py        # 数据库配置
│   ├── models/            # 数据模型
│   ├── routers/           # API路由
│   ├── schemas/           # Pydantic模型
│   └── utils/             # 工具函数
├── frontend/              # 前端代码
│   ├── src/               # 源代码
│   │   ├── api/           # API调用
│   │   ├── components/    # 组件
│   │   ├── contexts/      # 上下文
│   │   ├── layouts/       # 布局组件
│   │   ├── pages/         # 页面组件
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
├── requirements.txt       # Python依赖
├── run.py                 # 启动脚本
└── test.py                # 测试脚本
```

## 用户角色

- 管理员：可以管理所有内容，包括项目、工单、材料、工作内容、施工队等
- 项目经理：可以创建项目，分配工单，查看统计信息
- 施工人员：可以接单、转派、回单

## 最新更新内容

### 2025年5月19日更新

1. **数据库关系更新**
   - 明确了系统中的主要实体关系
   - 维修项目与工单：一对多关系
   - 施工人员与施工队伍：多对一关系
   - 维修项目与施工队伍：多对多关系
   - 工单与施工人员：多对多关系
   - 添加了数据库关系文档

### 2025年5月18日更新

1. **前端端口配置**
   - 前端服务端口已从默认的5173修改为8458
   - 修改了Vite配置文件，添加了自定义端口设置
   - 更新了启动脚本中的端口显示信息

2. **CORS配置更新**
   - 后端CORS配置已更新，添加了对新前端端口(8458)的支持
   - 解决了跨域请求问题，确保前后端通信正常

3. **管理功能增强**
   - 添加了材料管理页面，支持材料的增删改查
   - 添加了工作内容管理页面，可配置不同类型的工作内容
   - 添加了施工队伍管理页面，支持团队和成员管理
   - 添加了统计分析页面，提供多维度数据可视化

4. **兼容性说明**
   - 系统现在使用React 19，而Ant Design v5官方支持React 16-18
   - 虽然会显示兼容性警告，但功能正常运行
   - 如需消除警告，可考虑降级React版本至18

## 故障排除

如果在运行系统时遇到问题，可以尝试以下步骤：

1. **后端启动失败**
   - 检查Python版本是否为3.8+
   - 确保所有依赖都已正确安装
   - 检查导入路径问题（参见"常见问题及修复"部分）
   - 查看后端日志以获取详细错误信息

2. **前端启动失败**
   - 检查Node.js版本是否为14+
   - 确保所有依赖都已正确安装
   - 检查类型导入问题（参见"常见问题及修复"部分）
   - 查看浏览器控制台以获取详细错误信息

3. **数据库问题**
   - 确保SQLite数据库文件存在且有正确的权限
   - 如果数据库结构有问题，可以删除数据库文件并重新启动后端，系统会自动创建新的数据库

4. **API请求失败**
   - 确保后端服务正在运行
   - 检查API请求的URL是否正确
   - 检查认证令牌是否有效
   - 使用浏览器开发者工具查看网络请求的详细信息
   - 确认CORS配置正确，特别是当修改端口后

5. **UI显示问题**
   - 确保前端依赖正确安装，特别是Ant Design和dayjs
   - 检查浏览器兼容性，推荐使用最新版本的Chrome或Firefox
   - 清除浏览器缓存并刷新页面

## 许可证

[MIT](LICENSE)
