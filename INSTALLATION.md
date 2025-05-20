# 安装和运行指南

本文档提供了维修项目管理系统的详细安装步骤和运行说明。

## 安装方式

维修项目管理系统提供两种安装方式：
1. 使用Docker（推荐）
2. 本地安装

## 方式一：使用Docker（推荐）

使用Docker是最简单的方式，无需安装Python和Node.js环境。

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+

### 安装步骤

1. 克隆代码仓库（如果尚未克隆）
```bash
git clone https://github.com/licx506/repair-management-system.git
cd repair-management-system
```

2. 使用提供的脚本启动系统
```bash
bash docker-run.sh
```

或者手动使用Docker Compose启动
```bash
# 创建必要的目录
mkdir -p data logs uploads

# 构建并启动容器
docker-compose up -d
```

3. 创建管理员用户
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

4. 访问系统
   - 系统访问地址: http://localhost:8458

### 停止系统

使用提供的脚本停止系统
```bash
bash docker-stop.sh
```

或者手动使用Docker Compose停止
```bash
docker-compose down
```

### Docker数据持久化

Docker部署方式会将以下数据持久化到宿主机：
- 数据库文件: `./data`
- 日志文件: `./logs`
- 上传文件: `./uploads`

## 方式二：本地安装

如果您希望在本地开发环境中运行，可以按照以下步骤操作。

### 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

### 安装依赖

#### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```bash
cd frontend
npm install
```

## 环境准备

为了确保系统能够正常运行，请确保安装了以下关键依赖：

### 后端关键依赖

- FastAPI: Web框架
- SQLAlchemy: ORM工具
- Uvicorn: ASGI服务器
- Passlib: 密码哈希
- Email-validator: 邮箱验证

### 前端关键依赖

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

## 运行应用

### 使用启动脚本

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

## 部署说明

### 方式一：使用Docker部署（推荐）

使用Docker部署是最简单的方式，适合生产环境。

1. 克隆代码仓库
```bash
git clone https://github.com/licx506/repair-management-system.git
cd repair-management-system
```

2. 修改docker-compose.yml（可选）
```yaml
# 如果需要修改端口，可以编辑docker-compose.yml文件
# 例如，将8458端口改为80端口
ports:
  - "80:80"
```

3. 构建并启动容器
```bash
docker-compose up -d
```

4. 配置外部访问（如果需要）
   - 如果需要从外部访问系统，可以配置反向代理（如Nginx）指向Docker容器
   - 或者直接修改docker-compose.yml中的端口映射

5. 备份数据
```bash
# 备份数据库
cp -r data /backup/data_$(date +%Y%m%d)

# 备份上传文件
cp -r uploads /backup/uploads_$(date +%Y%m%d)
```

### 方式二：传统部署

#### 前端部署

1. 构建前端生产版本：

```bash
cd frontend
npm run build
```

2. 将生成的`dist`目录部署到Web服务器。

#### 后端部署

1. 使用生产级ASGI服务器（如Gunicorn）运行后端：

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

2. 配置反向代理（如Nginx）指向后端服务。

#### 外部访问配置

如果需要从外部访问系统，需要修改以下配置：

1. 在`backend/main.py`中添加允许的域名：

```python
origins = [
    "http://localhost:8458",
    "http://your-domain.com",
    "http://your-ip-address:8458"
]
```

2. 在`frontend/vite.config.ts`中添加服务器配置：

```typescript
server: {
  port: 8458,
  host: '0.0.0.0',
  allowedHosts: ['your-domain.com', 'your-ip-address']
}
```

### Docker部署的优势

1. **环境一致性**：Docker确保开发、测试和生产环境的一致性
2. **简化部署**：一键部署，无需手动配置环境
3. **隔离性**：应用程序和依赖项在容器中运行，不会影响宿主机
4. **可移植性**：可以在任何支持Docker的系统上运行
5. **易于扩展**：可以轻松扩展到多个容器
6. **版本控制**：可以轻松回滚到之前的版本

## 数据库初始化

系统使用SQLite数据库，首次运行时会自动创建数据库文件。如果需要重新初始化数据库，可以删除`backend/repair_management.db`文件，然后重新启动后端。

## 数据库结构检查和修复

如果遇到数据库结构问题，可以使用以下工具：

```bash
# 检查数据库结构
python check_db_structure.py

# 修复数据库结构
python fix_db_structure.py
```

## 批量导入数据

系统提供了批量导入功能，可以通过以下方式使用：

1. 在管理员界面中使用批量导入功能
2. 使用提供的批量导入工具：

```bash
# 批量导入工作内容
python batch_add_work_items.py --username admin --password admin123
```

## 更多信息

如果在安装或运行过程中遇到问题，请参考[故障排除](TROUBLESHOOTING.md)文档。
