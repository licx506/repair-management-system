# 登录网络错误修复记录

## 问题描述

在Docker环境下运行系统后，打开首页登录时出现以下错误：

```
API响应错误: Object
code: "ERR_NETWORK"
data: undefined
message: "Network Error"
method: "post"
stack: "AxiosError: Network Error\n    at m.onerror (http://arm.work.gd:8458/assets/index-thRmhLDE.js:484:6097)"
status: undefined
url: "/auth/token"
```

## 问题分析

通过分析系统日志和代码，发现了以下问题：

1. 数据库结构问题：后端日志显示数据库查询错误 `no such column: tasks.company_material_cost`，表明数据库结构与代码不匹配。

2. 前端API请求错误：前端尝试访问 `/auth/token` 端点时出现网络错误，可能是由于后端服务不可用或网络连接问题。

3. 前端API配置问题：前端配置使用了绝对URL，可能导致跨域问题。

## 修复步骤

### 1. 修复数据库结构

修改 `fix_db_structure.py` 脚本，添加缺少的数据库列：

```python
# 添加以下列到 tasks 表
if "company_material_cost" not in columns:
    missing_columns.append(("company_material_cost", "FLOAT DEFAULT 0.0"))
if "self_material_cost" not in columns:
    missing_columns.append(("self_material_cost", "FLOAT DEFAULT 0.0"))
if "total_cost" not in columns:
    missing_columns.append(("total_cost", "FLOAT DEFAULT 0.0"))
```

运行修复脚本：

```bash
python fix_db_structure.py
```

脚本执行结果：
```
数据库路径: /home/aaa/backend/repair_management.db
备份数据库到 /home/aaa/backend/repair_management.db.bak
tasks表缺少以下列: ['attachment', 'work_list', 'company_material_list', 'self_material_list', 'labor_cost', 'material_cost', 'company_material_cost', 'self_material_cost']
添加列 attachment (VARCHAR)
添加列 work_list (VARCHAR)
添加列 company_material_list (VARCHAR)
添加列 self_material_list (VARCHAR)
添加列 labor_cost (FLOAT DEFAULT 0.0)
添加列 material_cost (FLOAT DEFAULT 0.0)
添加列 company_material_cost (FLOAT DEFAULT 0.0)
添加列 self_material_cost (FLOAT DEFAULT 0.0)
tasks表结构修复完成
数据库结构修复完成
```

### 2. 修复前端API配置

修改 `frontend/src/utils/config.ts` 文件，将API配置从绝对URL改为相对路径：

```typescript
// 默认配置
const defaultConfig = {
  // API服务器地址 - 使用相对路径避免跨域问题
  apiBaseUrl: '',
  // 模板文件服务器地址 - 使用相对路径避免跨域问题
  templateBaseUrl: '',
  // 其他配置项可以在这里添加
};
```

### 3. 重新构建和启动Docker容器

```bash
docker-compose down && docker-compose build && docker-compose up -d
```

## 修复结果

1. 数据库结构已更新，添加了缺少的列。
2. 前端API配置已修改为使用相对路径，避免了跨域问题。
3. 系统重新部署后，登录功能正常工作，不再出现网络错误。

## 预防措施

1. 在进行数据库模型更改时，确保同步更新数据库结构。
2. 使用相对路径配置API请求，避免跨域问题。
3. 在部署前进行完整的测试，确保所有功能正常工作。

## 修复日期

2025年5月21日
