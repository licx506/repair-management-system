from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from models.project import Project, ProjectStatus
from schemas.project import ProjectCreate, ProjectUpdate, Project as ProjectSchema, ProjectDetail
from utils.auth import get_current_active_user

router = APIRouter(prefix="/projects")

@router.post("/", response_model=ProjectSchema)
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = Project(
        **project.dict(),
        created_by_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=ProjectDetail)
def read_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 计算任务统计信息
    tasks_count = len(db_project.tasks)
    completed_tasks_count = sum(1 for task in db_project.tasks if task.status == "completed")
    
    # 创建返回对象
    result = ProjectDetail(
        **{c.name: getattr(db_project, c.name) for c in db_project.__table__.columns},
        tasks_count=tasks_count,
        completed_tasks_count=completed_tasks_count
    )
    
    return result

@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int, 
    project: ProjectUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 更新项目状态
    update_data = project.dict(exclude_unset=True)
    
    # 如果状态变为已完成，设置完成时间
    if "status" in update_data and update_data["status"] == ProjectStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查是否有关联的任务
    if db_project.tasks:
        raise HTTPException(status_code=400, detail="无法删除有关联任务的项目")
    
    db.delete(db_project)
    db.commit()
    return None
