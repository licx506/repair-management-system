from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.project import Project
from models.task import Task, TaskMaterial, TaskWorkItem
from models.material import Material
from models.work_item import WorkItem
from models.team import Team, TeamMember
from utils.auth import get_current_active_user

router = APIRouter(prefix="/statistics")

@router.get("/projects")
def get_project_statistics(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 默认统计最近30天
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # 项目总数
    total_projects = db.query(func.count(Project.id)).filter(
        Project.created_at >= start_date,
        Project.created_at <= end_date
    ).scalar()
    
    # 已完成项目数
    completed_projects = db.query(func.count(Project.id)).filter(
        Project.created_at >= start_date,
        Project.created_at <= end_date,
        Project.status == "completed"
    ).scalar()
    
    # 进行中项目数
    in_progress_projects = db.query(func.count(Project.id)).filter(
        Project.created_at >= start_date,
        Project.created_at <= end_date,
        Project.status == "in_progress"
    ).scalar()
    
    # 待处理项目数
    pending_projects = db.query(func.count(Project.id)).filter(
        Project.created_at >= start_date,
        Project.created_at <= end_date,
        Project.status == "pending"
    ).scalar()
    
    return {
        "total_projects": total_projects,
        "completed_projects": completed_projects,
        "in_progress_projects": in_progress_projects,
        "pending_projects": pending_projects,
        "completion_rate": completed_projects / total_projects if total_projects > 0 else 0
    }

@router.get("/tasks")
def get_task_statistics(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 默认统计最近30天
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # 工单总数
    total_tasks = db.query(func.count(Task.id)).filter(
        Task.created_at >= start_date,
        Task.created_at <= end_date
    ).scalar()
    
    # 已完成工单数
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.created_at >= start_date,
        Task.created_at <= end_date,
        Task.status == "completed"
    ).scalar()
    
    # 进行中工单数
    in_progress_tasks = db.query(func.count(Task.id)).filter(
        Task.created_at >= start_date,
        Task.created_at <= end_date,
        Task.status.in_(["assigned", "in_progress"])
    ).scalar()
    
    # 待处理工单数
    pending_tasks = db.query(func.count(Task.id)).filter(
        Task.created_at >= start_date,
        Task.created_at <= end_date,
        Task.status == "pending"
    ).scalar()
    
    # 平均完成时间（小时）
    avg_completion_time = db.query(
        func.avg(func.extract('epoch', Task.completed_at - Task.created_at) / 3600)
    ).filter(
        Task.created_at >= start_date,
        Task.created_at <= end_date,
        Task.status == "completed"
    ).scalar()
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
        "avg_completion_time_hours": avg_completion_time or 0
    }

@router.get("/materials")
def get_material_statistics(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 默认统计最近30天
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # 查询完成的工单
    completed_tasks = db.query(Task.id).filter(
        Task.completed_at >= start_date,
        Task.completed_at <= end_date,
        Task.status == "completed"
    ).all()
    
    task_ids = [task.id for task in completed_tasks]
    
    if not task_ids:
        return {
            "total_material_cost": 0,
            "company_provided_cost": 0,
            "self_purchased_cost": 0,
            "most_used_materials": []
        }
    
    # 材料总费用
    total_material_cost = db.query(func.sum(TaskMaterial.total_price)).filter(
        TaskMaterial.task_id.in_(task_ids)
    ).scalar() or 0
    
    # 甲供材料费用
    company_provided_cost = db.query(func.sum(TaskMaterial.total_price)).filter(
        TaskMaterial.task_id.in_(task_ids),
        TaskMaterial.is_company_provided == True
    ).scalar() or 0
    
    # 自购材料费用
    self_purchased_cost = db.query(func.sum(TaskMaterial.total_price)).filter(
        TaskMaterial.task_id.in_(task_ids),
        TaskMaterial.is_company_provided == False
    ).scalar() or 0
    
    # 最常用的材料
    most_used_materials = db.query(
        Material.id,
        Material.name,
        func.sum(TaskMaterial.quantity).label("total_quantity"),
        func.sum(TaskMaterial.total_price).label("total_cost")
    ).join(
        TaskMaterial, Material.id == TaskMaterial.material_id
    ).filter(
        TaskMaterial.task_id.in_(task_ids)
    ).group_by(
        Material.id, Material.name
    ).order_by(
        func.sum(TaskMaterial.quantity).desc()
    ).limit(10).all()
    
    return {
        "total_material_cost": total_material_cost,
        "company_provided_cost": company_provided_cost,
        "self_purchased_cost": self_purchased_cost,
        "most_used_materials": [
            {
                "id": material.id,
                "name": material.name,
                "total_quantity": material.total_quantity,
                "total_cost": material.total_cost
            }
            for material in most_used_materials
        ]
    }

@router.get("/work-items")
def get_work_item_statistics(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 默认统计最近30天
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # 查询完成的工单
    completed_tasks = db.query(Task.id).filter(
        Task.completed_at >= start_date,
        Task.completed_at <= end_date,
        Task.status == "completed"
    ).all()
    
    task_ids = [task.id for task in completed_tasks]
    
    if not task_ids:
        return {
            "total_work_item_cost": 0,
            "most_performed_work_items": []
        }
    
    # 工作内容总费用
    total_work_item_cost = db.query(func.sum(TaskWorkItem.total_price)).filter(
        TaskWorkItem.task_id.in_(task_ids)
    ).scalar() or 0
    
    # 最常执行的工作内容
    most_performed_work_items = db.query(
        WorkItem.id,
        WorkItem.name,
        func.sum(TaskWorkItem.quantity).label("total_quantity"),
        func.sum(TaskWorkItem.total_price).label("total_cost")
    ).join(
        TaskWorkItem, WorkItem.id == TaskWorkItem.work_item_id
    ).filter(
        TaskWorkItem.task_id.in_(task_ids)
    ).group_by(
        WorkItem.id, WorkItem.name
    ).order_by(
        func.sum(TaskWorkItem.quantity).desc()
    ).limit(10).all()
    
    return {
        "total_work_item_cost": total_work_item_cost,
        "most_performed_work_items": [
            {
                "id": work_item.id,
                "name": work_item.name,
                "total_quantity": work_item.total_quantity,
                "total_cost": work_item.total_cost
            }
            for work_item in most_performed_work_items
        ]
    }

@router.get("/teams")
def get_team_statistics(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 默认统计最近30天
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # 查询所有团队
    teams = db.query(Team).filter(Team.is_active == True).all()
    
    result = []
    for team in teams:
        # 团队完成的工单数
        completed_tasks_count = db.query(func.count(Task.id)).filter(
            Task.team_id == team.id,
            Task.completed_at >= start_date,
            Task.completed_at <= end_date,
            Task.status == "completed"
        ).scalar() or 0
        
        # 团队总工单数
        total_tasks_count = db.query(func.count(Task.id)).filter(
            Task.team_id == team.id,
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).scalar() or 0
        
        # 团队总收入（工单总费用）
        total_income = db.query(func.sum(Task.total_cost)).filter(
            Task.team_id == team.id,
            Task.completed_at >= start_date,
            Task.completed_at <= end_date,
            Task.status == "completed"
        ).scalar() or 0
        
        # 团队成员数
        members_count = db.query(func.count(TeamMember.id)).filter(
            TeamMember.team_id == team.id
        ).scalar() or 0
        
        result.append({
            "id": team.id,
            "name": team.name,
            "completed_tasks_count": completed_tasks_count,
            "total_tasks_count": total_tasks_count,
            "completion_rate": completed_tasks_count / total_tasks_count if total_tasks_count > 0 else 0,
            "total_income": total_income,
            "members_count": members_count,
            "avg_income_per_member": total_income / members_count if members_count > 0 else 0
        })
    
    return result
