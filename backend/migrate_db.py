import sqlite3
import os
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent / "repair_management.db"

def migrate_database():
    """
    执行数据库迁移，添加新字段到现有表中
    """
    print(f"开始数据库迁移，数据库路径: {DB_PATH}")

    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"目录内容: {os.listdir(Path(__file__).parent)}")
        return

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查 work_items 表中是否已有 skilled_labor_days 和 unskilled_labor_days 字段
        cursor.execute("PRAGMA table_info(work_items)")
        columns = [column[1] for column in cursor.fetchall()]

        # 添加 skilled_labor_days 字段
        if 'skilled_labor_days' not in columns:
            print("添加 skilled_labor_days 字段到 work_items 表")
            cursor.execute("ALTER TABLE work_items ADD COLUMN skilled_labor_days FLOAT DEFAULT 0.0")

        # 添加 unskilled_labor_days 字段
        if 'unskilled_labor_days' not in columns:
            print("添加 unskilled_labor_days 字段到 work_items 表")
            cursor.execute("ALTER TABLE work_items ADD COLUMN unskilled_labor_days FLOAT DEFAULT 0.0")

        # 检查 materials 表中是否已有 category, code 和 supply_type 字段
        cursor.execute("PRAGMA table_info(materials)")
        columns = [column[1] for column in cursor.fetchall()]

        # 添加 category 字段
        if 'category' not in columns:
            print("添加 category 字段到 materials 表")
            cursor.execute("ALTER TABLE materials ADD COLUMN category VARCHAR DEFAULT '其他'")

        # 添加 code 字段
        if 'code' not in columns:
            print("添加 code 字段到 materials 表")
            # 为现有记录生成唯一编号
            cursor.execute("SELECT id FROM materials")
            material_ids = cursor.fetchall()
            for id_tuple in material_ids:
                material_id = id_tuple[0]
                code = f"M{material_id:04d}"
                cursor.execute("UPDATE materials SET code = ? WHERE id = ?", (code, material_id))

            # 添加字段并设置唯一约束
            cursor.execute("ALTER TABLE materials ADD COLUMN code VARCHAR(20) DEFAULT NULL")

        # 添加 supply_type 字段
        if 'supply_type' not in columns:
            print("添加 supply_type 字段到 materials 表")
            cursor.execute("ALTER TABLE materials ADD COLUMN supply_type VARCHAR DEFAULT '两者皆可'")

        # 提交更改
        conn.commit()
        print("数据库迁移完成")

    except Exception as e:
        conn.rollback()
        print(f"数据库迁移失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
