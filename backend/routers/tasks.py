from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from models.task import Task, TaskStatus, TaskMaterial, TaskWorkItem
from models.material import Material
from models.work_item import WorkItem
from schemas.task import (
    TaskCreate, TaskUpdate, Task as TaskSchema, 
    TaskDetail, TaskComplete, TaskMaterialCreate, TaskWorkItemCreate
)
from utils.auth import get_current_active_user

router = APIRouter(prefix="/tasks")

@router.post("/", response_model=TaskSchema)
def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_task = Task(
        **task.dict(),
        created_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
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
    
    # 如果状态变为已接单，设置接单时间和接单人
    if "status" in update_data and update_data["status"] == TaskStatus.ASSIGNED.value:
        if not db_task.assigned_to_id:
            update_data["assigned_to_id"] = current_user.id
        update_data["assigned_at"] = datetime.now()
    
    # 如果状态变为已完成，设置完成时间
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
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
    for material_item in task_complete.materials:
        db_material = db.query(Material).filter(Material.id == material_item.material_id).first()
        if not db_material:
            raise HTTPException(status_code=404, detail=f"材料ID {material_item.material_id} 不存在")
        
        material_cost = db_material.unit_price * material_item.quantity
        total_cost += material_cost
        
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
    
    # 更新工单状态和总费用
    db_task.status = TaskStatus.COMPLETED.value
    db_task.completed_at = datetime.now()
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
