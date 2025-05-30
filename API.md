# 维修项目管理系统 API 文档

本文档详细列出了维修项目管理系统提供的所有API端点，包括请求参数、响应格式、错误处理等详细信息。

## 基础信息

### 基础URL
- **开发环境**: `http://localhost:8000`
- **生产环境**: `http://xin.work.gd:8000`
- **API前缀**: `/api`

所有API端点都以`/api`为前缀。例如，完整的登录API URL是`http://localhost:8000/api/auth/token`。

### 认证机制

除了登录、注册API和健康检查API外，所有API都需要认证。认证使用JWT令牌，需要在HTTP请求头中添加`Authorization`字段：

```http
Authorization: Bearer {access_token}
```

其中`{access_token}`是通过登录API获取的访问令牌。

### CORS配置

后端已配置CORS以支持前端域名`arm.work.gd`的跨域访问。

### 响应格式

所有API响应都使用JSON格式，包含以下标准字段：
- 成功响应：直接返回数据或包含`message`字段
- 错误响应：包含`detail`字段描述错误信息

### 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 删除成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

## 基础API

### 根端点

- **URL**: `/`
- **方法**: `GET`
- **描述**: 返回API服务器欢迎信息
- **响应**:
  ```json
  {
    "message": "欢迎使用维修项目管理系统API"
  }
  ```

### 健康检查

- **URL**: `/api/health`
- **方法**: `GET`
- **描述**: 简单的健康检查端点
- **响应**:
  ```json
  {
    "status": "healthy"
  }
  ```

## 认证相关API

### 用户登录

- **URL**: `/api/auth/token`
- **方法**: `POST`
- **描述**: 用户登录，获取访问令牌
- **认证**: 无需认证
- **请求体**: 表单数据 (application/x-www-form-urlencoded)
  ```
  username=admin&password=admin123
  ```
- **成功响应** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
- **错误响应** (401):
  ```json
  {
    "detail": "用户名或密码错误"
  }
  ```

### 用户注册

- **URL**: `/api/auth/register`
- **方法**: `POST`
- **描述**: 用户注册，创建新用户账户
- **认证**: 无需认证
- **请求体**:
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "full_name": "New User",
    "phone": "13800000000",
    "role": "worker"
  }
  ```
- **字段说明**:
  - `username`: 用户名，必填，唯一
  - `password`: 密码，必填
  - `email`: 邮箱，必填，唯一，格式验证
  - `full_name`: 全名，可选
  - `phone`: 电话号码，可选
  - `role`: 角色，可选，默认为"worker"，可选值：admin、manager、worker
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "full_name": "New User",
    "phone": "13800000000",
    "role": "worker",
    "is_active": true
  }
  ```
- **错误响应** (400):
  ```json
  {
    "detail": "用户名已被注册"
  }
  ```

### 获取当前用户信息

- **URL**: `/api/auth/me`
- **方法**: `GET`
- **描述**: 获取当前登录用户的详细信息
- **认证**: 需要Bearer Token
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "phone": "13800000000",
    "role": "admin",
    "is_active": true
  }
  ```
- **错误响应** (401):
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

## 维修项目API

### 获取项目列表

- **URL**: `/api/projects/`
- **方法**: `GET`
- **描述**: 获取项目列表，支持分页和状态筛选
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100，最大1000
  - `status`: 项目状态筛选，可选值：pending、in_progress、completed、cancelled
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "title": "办公楼网络维修",
      "description": "办公楼网络设备故障维修",
      "location": "北京市朝阳区",
      "contact_name": "张三",
      "contact_phone": "13800000000",
      "status": "in_progress",
      "priority": 1,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T15:30:00",
      "completed_at": null,
      "created_by_id": 1
    }
  ]
  ```

### 创建新项目

- **URL**: `/api/projects/`
- **方法**: `POST`
- **描述**: 创建新的维修项目
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "title": "办公楼网络维修",
    "description": "办公楼网络设备故障维修",
    "location": "北京市朝阳区",
    "contact_name": "张三",
    "contact_phone": "13800000000",
    "priority": 1
  }
  ```
- **字段说明**:
  - `title`: 项目标题，必填
  - `description`: 项目描述，可选
  - `location`: 项目地点，必填
  - `contact_name`: 联系人姓名，必填
  - `contact_phone`: 联系人电话，必填
  - `priority`: 优先级，可选，默认1，数值越小优先级越高
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "title": "办公楼网络维修",
    "description": "办公楼网络设备故障维修",
    "location": "北京市朝阳区",
    "contact_name": "张三",
    "contact_phone": "13800000000",
    "status": "pending",
    "priority": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": null,
    "completed_at": null,
    "created_by_id": 1
  }
  ```

### 获取项目详情

- **URL**: `/api/projects/{project_id}`
- **方法**: `GET`
- **描述**: 获取指定项目的详细信息，包括任务统计
- **认证**: 需要Bearer Token
- **路径参数**:
  - `project_id`: 项目ID
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "title": "办公楼网络维修",
    "description": "办公楼网络设备故障维修",
    "location": "北京市朝阳区",
    "contact_name": "张三",
    "contact_phone": "13800000000",
    "status": "in_progress",
    "priority": 1,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T15:30:00",
    "completed_at": null,
    "created_by_id": 1,
    "tasks_count": 5,
    "completed_tasks_count": 2
  }
  ```
- **错误响应** (404):
  ```json
  {
    "detail": "项目不存在"
  }
  ```

### 更新项目信息

- **URL**: `/api/projects/{project_id}`
- **方法**: `PUT`
- **描述**: 更新指定项目的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `project_id`: 项目ID
- **请求体**:
  ```json
  {
    "title": "办公楼网络维修（更新）",
    "description": "办公楼网络设备故障维修，增加路由器更换",
    "location": "北京市朝阳区",
    "contact_name": "张三",
    "contact_phone": "13800000000",
    "status": "completed",
    "priority": 1
  }
  ```
- **字段说明**: 所有字段都是可选的，只更新提供的字段
- **成功响应** (200): 返回更新后的项目信息
- **错误响应** (404):
  ```json
  {
    "detail": "项目不存在"
  }
  ```

### 删除项目

- **URL**: `/api/projects/{project_id}`
- **方法**: `DELETE`
- **描述**: 删除指定项目
- **认证**: 需要Bearer Token
- **路径参数**:
  - `project_id`: 项目ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "项目不存在"
  }
  ```

## 工单管理API

### 获取工单列表

- **URL**: `/api/tasks/`
- **方法**: `GET`
- **描述**: 获取工单列表，支持多种筛选条件
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100
  - `status`: 工单状态筛选，可选值：pending、assigned、in_progress、completed、cancelled
  - `project_id`: 项目ID筛选
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "title": "网络设备检修",
      "description": "检查并维修网络设备",
      "project_id": 1,
      "assigned_to_id": 2,
      "status": "in_progress",
      "priority": 1,
      "estimated_hours": 4.0,
      "actual_hours": null,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T14:00:00",
      "completed_at": null,
      "created_by_id": 1,
      "materials": "[]",
      "work_items": "[]"
    }
  ]
  ```

### 获取我的工单

- **URL**: `/api/tasks/my-tasks`
- **方法**: `GET`
- **描述**: 获取分配给当前用户的工单列表
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100
  - `status`: 工单状态筛选
- **成功响应** (200): 返回工单列表，格式同上

### 创建新工单

- **URL**: `/api/tasks/`
- **方法**: `POST`
- **描述**: 创建新的工单
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "title": "网络设备检修",
    "description": "检查并维修网络设备",
    "project_id": 1,
    "assigned_to_id": 2,
    "priority": 1,
    "estimated_hours": 4.0,
    "materials": "[]",
    "work_items": "[]"
  }
  ```
- **字段说明**:
  - `title`: 工单标题，必填
  - `description`: 工单描述，可选
  - `project_id`: 所属项目ID，必填
  - `assigned_to_id`: 分配给的用户ID，可选
  - `priority`: 优先级，可选，默认1
  - `estimated_hours`: 预估工时，可选
  - `materials`: 材料信息JSON字符串，可选
  - `work_items`: 工作内容信息JSON字符串，可选
- **成功响应** (200): 返回创建的工单信息

### 获取工单详情

- **URL**: `/api/tasks/{task_id}`
- **方法**: `GET`
- **描述**: 获取指定工单的详细信息，包括材料和工作内容
- **认证**: 需要Bearer Token
- **路径参数**:
  - `task_id`: 工单ID
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "title": "网络设备检修",
    "description": "检查并维修网络设备",
    "project_id": 1,
    "assigned_to_id": 2,
    "status": "in_progress",
    "priority": 1,
    "estimated_hours": 4.0,
    "actual_hours": null,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T14:00:00",
    "completed_at": null,
    "created_by_id": 1,
    "materials": [
      {
        "id": 1,
        "task_id": 1,
        "material_id": 1,
        "quantity": 10.0,
        "unit_price": 5.0,
        "total_price": 50.0,
        "supply_type": "甲供"
      }
    ],
    "work_items": [
      {
        "id": 1,
        "task_id": 1,
        "work_item_id": 1,
        "quantity": 2.0,
        "unit_price": 100.0,
        "total_price": 200.0
      }
    ]
  }
  ```
- **错误响应** (404):
  ```json
  {
    "detail": "工单不存在"
  }
  ```

### 更新工单信息

- **URL**: `/api/tasks/{task_id}`
- **方法**: `PUT`
- **描述**: 更新指定工单的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `task_id`: 工单ID
- **请求体**: 包含要更新的字段，所有字段都是可选的
- **成功响应** (200): 返回更新后的工单信息
- **错误响应** (404):
  ```json
  {
    "detail": "工单不存在"
  }
  ```

### 分配工单

- **URL**: `/api/tasks/{task_id}/assign`
- **方法**: `POST`
- **描述**: 将工单分配给指定用户
- **认证**: 需要Bearer Token
- **路径参数**:
  - `task_id`: 工单ID
- **请求体**:
  ```json
  {
    "assigned_to_id": 2
  }
  ```
- **成功响应** (200): 返回更新后的工单信息
- **错误响应** (404):
  ```json
  {
    "detail": "工单不存在"
  }
  ```

### 完成工单

- **URL**: `/api/tasks/{task_id}/complete`
- **方法**: `POST`
- **描述**: 完成工单，记录实际使用的材料和工作内容
- **认证**: 需要Bearer Token
- **路径参数**:
  - `task_id`: 工单ID
- **请求体**:
  ```json
  {
    "materials": [
      {
        "material_id": 1,
        "quantity": 10.0,
        "unit_price": 5.0,
        "supply_type": "甲供"
      }
    ],
    "work_items": [
      {
        "work_item_id": 1,
        "quantity": 2.0,
        "unit_price": 100.0
      }
    ]
  }
  ```
- **成功响应** (200): 返回更新后的工单信息
- **错误响应** (404):
  ```json
  {
    "detail": "工单不存在"
  }
  ```

### 删除工单

- **URL**: `/api/tasks/{task_id}`
- **方法**: `DELETE`
- **描述**: 删除指定工单及其关联的材料和工作内容记录
- **认证**: 需要Bearer Token
- **路径参数**:
  - `task_id`: 工单ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "工单不存在"
  }
  ```

### 批量导入工单

- **URL**: `/api/tasks/import`
- **方法**: `POST`
- **描述**: 通过CSV文件批量导入工单
- **认证**: 需要Bearer Token
- **请求体**: multipart/form-data
  - `file`: CSV文件
- **CSV格式要求**:
  - 必需字段：title, project_id
  - 可选字段：description, assigned_to_id, priority, estimated_hours
- **成功响应** (201):
  ```json
  {
    "message": "成功导入 5 条工单记录"
  }
  ```
- **错误响应** (400):
  ```json
  {
    "detail": "只支持CSV文件格式"
  }
  ```

## 材料管理API

### 获取材料分类列表

- **URL**: `/api/materials/categories`
- **方法**: `GET`
- **描述**: 获取所有可用的材料分类
- **认证**: 需要Bearer Token
- **成功响应** (200):
  ```json
  [
    "电缆类",
    "管道类",
    "设备类",
    "工具类",
    "其他"
  ]
  ```

### 获取材料供应类型列表

- **URL**: `/api/materials/supply-types`
- **方法**: `GET`
- **描述**: 获取所有可用的供应类型
- **认证**: 需要Bearer Token
- **成功响应** (200):
  ```json
  [
    "甲供",
    "自购",
    "两者皆可"
  ]
  ```

### 获取材料列表

- **URL**: `/api/materials/`
- **方法**: `GET`
- **描述**: 获取材料列表，支持多种筛选条件
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100
  - `category`: 材料分类筛选
  - `code`: 材料编号筛选（模糊匹配）
  - `name`: 材料名称筛选（模糊匹配）
  - `supply_type`: 供应类型筛选
  - `is_active`: 是否启用筛选，true/false
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "category": "电缆类",
      "code": "CAB001",
      "name": "网络电缆",
      "description": "超五类网络电缆",
      "unit": "米",
      "unit_price": 5.0,
      "supply_type": "甲供",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": null
    }
  ]
  ```

### 获取材料详情

- **URL**: `/api/materials/{material_id}`
- **方法**: `GET`
- **描述**: 获取指定材料的详细信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `material_id`: 材料ID
- **成功响应** (200): 返回材料详细信息
- **错误响应** (404):
  ```json
  {
    "detail": "材料不存在"
  }
  ```

### 创建新材料

- **URL**: `/api/materials/`
- **方法**: `POST`
- **描述**: 创建新的材料记录
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "category": "电缆类",
    "code": "CAB001",
    "name": "网络电缆",
    "description": "超五类网络电缆",
    "unit": "米",
    "unit_price": 5.0,
    "supply_type": "甲供"
  }
  ```
- **字段说明**:
  - `category`: 材料分类，可选，默认"其他"
  - `code`: 材料编号，必填，唯一，最大20字符
  - `name`: 材料名称，必填
  - `description`: 材料描述，可选
  - `unit`: 计量单位，必填
  - `unit_price`: 单价，必填，必须大于0
  - `supply_type`: 供应类型，可选，默认"两者皆可"
- **成功响应** (200): 返回创建的材料信息
- **错误响应** (400):
  ```json
  {
    "detail": "材料编号已存在"
  }
  ```

### 更新材料信息

- **URL**: `/api/materials/{material_id}`
- **方法**: `PUT`
- **描述**: 更新指定材料的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `material_id`: 材料ID
- **请求体**: 包含要更新的字段，所有字段都是可选的
- **成功响应** (200): 返回更新后的材料信息
- **错误响应** (404):
  ```json
  {
    "detail": "材料不存在"
  }
  ```

### 删除材料

- **URL**: `/api/materials/{material_id}`
- **方法**: `DELETE`
- **描述**: 删除指定材料，如果有关联的任务使用记录则设为非活动状态
- **认证**: 需要Bearer Token
- **路径参数**:
  - `material_id`: 材料ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "材料不存在"
  }
  ```

### 批量导入材料

- **URL**: `/api/materials/import`
- **方法**: `POST`
- **描述**: 通过CSV文件批量导入材料
- **认证**: 需要Bearer Token
- **请求体**: multipart/form-data
  - `file`: CSV文件
- **CSV格式要求**:
  - 必需字段：category, code, name, unit, unit_price
  - 可选字段：description, supply_type
- **成功响应** (201):
  ```json
  {
    "message": "成功导入 10 条材料记录"
  }
  ```
- **错误响应** (400):
  ```json
  {
    "detail": "只支持CSV文件格式"
  }
  ```

## 工作内容管理API

### 获取工作内容分类列表

- **URL**: `/api/work-items/categories`
- **方法**: `GET`
- **描述**: 获取所有可用的工作内容分类
- **认证**: 需要Bearer Token
- **成功响应** (200):
  ```json
  [
    "线路工程",
    "设备安装",
    "设备维修",
    "网络配置",
    "其他"
  ]
  ```

### 获取工作内容列表

- **URL**: `/api/work-items/`
- **方法**: `GET`
- **描述**: 获取工作内容列表，支持多种筛选条件
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100
  - `category`: 项目分类筛选
  - `project_number`: 项目编号筛选（模糊匹配）
  - `name`: 工作项名称筛选（模糊匹配）
  - `is_active`: 是否启用筛选，true/false
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "category": "线路工程",
      "project_number": "LINE001",
      "name": "网络线路铺设",
      "description": "办公区域网络线路铺设",
      "unit": "米",
      "skilled_labor_days": 0.5,
      "unskilled_labor_days": 0.2,
      "unit_price": 50.0,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": null
    }
  ]
  ```

### 获取工作内容详情

- **URL**: `/api/work-items/{work_item_id}`
- **方法**: `GET`
- **描述**: 获取指定工作内容的详细信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `work_item_id`: 工作内容ID
- **成功响应** (200): 返回工作内容详细信息
- **错误响应** (404):
  ```json
  {
    "detail": "工作内容不存在"
  }
  ```

### 创建新工作内容

- **URL**: `/api/work-items/`
- **方法**: `POST`
- **描述**: 创建新的工作内容记录
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "category": "线路工程",
    "project_number": "LINE001",
    "name": "网络线路铺设",
    "description": "办公区域网络线路铺设",
    "unit": "米",
    "skilled_labor_days": 0.5,
    "unskilled_labor_days": 0.2,
    "unit_price": 50.0
  }
  ```
- **字段说明**:
  - `category`: 项目分类，可选，默认"其他"
  - `project_number`: 项目编号，必填，唯一，最大20字符
  - `name`: 工作项名称，必填，最大50字符
  - `description`: 工作项描述，可选
  - `unit`: 计量单位，必填，最大20字符
  - `skilled_labor_days`: 技工工日，可选，默认0.0，必须≥0
  - `unskilled_labor_days`: 普工工日，可选，默认0.0，必须≥0
  - `unit_price`: 单价，必填，必须≥0
- **成功响应** (200): 返回创建的工作内容信息
- **错误响应** (400):
  ```json
  {
    "detail": "项目编号已存在"
  }
  ```

### 更新工作内容

- **URL**: `/api/work-items/{work_item_id}`
- **方法**: `PUT`
- **描述**: 更新指定工作内容的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `work_item_id`: 工作内容ID
- **请求体**: 包含要更新的字段，所有字段都是可选的
- **成功响应** (200): 返回更新后的工作内容信息
- **错误响应** (404):
  ```json
  {
    "detail": "工作内容不存在"
  }
  ```

### 删除工作内容

- **URL**: `/api/work-items/{work_item_id}`
- **方法**: `DELETE`
- **描述**: 删除指定工作内容，如果有关联的任务使用记录则设为非活动状态
- **认证**: 需要Bearer Token
- **路径参数**:
  - `work_item_id`: 工作内容ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "工作内容不存在"
  }
  ```

### 批量导入工作内容

- **URL**: `/api/work-items/import`
- **方法**: `POST`
- **描述**: 通过CSV文件批量导入工作内容
- **认证**: 需要Bearer Token
- **请求体**: multipart/form-data
  - `file`: CSV文件
- **CSV格式要求**:
  - 必需字段：category, project_number, name, unit, unit_price
  - 可选字段：description, skilled_labor_days, unskilled_labor_days
- **成功响应** (201):
  ```json
  {
    "message": "成功导入 8 条工作内容记录"
  }
  ```
- **错误响应** (400):
  ```json
  {
    "detail": "只支持CSV文件格式"
  }
  ```

## 施工队伍管理API

### 获取队伍列表

- **URL**: `/api/teams/`
- **方法**: `GET`
- **描述**: 获取施工队伍列表，支持状态筛选
- **认证**: 需要Bearer Token
- **查询参数**:
  - `skip`: 跳过的记录数，默认0
  - `limit`: 返回的记录数，默认100
  - `is_active`: 是否启用筛选，true/false
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "name": "网络维修队",
      "description": "专业网络设备维修队伍",
      "created_at": "2024-01-01T10:00:00",
      "is_active": true
    }
  ]
  ```

### 创建新队伍

- **URL**: `/api/teams/`
- **方法**: `POST`
- **描述**: 创建新的施工队伍
- **认证**: 需要Bearer Token
- **请求体**:
  ```json
  {
    "name": "网络维修队",
    "description": "专业网络设备维修队伍"
  }
  ```
- **字段说明**:
  - `name`: 队伍名称，必填
  - `description`: 队伍描述，可选
- **成功响应** (200): 返回创建的队伍信息

### 获取队伍详情

- **URL**: `/api/teams/{team_id}`
- **方法**: `GET`
- **描述**: 获取指定队伍的详细信息，包括成员列表
- **认证**: 需要Bearer Token
- **路径参数**:
  - `team_id`: 队伍ID
- **成功响应** (200):
  ```json
  {
    "id": 1,
    "name": "网络维修队",
    "description": "专业网络设备维修队伍",
    "created_at": "2024-01-01T10:00:00",
    "is_active": true,
    "members": [
      {
        "id": 1,
        "team_id": 1,
        "user_id": 2,
        "is_leader": true,
        "joined_at": "2024-01-01T10:00:00",
        "user": {
          "id": 2,
          "username": "worker1",
          "email": "worker1@example.com",
          "full_name": "工人一",
          "phone": "13800000001",
          "role": "worker",
          "is_active": true
        }
      }
    ]
  }
  ```
- **错误响应** (404):
  ```json
  {
    "detail": "团队不存在"
  }
  ```

### 更新队伍信息

- **URL**: `/api/teams/{team_id}`
- **方法**: `PUT`
- **描述**: 更新指定队伍的信息
- **认证**: 需要Bearer Token
- **路径参数**:
  - `team_id`: 队伍ID
- **请求体**: 包含要更新的字段，所有字段都是可选的
- **成功响应** (200): 返回更新后的队伍信息
- **错误响应** (404):
  ```json
  {
    "detail": "团队不存在"
  }
  ```

### 添加队伍成员

- **URL**: `/api/teams/{team_id}/members`
- **方法**: `POST`
- **描述**: 向指定队伍添加成员
- **认证**: 需要Bearer Token
- **路径参数**:
  - `team_id`: 队伍ID
- **请求体**:
  ```json
  {
    "user_id": 2,
    "is_leader": false
  }
  ```
- **字段说明**:
  - `user_id`: 用户ID，必填
  - `is_leader`: 是否为队长，可选，默认false
- **成功响应** (200): 返回更新后的队伍信息
- **错误响应** (404):
  ```json
  {
    "detail": "团队不存在"
  }
  ```

### 移除队伍成员

- **URL**: `/api/teams/{team_id}/members/{member_id}`
- **方法**: `DELETE`
- **描述**: 从指定队伍移除成员
- **认证**: 需要Bearer Token
- **路径参数**:
  - `team_id`: 队伍ID
  - `member_id`: 成员ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "团队成员不存在"
  }
  ```

### 删除队伍

- **URL**: `/api/teams/{team_id}`
- **方法**: `DELETE`
- **描述**: 删除指定队伍
- **认证**: 需要Bearer Token
- **路径参数**:
  - `team_id`: 队伍ID
- **成功响应** (204): 无内容
- **错误响应** (404):
  ```json
  {
    "detail": "团队不存在"
  }
  ```

## 用户管理API

### 获取用户列表

- **URL**: `/api/users/`
- **方法**: `GET`
- **描述**: 获取用户列表，仅管理员可访问
- **认证**: 需要Bearer Token（管理员权限）
- **查询参数**:
  - `role`: 角色筛选，可选值：admin、manager、worker
  - `is_active`: 是否启用筛选，true/false
- **成功响应** (200):
  ```json
  [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "管理员",
      "phone": "13800000000",
      "role": "admin",
      "is_active": true
    }
  ]
  ```
- **错误响应** (403):
  ```json
  {
    "detail": "没有足够的权限执行此操作"
  }
  ```

### 获取用户详情

- **URL**: `/api/users/{user_id}`
- **方法**: `GET`
- **描述**: 获取指定用户的详细信息，仅管理员可访问
- **认证**: 需要Bearer Token（管理员权限）
- **路径参数**:
  - `user_id`: 用户ID
- **成功响应** (200): 返回用户详细信息
- **错误响应** (404):
  ```json
  {
    "detail": "用户不存在"
  }
  ```

### 更新用户信息

- **URL**: `/api/users/{user_id}`
- **方法**: `PUT`
- **描述**: 更新指定用户的信息，仅管理员可访问
- **认证**: 需要Bearer Token（管理员权限）
- **路径参数**:
  - `user_id`: 用户ID
- **请求体**:
  ```json
  {
    "email": "newemail@example.com",
    "full_name": "新姓名",
    "phone": "13800000001",
    "role": "manager",
    "is_active": true
  }
  ```
- **字段说明**: 所有字段都是可选的
  - `email`: 邮箱，格式验证
  - `full_name`: 全名
  - `phone`: 电话号码
  - `role`: 角色，可选值：admin、manager、worker
  - `is_active`: 是否启用
- **成功响应** (200): 返回更新后的用户信息
- **错误响应** (404):
  ```json
  {
    "detail": "用户不存在"
  }
  ```

### 删除用户

- **URL**: `/api/users/{user_id}`
- **方法**: `DELETE`
- **描述**: 删除指定用户，仅管理员可访问，不能删除自己
- **认证**: 需要Bearer Token（管理员权限）
- **路径参数**:
  - `user_id`: 用户ID
- **成功响应** (204): 无内容
- **错误响应** (400):
  ```json
  {
    "detail": "不能删除自己的账户"
  }
  ```

### 批量导入用户

- **URL**: `/api/users/import`
- **方法**: `POST`
- **描述**: 通过CSV文件批量导入用户，仅管理员可访问
- **认证**: 需要Bearer Token（管理员权限）
- **请求体**: multipart/form-data
  - `file`: CSV文件
- **CSV格式要求**:
  - 必需字段：username, password, email, role
  - 可选字段：full_name, phone
- **成功响应** (201):
  ```json
  {
    "message": "成功导入 3 条用户记录"
  }
  ```
- **错误响应** (400):
  ```json
  {
    "detail": "只支持CSV文件格式"
  }
  ```

## 统计分析API

### 项目统计

- **URL**: `/api/statistics/projects`
- **方法**: `GET`
- **描述**: 获取项目相关的统计信息
- **认证**: 需要Bearer Token
- **查询参数**:
  - `start_date`: 开始日期，格式：YYYY-MM-DD，可选，默认为30天前
  - `end_date`: 结束日期，格式：YYYY-MM-DD，可选，默认为当前日期
- **成功响应** (200):
  ```json
  {
    "total_projects": 25,
    "completed_projects": 18,
    "completion_rate": 72.0,
    "pending_projects": 3,
    "in_progress_projects": 4,
    "cancelled_projects": 0,
    "projects_by_status": [
      {"status": "completed", "count": 18},
      {"status": "in_progress", "count": 4},
      {"status": "pending", "count": 3}
    ]
  }
  ```

### 工单统计

- **URL**: `/api/statistics/tasks`
- **方法**: `GET`
- **描述**: 获取工单相关的统计信息
- **认证**: 需要Bearer Token
- **查询参数**:
  - `start_date`: 开始日期，格式：YYYY-MM-DD，可选，默认为30天前
  - `end_date`: 结束日期，格式：YYYY-MM-DD，可选，默认为当前日期
- **成功响应** (200):
  ```json
  {
    "total_tasks": 120,
    "completed_tasks": 95,
    "completion_rate": 79.17,
    "pending_tasks": 8,
    "assigned_tasks": 12,
    "in_progress_tasks": 5,
    "cancelled_tasks": 0,
    "tasks_by_status": [
      {"status": "completed", "count": 95},
      {"status": "assigned", "count": 12},
      {"status": "pending", "count": 8},
      {"status": "in_progress", "count": 5}
    ]
  }
  ```

### 材料使用统计

- **URL**: `/api/statistics/materials`
- **方法**: `GET`
- **描述**: 获取材料使用相关的统计信息
- **认证**: 需要Bearer Token
- **查询参数**:
  - `start_date`: 开始日期，格式：YYYY-MM-DD，可选，默认为30天前
  - `end_date`: 结束日期，格式：YYYY-MM-DD，可选，默认为当前日期
- **成功响应** (200):
  ```json
  {
    "total_material_cost": 15680.50,
    "company_provided_cost": 12340.00,
    "self_purchased_cost": 3340.50,
    "most_used_materials": [
      {
        "id": 1,
        "name": "网络电缆",
        "total_quantity": 500.0,
        "total_cost": 2500.0
      },
      {
        "id": 2,
        "name": "网络接头",
        "total_quantity": 200.0,
        "total_cost": 1000.0
      }
    ]
  }
  ```

### 工作内容统计

- **URL**: `/api/statistics/work-items`
- **方法**: `GET`
- **描述**: 获取工作内容相关的统计信息
- **认证**: 需要Bearer Token
- **查询参数**:
  - `start_date`: 开始日期，格式：YYYY-MM-DD，可选，默认为30天前
  - `end_date`: 结束日期，格式：YYYY-MM-DD，可选，默认为当前日期
- **成功响应** (200):
  ```json
  {
    "total_work_item_cost": 25600.00,
    "most_performed_work_items": [
      {
        "id": 1,
        "name": "网络线路铺设",
        "total_quantity": 1000.0,
        "total_cost": 50000.0
      },
      {
        "id": 2,
        "name": "设备安装",
        "total_quantity": 50.0,
        "total_cost": 15000.0
      }
    ]
  }
  ```

### 队伍绩效统计

- **URL**: `/api/statistics/teams`
- **方法**: `GET`
- **描述**: 获取队伍绩效相关的统计信息
- **认证**: 需要Bearer Token
- **查询参数**:
  - `start_date`: 开始日期，格式：YYYY-MM-DD，可选，默认为30天前
  - `end_date`: 结束日期，格式：YYYY-MM-DD，可选，默认为当前日期
- **成功响应** (200):
  ```json
  {
    "team_performance": [
      {
        "team_id": 1,
        "team_name": "网络维修队",
        "completed_tasks": 45,
        "total_tasks": 50,
        "completion_rate": 90.0
      }
    ]
  }
  ```

## 健康检查API

### 基础健康检查

- **URL**: `/api/health-check/`
- **方法**: `GET`
- **描述**: 检查API服务器是否正常运行，无需认证
- **认证**: 无需认证
- **成功响应** (200):
  ```json
  {
    "status": "ok",
    "message": "API服务器运行正常"
  }
  ```

### 认证健康检查

- **URL**: `/api/health-check/auth`
- **方法**: `GET`
- **描述**: 检查认证系统是否正常工作
- **认证**: 需要Bearer Token
- **成功响应** (200):
  ```json
  {
    "status": "ok",
    "message": "认证正常",
    "user_id": 1,
    "username": "admin"
  }
  ```
- **错误响应** (401):
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

## 文件上传API

### 上传单个文件

- **URL**: `/api/upload/`
- **方法**: `POST`
- **描述**: 上传单个文件到服务器
- **认证**: 需要Bearer Token
- **请求体**: multipart/form-data
  - `file`: 要上传的文件
- **成功响应** (201):
  ```json
  {
    "filename": "example.jpg",
    "url": "/uploads/20240101/uuid-filename.jpg",
    "size": 12345,
    "content_type": "image/jpeg"
  }
  ```
- **错误响应** (500):
  ```json
  {
    "detail": "文件上传失败: 磁盘空间不足"
  }
  ```

### 上传多个文件

- **URL**: `/api/upload/multiple`
- **方法**: `POST`
- **描述**: 批量上传多个文件到服务器
- **认证**: 需要Bearer Token
- **请求体**: multipart/form-data
  - `files`: 要上传的文件列表
- **成功响应** (201):
  ```json
  [
    {
      "filename": "file1.jpg",
      "url": "/uploads/20240101/uuid1-file1.jpg",
      "size": 12345,
      "content_type": "image/jpeg"
    },
    {
      "filename": "file2.pdf",
      "url": "/uploads/20240101/uuid2-file2.pdf",
      "size": 54321,
      "content_type": "application/pdf"
    }
  ]
  ```
- **部分失败响应** (201):
  ```json
  [
    {
      "filename": "file1.jpg",
      "url": "/uploads/20240101/uuid1-file1.jpg",
      "size": 12345,
      "content_type": "image/jpeg"
    },
    {
      "filename": "file2.pdf",
      "error": "文件大小超过限制"
    }
  ]
  ```

## 错误处理

### 通用错误格式

所有API错误都遵循统一的响应格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

- **400 Bad Request**: 请求参数错误或格式不正确
- **401 Unauthorized**: 未提供认证信息或认证失败
- **403 Forbidden**: 权限不足，无法访问资源
- **404 Not Found**: 请求的资源不存在
- **422 Unprocessable Entity**: 请求数据验证失败
- **500 Internal Server Error**: 服务器内部错误

### 认证错误

当认证失败时，API会返回401状态码：

```json
{
  "detail": "Could not validate credentials"
}
```

### 权限错误

当用户权限不足时，API会返回403状态码：

```json
{
  "detail": "没有足够的权限执行此操作"
}
```

### 数据验证错误

当请求数据验证失败时，API会返回422状态码：

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 使用示例

### JavaScript/Axios示例

```javascript
// 登录获取token
const loginResponse = await axios.post('/api/auth/token', {
  username: 'admin',
  password: 'admin123'
}, {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
});

const token = loginResponse.data.access_token;

// 使用token访问API
const projectsResponse = await axios.get('/api/projects/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 创建新项目
const newProject = await axios.post('/api/projects/', {
  title: '新项目',
  location: '北京',
  contact_name: '张三',
  contact_phone: '13800000000'
}, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Python/Requests示例

```python
import requests

# 登录获取token
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
login_response = requests.post(
    'http://localhost:8000/api/auth/token',
    data=login_data
)
token = login_response.json()['access_token']

# 设置认证头
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 获取项目列表
projects_response = requests.get(
    'http://localhost:8000/api/projects/',
    headers=headers
)
projects = projects_response.json()

# 创建新项目
new_project_data = {
    'title': '新项目',
    'location': '北京',
    'contact_name': '张三',
    'contact_phone': '13800000000'
}
create_response = requests.post(
    'http://localhost:8000/api/projects/',
    json=new_project_data,
    headers=headers
)
```

## 版本信息

- **API版本**: v1.0
- **文档版本**: 2024-01-01
- **最后更新**: 2024-01-01

## 联系信息

如有API相关问题，请联系开发团队。
