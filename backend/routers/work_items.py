from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.user import User
from models.work_item import WorkItem, WorkItemCategory
from schemas.work_item import WorkItemCreate, WorkItemUpdate, WorkItem as WorkItemSchema
from utils.auth import get_current_active_user

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
    db_work_item = WorkItem(**work_item.dict())
    db.add(db_work_item)
    db.commit()
    db.refresh(db_work_item)
    return db_work_item

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
    query = db.query(WorkItem)

    # 应用筛选条件
    if category:
        query = query.filter(WorkItem.category == category)
    if project_number:
        query = query.filter(WorkItem.project_number == project_number)
    if name:
        query = query.filter(WorkItem.name.ilike(f"%{name}%"))
    if is_active is not None:
        query = query.filter(WorkItem.is_active == is_active)

    return query.offset(skip).limit(limit).all()

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
