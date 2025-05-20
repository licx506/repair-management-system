#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查工作内容数据库表
"""

import os
import sys
import sqlite3
from pathlib import Path
import traceback

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

def check_work_items_table():
    """检查工作内容表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_items'")
        if cursor.fetchone() is None:
            print("work_items表不存在")
            return False

        print("work_items表存在")

        # 获取表结构
        cursor.execute("PRAGMA table_info(work_items)")
        columns = cursor.fetchall()

        print("\n工作内容表结构:")
        print("=" * 80)
        print(f"{'序号':<5} {'列名':<20} {'类型':<10} {'非空':<5} {'默认值':<20} {'主键':<5}")
        print("-" * 80)

        for col in columns:
            cid, name, type_, notnull, dflt_value, pk = col
            print(f"{cid:<5} {name:<20} {type_:<10} {notnull:<5} {str(dflt_value):<20} {pk:<5}")

        print("=" * 80)

        # 检查是否有category列
        has_category = any(col[1] == 'category' for col in columns)
        if not has_category:
            print("\n警告: 工作内容表缺少category列")
        else:
            print("\n工作内容表包含category列")

        # 检查是否有skilled_labor_days和unskilled_labor_days列
        has_skilled = any(col[1] == 'skilled_labor_days' for col in columns)
        has_unskilled = any(col[1] == 'unskilled_labor_days' for col in columns)

        if not has_skilled:
            print("警告: 工作内容表缺少skilled_labor_days列")
        else:
            print("工作内容表包含skilled_labor_days列")

        if not has_unskilled:
            print("警告: 工作内容表缺少unskilled_labor_days列")
        else:
            print("工作内容表包含unskilled_labor_days列")

        return True
    except Exception as e:
        print(f"检查工作内容表结构失败: {e}")
        return False
    finally:
        conn.close()

def count_work_items():
    """统计工作内容数量"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM work_items")
        count = cursor.fetchone()[0]
        print(f"\n工作内容总数: {count}")

        if count > 0:
            # 获取前10条记录
            cursor.execute("SELECT id, category, project_number, name, unit_price FROM work_items LIMIT 10")
            items = cursor.fetchall()

            print("\n前10条工作内容记录:")
            print("=" * 100)
            print(f"{'ID':<5} {'分类':<15} {'项目编号':<15} {'名称':<30} {'单价':<10}")
            print("-" * 100)

            for item in items:
                id_, category, project_number, name, unit_price = item
                print(f"{id_:<5} {category or '无':<15} {project_number or '无':<15} {name or '无':<30} {unit_price or 0:<10}")

            print("=" * 100)

        return count
    except Exception as e:
        print(f"统计工作内容数量失败: {e}")
        return 0
    finally:
        conn.close()

def main():
    """主函数"""
    print("开始检查工作内容数据...")

    if not check_database():
        return False

    if not check_work_items_table():
        return False

    count = count_work_items()

    if count == 0:
        print("\n警告: 工作内容表中没有数据")

    print("\n检查完成")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
