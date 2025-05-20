#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重建数据库表结构
此脚本将重建数据库表结构，确保与当前模型匹配
"""

import os
import sys
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "backend" / "repair_management.db"

def backup_database():
    """备份数据库"""
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.bak"
        print(f"备份数据库到 {backup_path}")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        return True
    return False

def rebuild_work_items_table():
    """重建工作内容表"""
    print(f"正在重建工作内容表...")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_items'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 获取现有数据
            print("获取现有工作内容数据...")
            cursor.execute("SELECT * FROM work_items")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # 创建临时表
            print("创建临时表...")
            cursor.execute("CREATE TABLE work_items_temp (id INTEGER PRIMARY KEY, category TEXT, project_number TEXT UNIQUE, name TEXT, description TEXT, unit TEXT, skilled_labor_days FLOAT, unskilled_labor_days FLOAT, unit_price FLOAT, is_active BOOLEAN, created_at TIMESTAMP, updated_at TIMESTAMP)")
            
            # 将数据迁移到临时表
            if rows:
                print(f"迁移 {len(rows)} 条数据到临时表...")
                for row in rows:
                    # 创建一个包含所有新列的数据字典
                    data = {}
                    for i, col in enumerate(columns):
                        data[col] = row[i]
                    
                    # 添加新列的默认值
                    if 'category' not in data:
                        data['category'] = '通信线路'
                    if 'skilled_labor_days' not in data:
                        data['skilled_labor_days'] = 0.0
                    if 'unskilled_labor_days' not in data:
                        data['unskilled_labor_days'] = 0.0
                    
                    # 构建插入语句
                    cols = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data.keys()])
                    sql = f"INSERT INTO work_items_temp ({cols}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(data.values()))
            
            # 删除原表并重命名临时表
            print("删除原表并重命名临时表...")
            cursor.execute("DROP TABLE work_items")
            cursor.execute("ALTER TABLE work_items_temp RENAME TO work_items")
            
            # 创建索引
            print("创建索引...")
            cursor.execute("CREATE INDEX ix_work_items_category ON work_items (category)")
            cursor.execute("CREATE INDEX ix_work_items_project_number ON work_items (project_number)")
            cursor.execute("CREATE INDEX ix_work_items_name ON work_items (name)")
            
            print("工作内容表重建完成")
        else:
            # 创建新表
            print("创建工作内容表...")
            cursor.execute("""
            CREATE TABLE work_items (
                id INTEGER PRIMARY KEY,
                category TEXT,
                project_number TEXT UNIQUE,
                name TEXT,
                description TEXT,
                unit TEXT,
                skilled_labor_days FLOAT DEFAULT 0.0,
                unskilled_labor_days FLOAT DEFAULT 0.0,
                unit_price FLOAT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
            """)
            
            # 创建索引
            print("创建索引...")
            cursor.execute("CREATE INDEX ix_work_items_category ON work_items (category)")
            cursor.execute("CREATE INDEX ix_work_items_project_number ON work_items (project_number)")
            cursor.execute("CREATE INDEX ix_work_items_name ON work_items (name)")
            
            print("工作内容表创建完成")
        
        # 提交更改
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"重建工作内容表失败: {e}")
        return False
    finally:
        conn.close()

def main():
    print(f"数据库路径: {DB_PATH}")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        print("请先运行应用程序以创建数据库")
        return False
    
    # 备份数据库
    backup_database()
    
    # 重建工作内容表
    if not rebuild_work_items_table():
        print("重建数据库失败")
        return False
    
    print("数据库重建成功")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
