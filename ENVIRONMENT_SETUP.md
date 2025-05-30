# 环境初始化和检测指南

本文档详细说明了维修项目管理系统的环境初始化和检测流程。

## 概述

我们提供了两个脚本来简化环境配置过程：

1. **`init_environment.sh`** - 自动化环境初始化脚本
2. **`check_environment.py`** - 环境检测和验证脚本

## 环境初始化脚本 (init_environment.sh)

### 功能特性

- **跨平台支持**：自动检测操作系统类型（CentOS/RHEL、Ubuntu/Debian、Arch Linux等）
- **智能包管理**：自动选择合适的包管理器（dnf、yum、apt、pacman）
- **版本管理**：确保安装符合要求的软件版本
- **依赖管理**：自动安装和配置所有必需的依赖
- **错误处理**：提供详细的错误信息和解决建议

### 安装的组件

#### 系统依赖
- Python 3.8+
- Node.js 18+
- npm
- git
- curl
- wget
- 编译工具链（gcc、make等）
- SQLite

#### Python依赖
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- python-jose
- passlib
- python-multipart
- 其他requirements.txt中的依赖

#### 前端依赖
- React
- Ant Design
- Axios
- React Router
- 其他package.json中的依赖

### 使用方法

```bash
# 使用root权限运行（推荐）
sudo bash init_environment.sh

# 或者普通用户运行（需要手动安装系统依赖）
bash init_environment.sh
```

### 执行流程

1. **系统检测**：检测操作系统类型和版本
2. **包管理器配置**：选择合适的包管理器
3. **系统更新**：更新系统包列表
4. **系统依赖安装**：安装基础系统依赖
5. **Python环境配置**：安装Python和pip
6. **Node.js环境配置**：安装Node.js和npm
7. **目录创建**：创建必要的项目目录
8. **Python依赖安装**：安装后端依赖
9. **前端依赖安装**：安装前端依赖
10. **数据库初始化**：初始化SQLite数据库
11. **环境测试**：验证安装结果
12. **使用说明**：显示后续操作指南

## 环境检测脚本 (check_environment.py)

### 功能特性

- **全面检测**：检查所有必需的环境组件
- **详细报告**：生成完整的环境状态报告
- **问题诊断**：识别常见问题并提供解决建议
- **彩色输出**：使用颜色区分不同状态信息

### 检测项目

#### Python环境
- Python版本（要求3.8+）
- pip可用性
- 必需的Python包

#### Node.js环境
- Node.js版本（要求16+，推荐18+）
- npm版本和可用性

#### 系统依赖
- git
- curl
- wget

#### 项目结构
- 关键文件存在性
- 目录结构完整性

#### 依赖状态
- Python依赖包安装状态
- 前端依赖配置状态

#### 运行环境
- 端口占用情况（8000、8458）
- 数据库文件状态

### 使用方法

```bash
# 在项目根目录运行
python3 check_environment.py
```

### 输出示例

```
维修项目管理系统环境检测
============================================================
[INFO] 生成环境检测报告...

============================================================
环境检测报告
============================================================

Python环境:
------------------------------
[SUCCESS] Python版本: 3.9.21 ✓
[SUCCESS] pip已安装 ✓

Node.js环境:
------------------------------
[SUCCESS] Node.js版本: v18.20.8 ✓
[SUCCESS] npm版本: 10.8.2 ✓

...

============================================================
检测结果汇总:
============================================================
Python环境: ✓ 通过
Node.js环境: ✓ 通过
系统依赖: ✓ 通过
项目结构: ✓ 通过
Python依赖: ✓ 通过
前端依赖: ✓ 通过
端口检查: ✓ 通过
数据库检查: ✓ 通过

============================================================
[SUCCESS] 所有检查都通过！系统可以正常运行。

启动系统:
python3 run.py
============================================================
```

## 常见问题和解决方案

### Node.js版本问题

**问题**：Node.js版本过低或esbuild平台不匹配

**解决方案**：
```bash
# 自动升级Node.js
sudo bash init_environment.sh

# 或手动升级
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install nodejs -y
```

### Python依赖问题

**问题**：某些Python包未安装

**解决方案**：
```bash
# 安装所有依赖
python3 -m pip install -r requirements.txt

# 或安装特定包
python3 -m pip install fastapi uvicorn sqlalchemy
```

### 前端依赖问题

**问题**：前端依赖安装失败或版本不匹配

**解决方案**：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 端口占用问题

**问题**：端口8000或8458被占用

**解决方案**：
```bash
# 查看占用进程
sudo netstat -tlnp | grep :8000
sudo ss -tlnp | grep :8000

# 停止占用进程
sudo kill -9 <PID>

# 或修改配置使用其他端口
```

### 权限问题

**问题**：没有权限安装系统依赖

**解决方案**：
```bash
# 使用sudo运行初始化脚本
sudo bash init_environment.sh

# 或手动安装系统依赖后运行
bash init_environment.sh
```

## 最佳实践

### 1. 使用虚拟环境

```bash
# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 在虚拟环境中安装依赖
pip install -r requirements.txt
```

### 2. 定期检查环境

```bash
# 定期运行环境检测
python3 check_environment.py
```

### 3. 保持依赖更新

```bash
# 更新Python依赖
pip install --upgrade -r requirements.txt

# 更新前端依赖
cd frontend && npm update
```

### 4. 备份配置

在进行环境变更前，建议备份重要配置文件：
- `frontend/vite.config.ts`
- `backend/database.py`
- 数据库文件

## 支持的操作系统

### 已测试的系统

- **CentOS/RHEL 8+**：使用dnf包管理器
- **CentOS/RHEL 7**：使用yum包管理器
- **Ubuntu 18.04+**：使用apt包管理器
- **Debian 10+**：使用apt包管理器
- **Arch Linux**：使用pacman包管理器

### 系统要求

- **最小内存**：2GB RAM
- **存储空间**：5GB可用空间
- **网络**：需要互联网连接下载依赖
- **权限**：建议使用root权限运行初始化脚本

## 故障排除

如果遇到问题，请按以下步骤排查：

1. **运行环境检测**：`python3 check_environment.py`
2. **查看详细日志**：检查脚本输出的错误信息
3. **检查网络连接**：确保可以访问软件源
4. **验证权限**：确保有足够的权限安装软件
5. **查看系统日志**：检查系统日志中的相关错误

如果问题仍然存在，请提供以下信息：
- 操作系统版本
- 错误信息
- 环境检测报告
- 相关日志文件
