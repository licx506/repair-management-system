from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database import get_db
from models.user import User
from models.work_item import WorkItem, WorkItemCategory
from schemas.work_item import WorkItemCreate, WorkItemUpdate, WorkItem as WorkItemSchema
from utils.auth import get_current_active_user
from utils.import_utils import process_import

# 创建日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/work-items")

@router.get("/categories", response_model=List[str])
def get_work_item_categories():
    """获取所有工作项分类"""
    return [category.value for category in WorkItemCategory]

@router.post("/", response_model=WorkItemSchema)
def create_work_item(
    work_item: WorkItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # 打印请求数据，用于调试
        print(f"接收到的工作内容数据: {work_item.dict()}")

        # 检查项目编号是否已存在
        existing_item = db.query(WorkItem).filter(WorkItem.project_number == work_item.project_number).first()
        if existing_item:
            print(f"项目编号 '{work_item.project_number}' 已存在")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目编号 '{work_item.project_number}' 已存在"
            )

        # 确保数值字段有默认值
        work_item_dict = work_item.dict()
        work_item_dict["skilled_labor_days"] = work_item_dict.get("skilled_labor_days", 0.0) or 0.0
        work_item_dict["unskilled_labor_days"] = work_item_dict.get("unskilled_labor_days", 0.0) or 0.0
        work_item_dict["unit_price"] = work_item_dict.get("unit_price", 0.0) or 0.0

        # 确保category字段有值
        if "category" not in work_item_dict or not work_item_dict["category"]:
            work_item_dict["category"] = "通信线路"

        print(f"处理后的工作内容数据: {work_item_dict}")

        # 创建工作内容对象
        try:
            db_work_item = WorkItem(**work_item_dict)
            print(f"创建的工作内容对象: {db_work_item.__dict__}")
        except Exception as e:
            print(f"创建工作内容对象失败: {str(e)}")
            raise

        # 添加到数据库
        try:
            db.add(db_work_item)
            db.commit()
            db.refresh(db_work_item)
            print(f"工作内容添加成功，ID: {db_work_item.id}")
            return db_work_item
        except Exception as e:
            print(f"数据库操作失败: {str(e)}")
            db.rollback()
            raise
    except HTTPException as e:
        # 直接抛出HTTP异常
        print(f"HTTP异常: {e.detail}")
        raise
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        error_msg = f"创建工作内容失败: {str(e)}"
        print(error_msg)
        print(f"异常类型: {type(e).__name__}")
        import traceback
        print(f"异常堆栈: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.get("/", response_model=List[WorkItemSchema])
def read_work_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="项目分类"),
    project_number: Optional[str] = Query(None, description="项目编号"),
    name: Optional[str] = Query(None, description="工作项名称"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print(f"获取工作内容列表，参数: skip={skip}, limit={limit}, category={category}, project_number={project_number}, name={name}, is_active={is_active}")

    try:
        # 构建查询
        query = db.query(WorkItem)

        # 应用过滤条件
        if category:
            query = query.filter(WorkItem.category == category)
        if project_number:
            query = query.filter(WorkItem.project_number == project_number)
        if name:
            query = query.filter(WorkItem.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.filter(WorkItem.is_active == is_active)

        # 执行查询
        items = query.all()
        print(f"查询成功，找到 {len(items)} 条工作内容记录")

        # 打印前5条记录，用于调试
        for i, item in enumerate(items[:5]):
            print(f"记录 {i+1}: ID={item.id}, 名称={item.name}")

        # 确保所有必需字段都有值
        result = []
        from datetime import datetime
        for item in items:
            # 确保created_at字段有值
            if item.created_at is None:
                item.created_at = datetime.now()
            result.append(item)

        return result
    except Exception as e:
        # 记录详细错误信息
        error_msg = f"获取工作内容列表失败: {str(e)}"
        print(error_msg)
        print(f"异常类型: {type(e).__name__}")
        import traceback
        print(f"异常堆栈: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.get("/{work_item_id}", response_model=WorkItemSchema)
def read_work_item(
    work_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if db_work_item is None:
        raise HTTPException(status_code=404, detail="工作内容不存在")
    return db_work_item

@router.put("/{work_item_id}", response_model=WorkItemSchema)
def update_work_item(
    work_item_id: int,
    work_item: WorkItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if db_work_item is None:
        raise HTTPException(status_code=404, detail="工作内容不存在")

    update_data = work_item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_work_item, key, value)

    db.commit()
    db.refresh(db_work_item)
    return db_work_item

@router.delete("/{work_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_item(
    work_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if db_work_item is None:
        raise HTTPException(status_code=404, detail="工作内容不存在")

    # 检查是否有关联的任务工作内容
    if db_work_item.task_usages:
        # 不直接删除，而是设置为非活动状态
        db_work_item.is_active = False
        db.commit()
    else:
        db.delete(db_work_item)
        db.commit()

    return None

@router.options("/import")
async def options_import_work_items():
    """处理OPTIONS预检请求"""
    logger.info("收到工作内容导入OPTIONS预检请求")
    return {}

@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_work_items(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入工作内容"""
    logger.info(f"收到工作内容导入请求，文件名: {file.filename}")

    if not file.filename.endswith(('.csv', '.CSV')):
        logger.warning(f"文件格式不支持: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()
        logger.info(f"成功读取文件内容，大小: {len(file_content)} 字节")

        # 定义必需字段
        required_fields = ["category", "project_number", "name", "unit", "unit_price"]
        logger.debug(f"必需字段: {required_fields}")

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> WorkItem:
            # 记录正在处理的行
            logger.debug(f"处理行数据: {row}")

            # 转换数据类型
            work_item_data = {
                "category": row.get("category", "通信线路"),
                "project_number": row.get("project_number", ""),
                "name": row.get("name", ""),
                "description": row.get("description", ""),
                "unit": row.get("unit", ""),
                "skilled_labor_days": float(row.get("skilled_labor_days", 0) or 0),
                "unskilled_labor_days": float(row.get("unskilled_labor_days", 0) or 0),
                "unit_price": float(row.get("unit_price", 0) or 0),
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 验证必填字段
            for field in ["project_number", "name", "unit"]:
                if not work_item_data[field]:
                    error_msg = f"字段 '{field}' 不能为空"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            # 检查项目编号是否已存在
            existing_item = db.query(WorkItem).filter(WorkItem.project_number == work_item_data["project_number"]).first()
            if existing_item:
                error_msg = f"项目编号 '{work_item_data['project_number']}' 已存在"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # 创建工作内容对象
            try:
                db_work_item = WorkItem(**work_item_data)
                db.add(db_work_item)
                logger.debug(f"成功创建工作内容对象: {work_item_data['project_number']}")
                return db_work_item
            except Exception as e:
                error_msg = f"创建工作内容对象失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 定义验证函数
        def validate_data(rows: List[Dict[str, Any]]) -> None:
            logger.info(f"开始验证数据，共 {len(rows)} 行")

            # 检查项目编号是否唯一
            project_numbers = [row.get("project_number") for row in rows if row.get("project_number")]
            if len(project_numbers) != len(set(project_numbers)):
                error_msg = "CSV文件中存在重复的项目编号"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # 检查是否有空的项目编号
            if any(not pn for pn in project_numbers):
                error_msg = "CSV文件中存在空的项目编号"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("数据验证通过")

        # 处理导入
        logger.info("开始处理导入")
        imported_items = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row,
            validate_func=validate_data
        )

        # 提交事务
        db.commit()
        logger.info(f"成功导入 {len(imported_items)} 条工作内容记录")

        return {"message": f"成功导入 {len(imported_items)} 条工作内容记录"}
    except ValueError as e:
        db.rollback()
        logger.error(f"导入数据验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"导入工作内容失败: {str(e)}")
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入工作内容失败: {str(e)}"
        )
    finally:
        file.file.close()
        logger.info("导入处理完成，文件已关闭")
