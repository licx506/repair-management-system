#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复数据库表结构
"""

import os
import sys
import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "backend" / "repair_management.db"
print(f"数据库路径: {DB_PATH}")

def backup_database():
    """备份数据库"""
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.bak"
        print(f"备份数据库到 {backup_path}")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        return True
    return False

def fix_tasks_table():
    """修复tasks表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if cursor.fetchone() is None:
            print("tasks表不存在，无需修复")
            return False

        # 检查列是否存在
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]

        # 添加缺失的列
        missing_columns = []
        if "attachment" not in columns:
            missing_columns.append(("attachment", "VARCHAR"))
        if "work_list" not in columns:
            missing_columns.append(("work_list", "VARCHAR"))
        if "company_material_list" not in columns:
            missing_columns.append(("company_material_list", "VARCHAR"))
        if "self_material_list" not in columns:
            missing_columns.append(("self_material_list", "VARCHAR"))
        if "labor_cost" not in columns:
            missing_columns.append(("labor_cost", "FLOAT DEFAULT 0.0"))
        if "material_cost" not in columns:
            missing_columns.append(("material_cost", "FLOAT DEFAULT 0.0"))
        if "company_material_cost" not in columns:
            missing_columns.append(("company_material_cost", "FLOAT DEFAULT 0.0"))
        if "self_material_cost" not in columns:
            missing_columns.append(("self_material_cost", "FLOAT DEFAULT 0.0"))
        if "total_cost" not in columns:
            missing_columns.append(("total_cost", "FLOAT DEFAULT 0.0"))

        if not missing_columns:
            print("tasks表结构完整，无需修复")
            return True

        print(f"tasks表缺少以下列: {[col[0] for col in missing_columns]}")

        # 添加缺失的列
        for col_name, col_type in missing_columns:
            print(f"添加列 {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")

        conn.commit()
        print("tasks表结构修复完成")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修复tasks表结构失败: {e}")
        return False
    finally:
        conn.close()

def fix_materials_table():
    """修复materials表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='materials'")
        if cursor.fetchone() is None:
            print("materials表不存在，无需修复")
            return False

        # 检查列是否存在
        cursor.execute("PRAGMA table_info(materials)")
        columns = [col[1] for col in cursor.fetchall()]

        # 添加缺失的列
        missing_columns = []
        if "category" not in columns:
            missing_columns.append(("category", "VARCHAR"))
        if "code" not in columns:
            missing_columns.append(("code", "VARCHAR"))
        if "description" not in columns:
            missing_columns.append(("description", "TEXT"))
        if "unit" not in columns:
            missing_columns.append(("unit", "VARCHAR"))
        if "unit_price" not in columns:
            missing_columns.append(("unit_price", "FLOAT DEFAULT 0.0"))
        if "supply_type" not in columns:
            missing_columns.append(("supply_type", "VARCHAR"))
        if "is_active" not in columns:
            missing_columns.append(("is_active", "BOOLEAN DEFAULT 1"))
        if "created_at" not in columns:
            missing_columns.append(("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"))
        if "updated_at" not in columns:
            missing_columns.append(("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"))

        if not missing_columns:
            print("materials表结构完整，无需修复")
            return True

        print(f"materials表缺少以下列: {[col[0] for col in missing_columns]}")

        # 添加缺失的列
        for col_name, col_type in missing_columns:
            print(f"添加列 {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE materials ADD COLUMN {col_name} {col_type}")

        conn.commit()
        print("materials表结构修复完成")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修复materials表结构失败: {e}")
        return False
    finally:
        conn.close()

def fix_work_items_table():
    """修复work_items表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_items'")
        if cursor.fetchone() is None:
            print("work_items表不存在，无需修复")
            return False

        # 检查列是否存在
        cursor.execute("PRAGMA table_info(work_items)")
        columns = [col[1] for col in cursor.fetchall()]

        # 添加缺失的列
        missing_columns = []
        if "category" not in columns:
            missing_columns.append(("category", "VARCHAR"))
        if "project_number" not in columns:
            missing_columns.append(("project_number", "VARCHAR"))
        if "name" not in columns:
            missing_columns.append(("name", "VARCHAR"))
        if "unit" not in columns:
            missing_columns.append(("unit", "VARCHAR"))
        if "unit_price" not in columns:
            missing_columns.append(("unit_price", "FLOAT DEFAULT 0.0"))
        if "description" not in columns:
            missing_columns.append(("description", "TEXT"))
        if "is_active" not in columns:
            missing_columns.append(("is_active", "BOOLEAN DEFAULT 1"))
        if "created_at" not in columns:
            missing_columns.append(("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"))
        if "updated_at" not in columns:
            missing_columns.append(("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"))

        if not missing_columns:
            print("work_items表结构完整，无需修复")
            return True

        print(f"work_items表缺少以下列: {[col[0] for col in missing_columns]}")

        # 添加缺失的列
        for col_name, col_type in missing_columns:
            print(f"添加列 {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE work_items ADD COLUMN {col_name} {col_type}")

        conn.commit()
        print("work_items表结构修复完成")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修复work_items表结构失败: {e}")
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return False

    # 备份数据库
    backup_database()

    # 修复各个表结构
    fix_tasks_table()
    fix_materials_table()
    fix_work_items_table()

    print("数据库结构修复完成")
    return True

if __name__ == "__main__":
    main()
