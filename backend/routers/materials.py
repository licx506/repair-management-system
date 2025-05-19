from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.material import Material
from schemas.material import MaterialCreate, MaterialUpdate, Material as MaterialSchema
from utils.auth import get_current_active_user

router = APIRouter(prefix="/materials")

@router.post("/", response_model=MaterialSchema)
def create_material(
    material: MaterialCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_material = Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.get("/", response_model=List[MaterialSchema])
def read_materials(
    skip: int = 0, 
    limit: int = 100, 
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Material)
    if is_active is not None:
        query = query.filter(Material.is_active == is_active)
    return query.offset(skip).limit(limit).all()

@router.get("/{material_id}", response_model=MaterialSchema)
def read_material(
    material_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if db_material is None:
        raise HTTPException(status_code=404, detail="材料不存在")
    return db_material

@router.put("/{material_id}", response_model=MaterialSchema)
def update_material(
    material_id: int, 
    material: MaterialUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if db_material is None:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    update_data = material.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_material, key, value)
    
    db.commit()
    db.refresh(db_material)
    return db_material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if db_material is None:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    # 检查是否有关联的任务材料
    if db_material.task_usages:
        # 不直接删除，而是设置为非活动状态
        db_material.is_active = False
        db.commit()
    else:
        db.delete(db_material)
        db.commit()
    
    return None
