# 数据库文档

本文档描述了维修项目管理系统的数据库结构和表关系。

## 数据库概述

系统使用SQLite数据库，数据库文件位于项目根目录下的`repair_management.db`。

## 实体关系图

```
+-------------+       +-------------+       +-------------+
|   Project   |------>|    Task     |------>|  TaskWorker |
+-------------+       +-------------+       +-------------+
      |                     |                      |
      |                     |                      |
      v                     v                      v
+-------------+       +-------------+       +-------------+
| ProjectTeam |       | TaskMaterial|       |    User     |
+-------------+       +-------------+       +-------------+
      |                     |                      |
      |                     |                      |
      v                     v                      v
+-------------+       +-------------+       +-------------+
|    Team     |       |   Material  |       |  TeamMember |
+-------------+       +-------------+       +-------------+
                            |
                            |
                            v
                      +-------------+
                      | TaskWorkItem|
                      +-------------+
                            |
                            |
                            v
                      +-------------+
                      |  WorkItem   |
                      +-------------+
```

## 数据库关系

系统中的主要实体之间存在以下关系：

1. **维修项目 ↔ 工单**：一对多关系
   - 一个维修项目可以包含多个工单
   - 每个工单必须属于一个维修项目
   - 关系字段：`Task.project_id` 引用 `Project.id`

2. **施工人员 ↔ 施工队伍**：多对一关系
   - 一个施工队伍可以包含多个施工人员
   - 每个施工人员只能属于一个施工队伍
   - 关系表：`TeamMember` 表，包含 `team_id` 和 `user_id` 字段

3. **维修项目 ↔ 施工队伍**：多对多关系
   - 一个维修项目可以由多个施工队伍负责
   - 一个施工队伍可以负责多个维修项目
   - 关系表：`ProjectTeam` 表，包含 `project_id` 和 `team_id` 字段

4. **工单 ↔ 施工人员**：多对多关系
   - 一个工单可以由多个施工人员共同完成
   - 一个施工人员可以同时处理多个工单
   - 关系表：`TaskWorker` 表，包含 `task_id` 和 `user_id` 字段

5. **工单 ↔ 材料**：多对多关系
   - 一个工单可以使用多种材料
   - 一种材料可以用于多个工单
   - 关系表：`TaskMaterial` 表，包含 `task_id` 和 `material_id` 字段，以及数量和价格信息

6. **工单 ↔ 工作内容**：多对多关系
   - 一个工单可以包含多个工作内容
   - 一个工作内容可以用于多个工单
   - 关系表：`TaskWorkItem` 表，包含 `task_id` 和 `work_item_id` 字段，以及数量和价格信息

## 表结构

### User（用户表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 用户ID | 主键，自增 |
| username | VARCHAR | 用户名 | 非空，唯一 |
| hashed_password | VARCHAR | 哈希密码 | 非空 |
| email | VARCHAR | 邮箱 | 非空，唯一 |
| full_name | VARCHAR | 姓名 | 可空 |
| phone | VARCHAR | 电话 | 可空 |
| role | VARCHAR | 角色 | 非空，默认"worker" |
| is_active | BOOLEAN | 是否启用 | 非空，默认True |
| created_at | DATETIME | 创建时间 | 非空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### Project（项目表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 项目ID | 主键，自增 |
| title | VARCHAR | 项目标题 | 非空 |
| description | TEXT | 项目描述 | 可空 |
| status | VARCHAR | 项目状态 | 非空，默认"pending" |
| start_date | DATE | 开始日期 | 可空 |
| end_date | DATE | 结束日期 | 可空 |
| budget | FLOAT | 预算 | 可空 |
| created_by_id | INTEGER | 创建人ID | 外键，引用User.id |
| created_at | DATETIME | 创建时间 | 非空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### Task（工单表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 工单ID | 主键，自增 |
| project_id | INTEGER | 项目ID | 外键，引用Project.id |
| title | VARCHAR | 工单标题 | 非空 |
| description | TEXT | 工单描述 | 可空 |
| status | VARCHAR | 工单状态 | 非空，默认"pending" |
| attachment | VARCHAR | 派单附件 | 可空 |
| work_list | TEXT | 工作量清单 | 可空 |
| company_material_list | TEXT | 甲供材清单 | 可空 |
| self_material_list | TEXT | 自购料清单 | 可空 |
| labor_cost | FLOAT | 施工费 | 可空，默认0 |
| material_cost | FLOAT | 材料费 | 可空，默认0 |
| total_cost | FLOAT | 总费用 | 可空，默认0 |
| created_by_id | INTEGER | 创建人ID | 外键，引用User.id |
| assigned_to_id | INTEGER | 负责人ID | 外键，引用User.id |
| team_id | INTEGER | 施工队ID | 外键，引用Team.id |
| created_at | DATETIME | 创建时间 | 非空 |
| assigned_at | DATETIME | 分配时间 | 可空 |
| completed_at | DATETIME | 完成时间 | 可空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### Material（材料表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 材料ID | 主键，自增 |
| category | VARCHAR | 材料分类 | 非空 |
| code | VARCHAR | 材料编号 | 非空，唯一 |
| name | VARCHAR | 材料名称 | 非空 |
| description | TEXT | 材料描述 | 可空 |
| unit | VARCHAR | 单位 | 非空 |
| unit_price | FLOAT | 单价 | 非空，默认0 |
| supply_type | VARCHAR | 供应类型 | 非空，默认"甲供" |
| is_active | BOOLEAN | 是否启用 | 非空，默认True |
| created_at | DATETIME | 创建时间 | 非空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### WorkItem（工作内容表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 工作内容ID | 主键，自增 |
| category | VARCHAR | 项目分类 | 非空 |
| project_number | VARCHAR | 项目编号 | 非空，唯一 |
| name | VARCHAR | 工作内容名称 | 非空 |
| description | TEXT | 工作内容描述 | 可空 |
| unit | VARCHAR | 单位 | 非空 |
| skilled_labor_days | FLOAT | 技工工日 | 可空，默认0 |
| unskilled_labor_days | FLOAT | 普工工日 | 可空，默认0 |
| unit_price | FLOAT | 单价 | 非空，默认0 |
| is_active | BOOLEAN | 是否启用 | 非空，默认True |
| created_at | DATETIME | 创建时间 | 非空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### Team（施工队伍表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 队伍ID | 主键，自增 |
| name | VARCHAR | 队伍名称 | 非空 |
| description | TEXT | 队伍描述 | 可空 |
| leader_id | INTEGER | 队长ID | 外键，引用User.id |
| is_active | BOOLEAN | 是否启用 | 非空，默认True |
| created_at | DATETIME | 创建时间 | 非空 |
| updated_at | DATETIME | 更新时间 | 可空 |

### TeamMember（队伍成员表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 记录ID | 主键，自增 |
| team_id | INTEGER | 队伍ID | 外键，引用Team.id |
| user_id | INTEGER | 用户ID | 外键，引用User.id |
| joined_at | DATETIME | 加入时间 | 非空 |

### ProjectTeam（项目队伍关联表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 记录ID | 主键，自增 |
| project_id | INTEGER | 项目ID | 外键，引用Project.id |
| team_id | INTEGER | 队伍ID | 外键，引用Team.id |
| assigned_at | DATETIME | 分配时间 | 非空 |

### TaskWorker（工单工人关联表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 记录ID | 主键，自增 |
| task_id | INTEGER | 工单ID | 外键，引用Task.id |
| user_id | INTEGER | 用户ID | 外键，引用User.id |
| assigned_at | DATETIME | 分配时间 | 非空 |

### TaskMaterial（工单材料关联表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 记录ID | 主键，自增 |
| task_id | INTEGER | 工单ID | 外键，引用Task.id |
| material_id | INTEGER | 材料ID | 外键，引用Material.id |
| quantity | FLOAT | 数量 | 非空，默认0 |
| is_company_provided | BOOLEAN | 是否甲供 | 非空，默认True |
| unit_price | FLOAT | 单价 | 非空，默认0 |
| total_price | FLOAT | 总价 | 非空，默认0 |

### TaskWorkItem（工单工作内容关联表）

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | INTEGER | 记录ID | 主键，自增 |
| task_id | INTEGER | 工单ID | 外键，引用Task.id |
| work_item_id | INTEGER | 工作内容ID | 外键，引用WorkItem.id |
| quantity | FLOAT | 数量 | 非空，默认0 |
| unit_price | FLOAT | 单价 | 非空，默认0 |
| total_price | FLOAT | 总价 | 非空，默认0 |

## 索引

为了提高查询性能，系统在以下字段上创建了索引：

1. `User.username`：用户名索引，加速用户查询
2. `User.email`：邮箱索引，加速邮箱查询
3. `Project.created_by_id`：项目创建人索引，加速用户项目查询
4. `Task.project_id`：工单项目索引，加速项目工单查询
5. `Task.assigned_to_id`：工单负责人索引，加速用户工单查询
6. `Task.status`：工单状态索引，加速状态筛选
7. `Material.code`：材料编号索引，加速材料查询
8. `Material.category`：材料分类索引，加速分类筛选
9. `WorkItem.project_number`：工作内容项目编号索引，加速工作内容查询
10. `WorkItem.category`：工作内容分类索引，加速分类筛选

## 数据库结构检查和修复

系统提供了数据库结构检查和修复工具：

1. `check_db_structure.py`：检查数据库表结构是否完整
2. `fix_db_structure.py`：修复数据库表结构问题

这些工具可以帮助解决数据库结构不一致的问题，特别是在系统升级或迁移后。
