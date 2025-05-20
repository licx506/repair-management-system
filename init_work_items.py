#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化工作内容数据
"""

import os
import sys
import traceback
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))
print(f"Python路径: {sys.path}")

# 导入模型和数据库配置
try:
    print("尝试导入数据库配置...")
    from backend.database import Base, SQLALCHEMY_DATABASE_URL
    from backend.models.work_item import WorkItem, WorkItemCategory
    print("导入成功")
except ImportError as e:
    print(f"导入失败: {e}")
    print("尝试使用相对导入...")
    try:
        from database import Base, SQLALCHEMY_DATABASE_URL
        from models.work_item import WorkItem, WorkItemCategory
        print("相对导入成功")
    except ImportError as e2:
        print(f"相对导入也失败了: {e2}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"目录内容: {os.listdir('.')}")
        if os.path.exists('backend'):
            print(f"backend目录内容: {os.listdir('backend')}")
        sys.exit(1)

# 创建数据库连接
print(f"数据库URL: {SQLALCHEMY_DATABASE_URL}")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 示例工作内容数据
sample_work_items = [
    {
        "category": WorkItemCategory.LINE.value,
        "project_number": "TXL2-001",
        "name": "挖、松填光（电）缆沟及接头坑 普通土",
        "description": "普通土壤条件下的挖掘和回填工作",
        "unit": "百立方米",
        "skilled_labor_days": 0,
        "unskilled_labor_days": 39.38,
        "unit_price": 5
    },
    {
        "category": WorkItemCategory.LINE.value,
        "project_number": "TXL2-002",
        "name": "挖、松填光（电）缆沟及接头坑 硬土",
        "description": "硬土壤条件下的挖掘和回填工作",
        "unit": "百立方米",
        "skilled_labor_days": 0,
        "unskilled_labor_days": 45.5,
        "unit_price": 6
    },
    {
        "category": WorkItemCategory.LINE.value,
        "project_number": "TXL2-003",
        "name": "挖、松填光（电）缆沟及接头坑 冻土",
        "description": "冻土条件下的挖掘和回填工作",
        "unit": "百立方米",
        "skilled_labor_days": 0,
        "unskilled_labor_days": 52.8,
        "unit_price": 7.5
    },
    {
        "category": WorkItemCategory.POWER.value,
        "project_number": "TXDY-001",
        "name": "安装电源设备 小型",
        "description": "小型电源设备的安装",
        "unit": "台",
        "skilled_labor_days": 2.5,
        "unskilled_labor_days": 1.2,
        "unit_price": 120
    },
    {
        "category": WorkItemCategory.POWER.value,
        "project_number": "TXDY-002",
        "name": "安装电源设备 中型",
        "description": "中型电源设备的安装",
        "unit": "台",
        "skilled_labor_days": 3.8,
        "unskilled_labor_days": 2.5,
        "unit_price": 180
    }
]

def init_work_items():
    """初始化工作内容数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_count = db.query(WorkItem).count()
        print(f"当前工作内容表中有 {existing_count} 条记录")

        if existing_count > 0:
            print("工作内容表已有数据，跳过初始化")
            return

        # 添加示例数据
        for item_data in sample_work_items:
            work_item = WorkItem(**item_data)
            db.add(work_item)

        db.commit()
        print(f"成功添加 {len(sample_work_items)} 条工作内容记录")
    except Exception as e:
        db.rollback()
        print(f"初始化工作内容数据失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("开始初始化工作内容数据...")

    try:
        # 检查数据库连接
        print("检查数据库连接...")
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        print("数据库连接正常")

        # 初始化数据
        init_work_items()
        print("初始化完成")
        return True
    except Exception as e:
        print(f"初始化失败: {e}")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常堆栈: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
