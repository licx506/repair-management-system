#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库管理工具
提供数据库初始化、检查和修复功能
"""

import os
import sys
import sqlite3
import shutil
import traceback
from pathlib import Path
import argparse
import logging
from datetime import datetime

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
DB_PATH = BACKEND_DIR / "repair_management.db"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_manager")

def backup_database():
    """备份数据库"""
    if not os.path.exists(DB_PATH):
        logger.warning(f"数据库文件不存在: {DB_PATH}")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{DB_PATH}.{timestamp}.bak"
    logger.info(f"备份数据库到 {backup_path}")

    try:
        shutil.copy2(DB_PATH, backup_path)
        logger.info("数据库备份成功")
        return True
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")
        return False

def check_database():
    """检查数据库是否存在"""
    if not os.path.exists(DB_PATH):
        logger.warning(f"数据库文件不存在: {DB_PATH}")
        return False

    logger.info(f"数据库文件存在: {DB_PATH}")
    return True

def check_table_structure(table_name):
    """检查表结构"""
    if not check_database():
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone() is None:
            logger.warning(f"表 {table_name} 不存在")
            return False

        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        logger.info(f"\n{table_name}表结构:")
        logger.info("=" * 80)
        logger.info(f"{'序号':<8}{'列名':<25}{'类型':<15}{'非空':<8}{'默认值':<20}{'主键':<8}")
        logger.info("-" * 80)
        for col in columns:
            logger.info(f"{col[0]:<8}{col[1]:<25}{col[2]:<15}{col[3]:<8}{str(col[4]):<20}{col[5]:<8}")
        logger.info("=" * 80)

        return True
    except Exception as e:
        logger.error(f"检查表结构失败: {e}")
        return False
    finally:
        conn.close()

def fix_tasks_table():
    """修复tasks表结构"""
    if not check_database():
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if cursor.fetchone() is None:
            logger.warning("tasks表不存在，无需修复")
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

        if not missing_columns:
            logger.info("tasks表结构完整，无需修复")
            return True

        logger.info(f"tasks表缺少以下列: {[col[0] for col in missing_columns]}")

        # 添加缺失的列
        for col_name, col_type in missing_columns:
            logger.info(f"添加列 {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")

        conn.commit()
        logger.info("tasks表结构修复完成")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"修复tasks表结构失败: {e}")
        return False
    finally:
        conn.close()

def rebuild_work_items_table():
    """重建工作内容表"""
    if not check_database():
        return False

    logger.info(f"正在重建工作内容表...")

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_items'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # 获取现有数据
            logger.info("获取现有工作内容数据...")
            cursor.execute("SELECT * FROM work_items")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

            # 创建临时表
            logger.info("创建临时表...")
            cursor.execute("CREATE TABLE work_items_temp (id INTEGER PRIMARY KEY, category TEXT, project_number TEXT UNIQUE, name TEXT, description TEXT, unit TEXT, skilled_labor_days FLOAT, unskilled_labor_days FLOAT, unit_price FLOAT, is_active BOOLEAN, created_at TIMESTAMP, updated_at TIMESTAMP)")

            # 将数据迁移到临时表
            if rows:
                logger.info(f"迁移 {len(rows)} 条数据到临时表...")
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
            logger.info("删除原表并重命名临时表...")
            cursor.execute("DROP TABLE work_items")
            cursor.execute("ALTER TABLE work_items_temp RENAME TO work_items")

            # 创建索引
            logger.info("创建索引...")
            cursor.execute("CREATE INDEX ix_work_items_category ON work_items (category)")
            cursor.execute("CREATE INDEX ix_work_items_project_number ON work_items (project_number)")
            cursor.execute("CREATE INDEX ix_work_items_name ON work_items (name)")

            logger.info("工作内容表重建完成")
        else:
            # 创建新表
            logger.info("创建工作内容表...")
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
            logger.info("创建索引...")
            cursor.execute("CREATE INDEX ix_work_items_category ON work_items (category)")
            cursor.execute("CREATE INDEX ix_work_items_project_number ON work_items (project_number)")
            cursor.execute("CREATE INDEX ix_work_items_name ON work_items (name)")

            logger.info("工作内容表创建完成")

        # 提交更改
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"重建工作内容表失败: {e}")
        return False
    finally:
        conn.close()

def create_database_directly():
    """直接创建数据库（不通过后端服务）"""
    logger.info("直接创建数据库...")
    try:
        # 创建数据库连接
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 创建用户表
        logger.info("创建用户表...")
        cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(100) NOT NULL,
            full_name VARCHAR(100),
            phone VARCHAR(20),
            role VARCHAR(20) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建项目表
        logger.info("创建项目表...")
        cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            location VARCHAR(100),
            contact_name VARCHAR(50),
            contact_phone VARCHAR(20),
            status VARCHAR(20) NOT NULL,
            priority INTEGER DEFAULT 3,
            created_by_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (created_by_id) REFERENCES users (id)
        )
        """)

        # 创建工单表
        logger.info("创建工单表...")
        cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL,
            priority INTEGER DEFAULT 3,
            created_by_id INTEGER,
            assigned_to_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            assigned_at TIMESTAMP,
            completed_at TIMESTAMP,
            attachment VARCHAR,
            work_list VARCHAR,
            company_material_list VARCHAR,
            self_material_list VARCHAR,
            labor_cost FLOAT DEFAULT 0.0,
            material_cost FLOAT DEFAULT 0.0,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (created_by_id) REFERENCES users (id),
            FOREIGN KEY (assigned_to_id) REFERENCES users (id)
        )
        """)

        # 创建材料表
        logger.info("创建材料表...")
        cursor.execute("""
        CREATE TABLE materials (
            id INTEGER PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            unit VARCHAR(20) NOT NULL,
            unit_price FLOAT NOT NULL,
            supply_type VARCHAR(20) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """)

        # 创建工作内容表
        logger.info("创建工作内容表...")
        cursor.execute("""
        CREATE TABLE work_items (
            id INTEGER PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            project_number VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            unit VARCHAR(20) NOT NULL,
            skilled_labor_days FLOAT DEFAULT 0.0,
            unskilled_labor_days FLOAT DEFAULT 0.0,
            unit_price FLOAT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """)

        # 创建团队表
        logger.info("创建团队表...")
        cursor.execute("""
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 创建团队成员表
        logger.info("创建团队成员表...")
        cursor.execute("""
        CREATE TABLE team_members (
            id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            is_leader BOOLEAN NOT NULL DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (team_id, user_id)
        )
        """)

        # 创建任务材料关联表
        logger.info("创建任务材料关联表...")
        cursor.execute("""
        CREATE TABLE task_materials (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity FLOAT NOT NULL,
            unit_price FLOAT NOT NULL,
            total_price FLOAT NOT NULL,
            supply_type VARCHAR(20) NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (material_id) REFERENCES materials (id)
        )
        """)

        # 创建任务工作内容关联表
        logger.info("创建任务工作内容关联表...")
        cursor.execute("""
        CREATE TABLE task_work_items (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            work_item_id INTEGER NOT NULL,
            quantity FLOAT NOT NULL,
            unit_price FLOAT NOT NULL,
            total_price FLOAT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (work_item_id) REFERENCES work_items (id)
        )
        """)

        # 创建索引
        logger.info("创建索引...")
        cursor.execute("CREATE INDEX ix_users_username ON users (username)")
        cursor.execute("CREATE INDEX ix_users_email ON users (email)")
        cursor.execute("CREATE INDEX ix_projects_status ON projects (status)")
        cursor.execute("CREATE INDEX ix_tasks_status ON tasks (status)")
        cursor.execute("CREATE INDEX ix_tasks_project_id ON tasks (project_id)")
        cursor.execute("CREATE INDEX ix_tasks_assigned_to_id ON tasks (assigned_to_id)")
        cursor.execute("CREATE INDEX ix_materials_category ON materials (category)")
        cursor.execute("CREATE INDEX ix_materials_code ON materials (code)")
        cursor.execute("CREATE INDEX ix_work_items_category ON work_items (category)")
        cursor.execute("CREATE INDEX ix_work_items_project_number ON work_items (project_number)")

        # 提交更改
        conn.commit()
        logger.info("数据库创建成功")

        # 检查表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"创建的表: {[table[0] for table in tables]}")

        return True
    except Exception as e:
        logger.error(f"直接创建数据库失败: {e}")
        logger.error(traceback.format_exc())
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def initialize_database():
    """初始化数据库"""
    logger.info("初始化数据库...")

    # 检查数据库文件是否存在
    if os.path.exists(DB_PATH):
        logger.warning(f"数据库文件已存在: {DB_PATH}")
        choice = input("是否要删除现有数据库并重新初始化？(y/n): ")
        if choice.lower() != 'y':
            logger.info("取消初始化")
            return False

        # 备份现有数据库
        backup_database()

        # 删除现有数据库
        logger.info(f"删除现有数据库: {DB_PATH}")
        os.remove(DB_PATH)

    # 尝试方法1：启动后端服务创建数据库
    logger.info("方法1：启动后端服务创建数据库...")
    try:
        # 导入run模块
        sys.path.append(str(ROOT_DIR))
        from run import start_backend, stop_backend

        # 启动后端
        process = start_backend(background=True)
        if not process:
            logger.error("启动后端服务失败")
            logger.info("尝试方法2：直接创建数据库...")
            return create_database_directly()

        # 等待数据库创建，最多等待30秒
        import time
        max_wait_time = 30  # 最大等待时间（秒）
        wait_interval = 2   # 检查间隔（秒）
        total_wait_time = 0

        logger.info(f"等待数据库创建，最多等待 {max_wait_time} 秒...")
        while total_wait_time < max_wait_time:
            if os.path.exists(DB_PATH):
                logger.info(f"数据库文件已创建: {DB_PATH}")
                # 再等待2秒确保数据库初始化完成
                time.sleep(2)
                break

            time.sleep(wait_interval)
            total_wait_time += wait_interval
            logger.info(f"已等待 {total_wait_time} 秒...")

        # 停止后端
        logger.info("停止后端服务...")
        stop_backend()

        # 检查数据库是否创建成功
        if not os.path.exists(DB_PATH):
            logger.error("方法1失败：数据库未创建")
            logger.info("尝试方法2：直接创建数据库...")
            return create_database_directly()

        # 检查数据库是否可以连接
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()

            if not tables:
                logger.error("方法1失败：数据库创建但没有表")
                logger.info("尝试方法2：直接创建数据库...")
                os.remove(DB_PATH)
                return create_database_directly()

            logger.info(f"数据库创建成功，包含以下表: {[table[0] for table in tables]}")
            return True
        except Exception as e:
            logger.error(f"数据库创建成功，但无法连接: {e}")
            logger.info("尝试方法2：直接创建数据库...")
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            return create_database_directly()
    except Exception as e:
        logger.error(f"方法1失败：{e}")
        logger.error(traceback.format_exc())
        logger.info("尝试方法2：直接创建数据库...")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        return create_database_directly()

def create_admin_user():
    """创建管理员用户"""
    if not check_database():
        logger.error("数据库不存在，无法创建管理员用户")
        return False

    try:
        # 导入密码哈希工具
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            logger.error("users表不存在，无法创建管理员用户")
            return False

        # 检查是否已存在管理员用户
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone():
            logger.info("管理员用户已存在")
            return True

        # 获取管理员信息
        print("\n创建管理员用户")
        print("=" * 50)
        username = input("用户名 (默认: admin): ") or "admin"
        password = input("密码 (默认: admin123): ") or "admin123"
        email = input("邮箱 (默认: admin@example.com): ") or "admin@example.com"
        full_name = input("姓名 (默认: 管理员): ") or "管理员"

        # 创建密码哈希
        hashed_password = pwd_context.hash(password)

        # 插入管理员用户
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, hashed_password, full_name, "admin", 1)
        )

        # 提交更改
        conn.commit()
        logger.info(f"管理员用户 '{username}' 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建管理员用户失败: {e}")
        logger.error(traceback.format_exc())
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('--check', action='store_true', help='检查数据库结构')
    parser.add_argument('--fix', action='store_true', help='修复数据库结构')
    parser.add_argument('--rebuild', action='store_true', help='重建工作内容表')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--backup', action='store_true', help='备份数据库')
    parser.add_argument('--create-admin', action='store_true', help='创建管理员用户')
    parser.add_argument('--table', help='指定要检查的表名')

    args = parser.parse_args()

    # 如果没有指定任何参数，显示交互式菜单
    if not any(vars(args).values()):
        show_menu()
        return

    # 执行指定的操作
    if args.backup:
        backup_database()

    if args.init:
        if initialize_database() and input("是否创建管理员用户？(y/n): ").lower() == 'y':
            create_admin_user()

    if args.create_admin:
        create_admin_user()

    if args.check:
        if args.table:
            check_table_structure(args.table)
        else:
            check_database()
            check_table_structure('tasks')
            check_table_structure('work_items')
            check_table_structure('materials')
            check_table_structure('users')

    if args.fix:
        backup_database()
        fix_tasks_table()

    if args.rebuild:
        backup_database()
        rebuild_work_items_table()

def show_menu():
    """显示交互式菜单"""
    while True:
        print("\n" + "="*50)
        print("数据库管理工具".center(50))
        print("="*50)
        print("1. 检查数据库结构")
        print("2. 修复数据库结构")
        print("3. 重建工作内容表")
        print("4. 初始化数据库")
        print("5. 备份数据库")
        print("6. 创建管理员用户")
        print("0. 退出")
        print("="*50)

        choice = input("请选择操作 [0-6]: ")

        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            check_database()
            check_table_structure('tasks')
            check_table_structure('work_items')
            check_table_structure('materials')
            check_table_structure('users')
        elif choice == '2':
            backup_database()
            fix_tasks_table()
        elif choice == '3':
            backup_database()
            rebuild_work_items_table()
        elif choice == '4':
            if initialize_database() and input("是否创建管理员用户？(y/n): ").lower() == 'y':
                create_admin_user()
        elif choice == '5':
            backup_database()
        elif choice == '6':
            create_admin_user()
        else:
            print("无效的选择，请重试")

if __name__ == "__main__":
    main()
