# Docker部署说明

本目录包含维修项目管理系统的Docker部署相关文件。

## 文件说明

- `nginx.conf`: Nginx配置文件，用于前端容器
- `../docker-compose.yml`: Docker Compose配置文件
- `../backend/Dockerfile`: 后端Docker镜像构建文件
- `../frontend/Dockerfile`: 前端Docker镜像构建文件
- `../docker-run.sh`: 系统启动脚本
- `../docker-stop.sh`: 系统停止脚本

## 快速部署

1. 确保已安装Docker和Docker Compose
2. 在项目根目录执行以下命令启动系统：

```bash
bash docker-run.sh
```

或者手动执行：

```bash
docker-compose up -d
```

3. 访问系统：http://localhost:8458

## 自定义配置

### 修改端口

如果需要修改访问端口，编辑`docker-compose.yml`文件：

```yaml
services:
  frontend:
    ports:
      - "自定义端口:80"  # 例如 "80:80"
```

### 修改数据存储路径

默认情况下，数据存储在项目根目录的`data`、`logs`和`uploads`目录中。如果需要修改，编辑`docker-compose.yml`文件：

```yaml
services:
  backend:
    volumes:
      - /自定义路径/data:/app/data
      - /自定义路径/logs:/app/logs
      - /自定义路径/uploads:/app/uploads
```

### 修改API地址

如果需要修改API地址，需要在前端构建前修改`frontend/src/utils/config.ts`文件：

```typescript
const defaultConfig = {
  apiBaseUrl: 'http://your-domain.com',
  templateBaseUrl: 'http://your-domain.com',
};
```

然后重新构建Docker镜像：

```bash
docker-compose build
docker-compose up -d
```

## 常见问题

### 1. 容器无法启动

检查Docker日志：

```bash
docker-compose logs
```

### 2. 无法访问系统

检查端口映射是否正确：

```bash
docker-compose ps
```

### 3. 数据持久化问题

确保volumes配置正确，并且宿主机目录有正确的权限：

```bash
ls -la data logs uploads
```

## 备份与恢复

### 备份数据

```bash
# 备份数据库和上传文件
tar -czvf backup_$(date +%Y%m%d).tar.gz data uploads
```

### 恢复数据

```bash
# 停止容器
docker-compose down

# 恢复数据
tar -xzvf backup_20250519.tar.gz

# 重新启动容器
docker-compose up -d
```
