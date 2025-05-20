#!/bin/bash

# 维修项目管理系统Docker启动脚本

# 创建必要的目录
mkdir -p data logs uploads

# 启动Docker容器
docker-compose up -d

echo "维修项目管理系统已启动"
echo "前端访问地址: http://localhost:8458"
echo "后端API地址: http://localhost:8458/api"

# 等待后端启动
echo "等待后端服务启动..."
sleep 5

# 创建管理员用户
echo "是否创建管理员用户? (y/n)"
read create_admin

if [ "$create_admin" = "y" ]; then
    docker exec -it repair-management-backend python -c "
import sqlite3
from passlib.context import CryptContext

# 连接数据库
conn = sqlite3.connect('repair_management.db')
cursor = conn.cursor()

# 检查用户是否已存在
cursor.execute(\"SELECT * FROM users WHERE username = 'admin'\")
if cursor.fetchone():
    print('管理员用户已存在')
    conn.close()
    exit()

# 创建密码哈希
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hashed_password = pwd_context.hash('admin123')

# 插入管理员用户
cursor.execute(
    \"INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)\",
    ('admin', 'admin@example.com', hashed_password, '管理员', 'admin', 1)
)
conn.commit()
conn.close()
print('管理员用户已创建，用户名: admin，密码: admin123')
"
fi

echo "系统已成功启动，可以通过浏览器访问: http://localhost:8458"
