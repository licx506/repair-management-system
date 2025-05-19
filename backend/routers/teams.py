from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.team import Team, TeamMember
from schemas.team import (
    TeamCreate, TeamUpdate, Team as TeamSchema, 
    TeamDetail, TeamMemberCreate
)
from utils.auth import get_current_active_user

router = APIRouter(prefix="/teams")

@router.post("/", response_model=TeamSchema)
def create_team(
    team: TeamCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # 创建团队时，将创建者添加为团队领导
    db_team_member = TeamMember(
        team_id=db_team.id,
        user_id=current_user.id,
        is_leader=True
    )
    db.add(db_team_member)
    db.commit()
    
    return db_team

@router.get("/", response_model=List[TeamSchema])
def read_teams(
    skip: int = 0, 
    limit: int = 100, 
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Team)
    if is_active is not None:
        query = query.filter(Team.is_active == is_active)
    return query.offset(skip).limit(limit).all()

@router.get("/{team_id}", response_model=TeamDetail)
def read_team(
    team_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    return db_team

@router.put("/{team_id}", response_model=TeamSchema)
def update_team(
    team_id: int, 
    team: TeamUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查当前用户是否是团队领导
    is_leader = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.is_leader == True
    ).first() is not None
    
    if not is_leader and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有团队领导或管理员可以更新团队信息")
    
    update_data = team.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_team, key, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team

@router.post("/{team_id}/members", response_model=TeamDetail)
def add_team_member(
    team_id: int, 
    member: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查当前用户是否是团队领导
    is_leader = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.is_leader == True
    ).first() is not None
    
    if not is_leader and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有团队领导或管理员可以添加团队成员")
    
    # 检查用户是否存在
    db_user = db.query(User).filter(User.id == member.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户是否已经是团队成员
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == member.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="用户已经是团队成员")
    
    db_team_member = TeamMember(
        team_id=team_id,
        user_id=member.user_id,
        is_leader=member.is_leader
    )
    db.add(db_team_member)
    db.commit()
    db.refresh(db_team)
    
    return db_team

@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: int, 
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查当前用户是否是团队领导
    is_leader = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.is_leader == True
    ).first() is not None
    
    if not is_leader and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有团队领导或管理员可以移除团队成员")
    
    # 检查要移除的成员是否存在
    db_team_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if db_team_member is None:
        raise HTTPException(status_code=404, detail="团队成员不存在")
    
    # 不允许移除自己（如果是领导）
    if user_id == current_user.id and db_team_member.is_leader:
        raise HTTPException(status_code=400, detail="团队领导不能移除自己")
    
    db.delete(db_team_member)
    db.commit()
    
    return None

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    
    # 检查当前用户是否是团队领导
    is_leader = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.is_leader == True
    ).first() is not None
    
    if not is_leader and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有团队领导或管理员可以删除团队")
    
    # 检查是否有关联的任务
    if db_team.tasks:
        # 不直接删除，而是设置为非活动状态
        db_team.is_active = False
        db.commit()
    else:
        # 删除所有团队成员
        db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
        # 删除团队
        db.delete(db_team)
        db.commit()
    
    return None
