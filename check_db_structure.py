#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查数据库表结构
"""

import os
import sys
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "backend" / "repair_management.db"
print(f"数据库路径: {DB_PATH}")

def check_database():
    """检查数据库是否存在"""
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return False

    print(f"数据库文件存在: {DB_PATH}")
    return True

def check_table_structure(table_name):
    """检查表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone() is None:
            print(f"表 {table_name} 不存在")
            return False
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n{table_name}表结构:")
        print("=" * 80)
        print(f"{'序号':<8}{'列名':<25}{'类型':<15}{'非空':<8}{'默认值':<20}{'主键':<8}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<8}{col[1]:<25}{col[2]:<15}{col[3]:<8}{str(col[4]):<20}{col[5]:<8}")
        print("=" * 80)
        
        return True
    except Exception as e:
        print(f"检查表结构失败: {e}")
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    if not check_database():
        return False
    
    # 检查tasks表结构
    check_table_structure("tasks")
    
    # 检查work_items表结构
    check_table_structure("work_items")
    
    return True

if __name__ == "__main__":
    main()
