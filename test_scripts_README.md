# 工作内容测试脚本

这个目录包含用于测试工作内容API的脚本。

## 文件说明

- `test_add_work_item.py`: 添加单个工作内容的简单测试脚本
- `batch_add_work_items.py`: 批量添加工作内容的高级测试脚本
- `work_items.csv`: 包含多个工作内容示例的CSV文件

## 使用方法

### 添加单个工作内容

```bash
python test_add_work_item.py --username your_username --password your_password
```

这将添加一个预定义的工作内容：
- 分类：通信线路
- 编号：TXL2-001
- 名称：挖、松填光（电）缆沟及接头坑 普通土
- 计量单位：百立方米
- 技工工日：0
- 普工工日：39.38
- 单价：5

### 批量添加工作内容

从CSV文件批量添加工作内容：

```bash
python batch_add_work_items.py --username your_username --password your_password --csv work_items.csv --output results.csv
```

添加单个预定义的工作内容：

```bash
python batch_add_work_items.py --username your_username --password your_password --single
```

### 参数说明

这些脚本支持以下参数：

- `--username`: 用户名
- `--password`: 密码
- `--csv`: CSV文件路径，包含要添加的工作内容
- `--output`: 输出结果的CSV文件路径
- `--single`: 添加单个预定义的工作内容
- `--api-url`: API基础URL，例如 http://localhost:8000/api

### 使用环境变量

您也可以通过环境变量设置用户名和密码：

```bash
export API_USERNAME=your_username
export API_PASSWORD=your_password
python test_add_work_item.py
```

## CSV文件格式

CSV文件应包含以下列：

- `category`: 工作内容分类（如：通信线路、通信电源等）
- `project_number`: 项目编号（唯一）
- `name`: 工作内容名称
- `description`: 工作内容描述（可选）
- `unit`: 计量单位
- `skilled_labor_days`: 技工工日
- `unskilled_labor_days`: 普工工日
- `unit_price`: 单价

## 注意事项

1. 确保后端服务已启动并可访问
2. 默认API地址为 `http://localhost:8000/api`，可以通过 `--api-url` 参数修改
3. 项目编号必须唯一，如果添加失败，请检查是否已存在相同编号的工作内容
4. 所有数值字段（技工工日、普工工日、单价）必须为数字
5. 如果登录失败，请检查用户名和密码是否正确
6. 使用交互式菜单 `./run_test.sh` 可以方便地设置用户名、密码和API URL
7. 这些脚本使用Python内置的urllib库，不需要安装额外的依赖
