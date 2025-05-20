from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

from database import get_db
from models.user import User
from models.task import Task, TaskStatus, TaskMaterial, TaskWorkItem
from models.material import Material
from models.work_item import WorkItem
from models.project import Project
from schemas.task import (
    TaskCreate, TaskUpdate, Task as TaskSchema,
    TaskDetail, TaskComplete, TaskMaterialCreate, TaskWorkItemCreate
)
from utils.auth import get_current_active_user
from utils.import_utils import process_import

# 创建日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks")

@router.post("/", response_model=TaskSchema)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 获取任务数据
    task_data = task.dict()

    # 处理工作内容和材料数据
    work_items_str = task_data.pop('work_items', None)
    materials_str = task_data.pop('materials', None)

    # 创建任务
    db_task = Task(
        **task_data,
        created_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 如果有工作内容和材料数据，处理它们
    if work_items_str or materials_str:
        try:
            import json

            # 处理工作内容
            if work_items_str:
                work_items = json.loads(work_items_str)
                for work_item in work_items:
                    if not work_item.get('work_item_id') or not work_item.get('quantity'):
                        continue

                    work_item_id = work_item['work_item_id']
                    quantity = float(work_item['quantity'])

                    # 获取工作内容信息
                    db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
                    if db_work_item:
                        # 计算总价
                        total_price = db_work_item.unit_price * quantity

                        # 创建关联
                        db_task_work_item = TaskWorkItem(
                            task_id=db_task.id,
                            work_item_id=work_item_id,
                            quantity=quantity,
                            unit_price=db_work_item.unit_price,
                            total_price=total_price
                        )
                        db.add(db_task_work_item)

            # 处理材料
            if materials_str:
                materials = json.loads(materials_str)
                for material in materials:
                    if not material.get('material_id') or not material.get('quantity'):
                        continue

                    material_id = material['material_id']
                    quantity = float(material['quantity'])
                    is_company_provided = material.get('is_company_provided', False)

                    # 获取材料信息
                    db_material = db.query(Material).filter(Material.id == material_id).first()
                    if db_material:
                        # 计算总价
                        total_price = db_material.unit_price * quantity

                        # 创建关联
                        db_task_material = TaskMaterial(
                            task_id=db_task.id,
                            material_id=material_id,
                            quantity=quantity,
                            is_company_provided=is_company_provided,
                            unit_price=db_material.unit_price,
                            total_price=total_price
                        )
                        db.add(db_task_material)

            db.commit()
            db.refresh(db_task)
        except Exception as e:
            print(f"处理工作内容和材料数据失败: {str(e)}")
            # 不回滚，保留已创建的任务

    return db_task

@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    return query.offset(skip).limit(limit).all()

@router.get("/my-tasks", response_model=List[TaskSchema])
def read_my_tasks(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Task).filter(Task.assigned_to_id == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{task_id}", response_model=TaskDetail)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="工单不存在")
    return db_task

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 更新工单状态
    update_data = task.dict(exclude_unset=True)

    # 处理工作内容和材料数据
    work_items_str = update_data.pop('work_items', None)
    materials_str = update_data.pop('materials', None)

    # 如果状态变为已接单，设置接单时间和接单人
    if "status" in update_data and update_data["status"] == TaskStatus.ASSIGNED.value:
        if not db_task.assigned_to_id:
            update_data["assigned_to_id"] = current_user.id
        update_data["assigned_at"] = datetime.now()

    # 如果状态变为已完成，设置完成时间
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.now()

    # 更新基本字段
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    # 如果有工作内容和材料数据，处理它们
    if work_items_str or materials_str:
        try:
            import json

            # 清除现有的工作内容和材料
            db.query(TaskWorkItem).filter(TaskWorkItem.task_id == task_id).delete()
            db.query(TaskMaterial).filter(TaskMaterial.task_id == task_id).delete()

            labor_cost = 0.0
            company_material_cost = 0.0
            self_material_cost = 0.0

            # 处理工作内容
            if work_items_str:
                work_items = json.loads(work_items_str)
                for work_item in work_items:
                    if not work_item.get('work_item_id') or not work_item.get('quantity'):
                        continue

                    work_item_id = work_item['work_item_id']
                    quantity = float(work_item['quantity'])

                    # 获取工作内容信息
                    db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
                    if db_work_item:
                        # 计算总价
                        total_price = db_work_item.unit_price * quantity
                        labor_cost += total_price

                        # 创建关联
                        db_task_work_item = TaskWorkItem(
                            task_id=db_task.id,
                            work_item_id=work_item_id,
                            quantity=quantity,
                            unit_price=db_work_item.unit_price,
                            total_price=total_price
                        )
                        db.add(db_task_work_item)

            # 处理材料
            if materials_str:
                materials = json.loads(materials_str)
                for material in materials:
                    if not material.get('material_id') or not material.get('quantity'):
                        continue

                    material_id = material['material_id']
                    quantity = float(material['quantity'])
                    is_company_provided = material.get('is_company_provided', False)

                    # 获取材料信息
                    db_material = db.query(Material).filter(Material.id == material_id).first()
                    if db_material:
                        # 计算总价
                        total_price = db_material.unit_price * quantity

                        # 更新对应的材料费
                        if is_company_provided:
                            company_material_cost += total_price
                        else:
                            self_material_cost += total_price

                        # 创建关联
                        db_task_material = TaskMaterial(
                            task_id=db_task.id,
                            material_id=material_id,
                            quantity=quantity,
                            is_company_provided=is_company_provided,
                            unit_price=db_material.unit_price,
                            total_price=total_price
                        )
                        db.add(db_task_material)

            # 更新费用
            db_task.labor_cost = labor_cost
            db_task.company_material_cost = company_material_cost
            db_task.self_material_cost = self_material_cost
            db_task.material_cost = company_material_cost + self_material_cost
            db_task.total_cost = labor_cost + company_material_cost + self_material_cost

            db.commit()
            db.refresh(db_task)
        except Exception as e:
            print(f"处理工作内容和材料数据失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # 不回滚，保留已更新的任务

    return db_task

@router.post("/{task_id}/complete", response_model=TaskDetail)
def complete_task(
    task_id: int,
    task_complete: TaskComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    if db_task.status == TaskStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="工单已完成")

    # 清除现有的材料和工作内容
    db.query(TaskMaterial).filter(TaskMaterial.task_id == task_id).delete()
    db.query(TaskWorkItem).filter(TaskWorkItem.task_id == task_id).delete()

    total_cost = 0.0

    # 添加材料
    company_material_cost = 0.0
    self_material_cost = 0.0

    for material_item in task_complete.materials:
        db_material = db.query(Material).filter(Material.id == material_item.material_id).first()
        if not db_material:
            raise HTTPException(status_code=404, detail=f"材料ID {material_item.material_id} 不存在")

        material_cost = db_material.unit_price * material_item.quantity
        total_cost += material_cost

        # 更新对应的材料费
        if material_item.is_company_provided:
            company_material_cost += material_cost
        else:
            self_material_cost += material_cost

        db_task_material = TaskMaterial(
            task_id=task_id,
            material_id=material_item.material_id,
            quantity=material_item.quantity,
            is_company_provided=material_item.is_company_provided,
            unit_price=db_material.unit_price,
            total_price=material_cost
        )
        db.add(db_task_material)

    # 添加工作内容
    for work_item in task_complete.work_items:
        db_work_item = db.query(WorkItem).filter(WorkItem.id == work_item.work_item_id).first()
        if not db_work_item:
            raise HTTPException(status_code=404, detail=f"工作内容ID {work_item.work_item_id} 不存在")

        work_cost = db_work_item.unit_price * work_item.quantity
        total_cost += work_cost

        db_task_work_item = TaskWorkItem(
            task_id=task_id,
            work_item_id=work_item.work_item_id,
            quantity=work_item.quantity,
            unit_price=db_work_item.unit_price,
            total_price=work_cost
        )
        db.add(db_task_work_item)

    # 更新工单状态和费用
    db_task.status = TaskStatus.COMPLETED.value
    db_task.completed_at = datetime.now()
    db_task.labor_cost = total_cost - company_material_cost - self_material_cost
    db_task.material_cost = company_material_cost + self_material_cost
    db_task.company_material_cost = company_material_cost
    db_task.self_material_cost = self_material_cost
    db_task.total_cost = total_cost

    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 删除关联的材料和工作内容
    db.query(TaskMaterial).filter(TaskMaterial.task_id == task_id).delete()
    db.query(TaskWorkItem).filter(TaskWorkItem.task_id == task_id).delete()

    db.delete(db_task)
    db.commit()
    return None

@router.options("/import")
async def options_import_tasks():
    """处理OPTIONS预检请求"""
    logger.info("收到工单导入OPTIONS预检请求")
    return {}

@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_tasks(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入工单"""
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()

        # 定义必需字段
        required_fields = ["title"]

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> Task:
            # 转换数据类型
            task_data = {
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "attachment": row.get("attachment", ""),
                "work_list": row.get("work_list", ""),
                "company_material_list": row.get("company_material_list", ""),
                "self_material_list": row.get("self_material_list", ""),
                "labor_cost": float(row.get("labor_cost", 0) or 0),
                "material_cost": float(row.get("material_cost", 0) or 0),
                "status": TaskStatus.PENDING.value,
                "created_by_id": current_user.id,
                "created_at": datetime.now()
            }

            # 处理项目ID
            if "project_id" in row and row["project_id"]:
                project_id = int(row["project_id"])
                # 检查项目是否存在
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    raise ValueError(f"项目ID {project_id} 不存在")
                task_data["project_id"] = project_id

            # 创建工单对象
            db_task = Task(**task_data)
            db.add(db_task)

            return db_task

        # 处理导入
        imported_tasks = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row
        )

        # 提交事务
        db.commit()

        return {"message": f"成功导入 {len(imported_tasks)} 条工单记录"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        print(f"导入工单失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入工单失败: {str(e)}"
        )
    finally:
        file.file.close()

@router.post("/{task_id}/work-items/import", status_code=status.HTTP_201_CREATED)
def import_task_work_items(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入工单工作内容"""
    # 检查工单是否存在
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工单ID {task_id} 不存在"
        )

    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()

        # 定义必需字段
        required_fields = ["project_number", "quantity"]

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> TaskWorkItem:
            # 转换数据类型
            project_number = row.get("project_number", "").strip()
            quantity = float(row.get("quantity", 0) or 0)

            # 检查工作内容是否存在
            db_work_item = db.query(WorkItem).filter(WorkItem.project_number == project_number).first()
            if not db_work_item:
                raise ValueError(f"工作内容编号 {project_number} 不存在")

            # 计算总价
            total_price = db_work_item.unit_price * quantity

            # 创建工单工作内容关联
            db_task_work_item = TaskWorkItem(
                task_id=task_id,
                work_item_id=db_work_item.id,
                quantity=quantity,
                unit_price=db_work_item.unit_price,
                total_price=total_price
            )
            db.add(db_task_work_item)

            return db_task_work_item

        # 处理导入
        imported_work_items = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row
        )

        # 更新工单的施工费
        labor_cost = sum(item.total_price for item in imported_work_items)
        db_task.labor_cost = labor_cost
        db_task.total_cost = labor_cost + db_task.material_cost

        # 提交事务
        db.commit()

        return {"message": f"成功导入 {len(imported_work_items)} 条工作内容记录"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        print(f"导入工作内容失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入工作内容失败: {str(e)}"
        )
    finally:
        file.file.close()

@router.post("/{task_id}/materials/import", status_code=status.HTTP_201_CREATED)
def import_task_materials(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入工单材料"""
    # 检查工单是否存在
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工单ID {task_id} 不存在"
        )

    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()

        # 定义必需字段
        required_fields = ["code", "quantity"]

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> TaskMaterial:
            # 转换数据类型
            code = row.get("code", "").strip()
            quantity = float(row.get("quantity", 0) or 0)

            # 处理是否甲供
            is_company_provided_str = row.get("is_company_provided", "").lower()
            is_company_provided = is_company_provided_str in ["true", "1", "yes", "y", "是", "甲供"]

            # 检查材料是否存在
            db_material = db.query(Material).filter(Material.code == code).first()
            if not db_material:
                raise ValueError(f"材料编号 {code} 不存在")

            # 计算总价
            total_price = db_material.unit_price * quantity

            # 创建工单材料关联
            db_task_material = TaskMaterial(
                task_id=task_id,
                material_id=db_material.id,
                quantity=quantity,
                is_company_provided=is_company_provided,
                unit_price=db_material.unit_price,
                total_price=total_price
            )
            db.add(db_task_material)

            return db_task_material

        # 处理导入
        imported_materials = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row
        )

        # 更新工单的材料费
        company_material_cost = sum(item.total_price for item in imported_materials if item.is_company_provided)
        self_material_cost = sum(item.total_price for item in imported_materials if not item.is_company_provided)
        material_cost = company_material_cost + self_material_cost

        db_task.company_material_cost = company_material_cost
        db_task.self_material_cost = self_material_cost
        db_task.material_cost = material_cost
        db_task.total_cost = db_task.labor_cost + material_cost

        # 提交事务
        db.commit()

        return {"message": f"成功导入 {len(imported_materials)} 条材料记录"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        print(f"导入材料失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入材料失败: {str(e)}"
        )
    finally:
        file.file.close()
