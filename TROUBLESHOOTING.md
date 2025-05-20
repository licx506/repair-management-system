# 故障排除

本文档提供了维修项目管理系统常见问题的解决方案。

## 常见问题及修复

### 1. 导入路径问题

**问题**：遇到 `ModuleNotFoundError: No module named 'backend'` 错误。

**原因**：后端代码中的导入路径不正确。

**解决方案**：

使用提供的修复脚本：

```bash
python fix_imports.py
```

这个脚本会自动将所有 `from backend.xxx` 的导入修改为 `from xxx`。

或者手动修改导入语句，例如将：

```python
from backend.models.user import User
```

修改为：

```python
from models.user import User
```

### 2. 类型导入问题

**问题**：遇到 `The requested module does not provide an export named 'XXX'` 错误。

**原因**：前端代码中的类型导入方式不正确。

**解决方案**：

修改类型导入方式，例如将：

```typescript
import { Task } from '../../api/tasks';
```

修改为：

```typescript
import type { Task } from '../../api/tasks';
```

### 3. 日期验证问题

**问题**：遇到 `Uncaught TypeError: date.isValid is not a function` 错误。

**原因**：使用JavaScript的Date对象而不是dayjs对象。

**解决方案**：

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

### 4. 数据库表结构问题

**问题**：遇到 `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: xxx` 错误。

**原因**：数据库表结构与代码中的模型定义不一致。

**解决方案**：

1. 检查数据库表结构：
```bash
python check_db_structure.py
```

2. 修复数据库表结构：
```bash
python fix_db_structure.py
```

3. 如果问题仍然存在，可以尝试重新创建数据库：
```bash
# 备份数据库
cp backend/repair_management.db backend/repair_management.db.bak

# 删除数据库
rm backend/repair_management.db

# 重启后端，自动创建新数据库
python run.py --backend-only
```

### 5. 前端API请求失败

**问题**：前端API请求返回401或403错误。

**原因**：认证令牌无效或过期。

**解决方案**：

1. 检查localStorage中的令牌：
```javascript
// 在浏览器控制台中执行
console.log(localStorage.getItem('token'));
```

2. 如果令牌不存在或已过期，重新登录获取新令牌。

3. 确保API请求中包含正确的Authorization头：
```typescript
// 在api.ts中检查请求拦截器
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

### 6. 前端组件渲染问题

**问题**：前端组件不显示或显示不正确。

**原因**：组件props类型错误或数据格式不匹配。

**解决方案**：

1. 检查组件props类型：
```typescript
// 确保props类型定义正确
interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onTaskClick: (taskId: number) => void;
}
```

2. 检查数据格式：
```typescript
// 确保数据格式与组件期望的格式一致
console.log('Tasks data:', tasks);
```

3. 使用条件渲染处理加载状态和空数据：
```tsx
{loading ? (
  <Spin />
) : tasks.length > 0 ? (
  <TaskList tasks={tasks} onTaskClick={handleTaskClick} />
) : (
  <Empty description="暂无数据" />
)}
```

### 7. 批量导入问题

**问题**：批量导入失败或导入的数据不正确。

**原因**：CSV文件格式不正确或数据验证失败。

**解决方案**：

1. 确保CSV文件格式正确，包含所有必需字段：
   - 工作内容：category, project_number, name, unit, unit_price
   - 材料：category, code, name, unit, unit_price
   - 工单：title
   - 用户：username, password, email, role

2. 检查CSV文件编码，推荐使用UTF-8编码。

3. 确保数据库表结构完整：
```bash
python check_db_structure.py
```

4. 如果数据库表结构有问题，使用修复工具：
```bash
python fix_db_structure.py
```

5. 检查模板文件是否可以正常下载，确保静态文件服务正常运行。

6. 导入失败时，查看后端日志以获取详细错误信息：
```bash
tail -f logs/backend.log
```

### 8. 响应式布局问题

**问题**：在移动设备上页面显示不正确。

**原因**：响应式布局配置不正确或组件未适配移动设备。

**解决方案**：

1. 确保使用了正确的布局组件：
```tsx
// 根据设备类型选择布局
const isMobile = useIsMobile();
return isMobile ? <MobileLayout>{children}</MobileLayout> : <PCLayout>{children}</PCLayout>;
```

2. 使用Ant Design的响应式组件：
```tsx
<Row gutter={[16, 16]}>
  <Col xs={24} sm={12} md={8} lg={6}>
    <Card>内容</Card>
  </Col>
</Row>
```

3. 使用媒体查询适配不同屏幕尺寸：
```css
@media (max-width: 768px) {
  .container {
    padding: 8px;
  }
}
```

### 9. 后端服务启动失败

**问题**：后端服务无法启动或启动后立即崩溃。

**原因**：端口被占用、依赖缺失或配置错误。

**解决方案**：

1. 检查端口是否被占用：
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

2. 如果端口被占用，可以更改端口：
```python
# 在backend/main.py中修改
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

3. 检查依赖是否安装完整：
```bash
pip install -r requirements.txt
```

4. 检查配置文件是否正确：
```bash
# 检查数据库配置
cat backend/database.py
```

### 10. 前端构建失败

**问题**：前端构建失败或构建后无法运行。

**原因**：依赖冲突、TypeScript错误或配置问题。

**解决方案**：

1. 清理依赖缓存并重新安装：
```bash
cd frontend
rm -rf node_modules
npm cache clean --force
npm install
```

2. 检查TypeScript错误：
```bash
cd frontend
npm run tsc
```

3. 检查Vite配置：
```bash
cat frontend/vite.config.ts
```

4. 尝试使用开发模式运行：
```bash
cd frontend
npm run dev
```

## 性能优化建议

1. **数据库查询优化**：
   - 添加适当的索引
   - 使用分页加载数据
   - 避免N+1查询问题

2. **前端性能优化**：
   - 使用React.memo减少不必要的重渲染
   - 使用虚拟列表处理大量数据
   - 实现组件懒加载

3. **网络请求优化**：
   - 实现请求缓存
   - 使用批量请求减少API调用次数
   - 压缩响应数据

4. **静态资源优化**：
   - 使用CDN加载静态资源
   - 压缩和合并CSS/JS文件
   - 使用图片懒加载
