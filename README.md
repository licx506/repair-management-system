# 维修项目管理系统

这是一个维修项目管理的Web应用，支持PC端和移动端，具有工单管理、材料跟踪和管理功能。

> **最新更新**: 添加了批量导入功能，详细更新内容请查看[更新日志](CHANGELOG.md)。

## 功能特点

- 响应式设计，适配手机端和PC端
- 工单管理：查看维修列表，接单，转派，回单
- 材料管理：支持甲供和自购材料
- 工作内容管理：可配置工作内容清单
- 统计分析：项目完成情况，工作量汇总，材料汇总
- 施工队管理：管理施工人员和施工队伍
- 批量导入：支持工单、材料、工作内容和用户的批量导入

## 技术栈

### 前端技术

- **框架**：React 19
- **语言**：TypeScript 5.0+
- **UI组件库**：Ant Design 5.x
- **构建工具**：Vite 4.x
- **路由**：React Router 6.x
- **HTTP客户端**：Axios
- **状态管理**：React Context API
- **图表库**：ECharts 5.x
- **日期处理**：Day.js

### 后端技术

- **语言**：Python 3.8+
- **Web框架**：FastAPI 0.95+
- **ORM**：SQLAlchemy 2.0+
- **数据验证**：Pydantic 2.0+
- **认证**：JWT (JSON Web Tokens)
- **密码哈希**：Bcrypt
- **ASGI服务器**：Uvicorn

### 数据库

- **数据库系统**：SQLite 3
- **迁移工具**：SQLAlchemy原生迁移

## 文档导航

- [安装和运行指南](INSTALLATION.md) - 详细的安装步骤和运行说明
- [API文档](API.md) - 系统提供的所有API端点
- [架构文档](ARCHITECTURE.md) - 代码架构和项目结构
- [数据库文档](DATABASE.md) - 数据库关系和表结构
- [故障排除](TROUBLESHOOTING.md) - 常见问题和解决方案
- [更新日志](CHANGELOG.md) - 版本更新历史

## 快速开始

### 方式一：使用Docker（推荐）

使用Docker是最简单的方式，无需安装Python和Node.js环境。

#### 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

#### 启动应用

```bash
# 启动系统
bash docker-run.sh

# 或者直接使用docker-compose
docker-compose up -d
```

启动后，可通过以下地址访问：
- 系统访问地址: http://localhost:8458

#### 创建管理员用户

```bash
# 在docker-run.sh脚本中会提示是否创建管理员用户
# 或者手动执行以下命令
docker exec -it repair-management-backend python -c "
import sqlite3
from passlib.context import CryptContext
conn = sqlite3.connect('repair_management.db')
cursor = conn.cursor()
cursor.execute(\"SELECT * FROM users WHERE username = 'admin'\")
if not cursor.fetchone():
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    hashed_password = pwd_context.hash('admin123')
    cursor.execute(\"INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)\", ('admin', 'admin@example.com', hashed_password, '管理员', 'admin', 1))
    conn.commit()
    print('管理员用户已创建')
else:
    print('管理员用户已存在')
conn.close()
"
```

#### 停止应用

```bash
# 停止系统
bash docker-stop.sh

# 或者直接使用docker-compose
docker-compose down
```

### 方式二：本地安装

如果您希望在本地开发环境中运行，可以按照以下步骤操作。

#### 安装依赖

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

#### 运行应用

```bash
# 一键启动前后端
python run.py

# 或者分别启动
python run.py --backend-only  # 只启动后端
python run.py --frontend-only # 只启动前端
```

启动后，可通过以下地址访问：
- 前端: http://localhost:8458
- 后端: http://localhost:8000

#### 创建管理员用户

```bash
python run.py --create-admin
```

这将创建一个管理员用户，用户名：`admin`，密码：`admin123`

## 用户角色

- **管理员**：可以管理所有内容，包括项目、工单、材料、工作内容、施工队等
- **项目经理**：可以创建项目，分配工单，查看统计信息
- **施工人员**：可以接单、转派、回单

## 许可证

[MIT](LICENSE)
