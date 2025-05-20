from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database import get_db
from models.user import User
from models.material import Material, MaterialCategory, MaterialSupplyType
from schemas.material import MaterialCreate, MaterialUpdate, Material as MaterialSchema
from utils.auth import get_current_active_user
from utils.import_utils import process_import

# 创建日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/materials")

@router.get("/categories", response_model=List[str])
def get_material_categories():
    """获取所有材料分类"""
    return [category.value for category in MaterialCategory]

@router.get("/supply-types", response_model=List[str])
def get_material_supply_types():
    """获取所有供应类型"""
    return [supply_type.value for supply_type in MaterialSupplyType]

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
    category: Optional[str] = Query(None, description="材料分类"),
    code: Optional[str] = Query(None, description="材料编号"),
    name: Optional[str] = Query(None, description="材料名称"),
    supply_type: Optional[str] = Query(None, description="供应类型"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Material)

    # 应用筛选条件
    if category:
        query = query.filter(Material.category == category)
    if code:
        query = query.filter(Material.code.ilike(f"%{code}%"))
    if name:
        query = query.filter(Material.name.ilike(f"%{name}%"))
    if supply_type:
        query = query.filter(Material.supply_type == supply_type)
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

@router.options("/import")
async def options_import_materials():
    """处理OPTIONS预检请求"""
    logger.info("收到材料导入OPTIONS预检请求")
    return {}

@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_materials(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入材料"""
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()

        # 定义必需字段
        required_fields = ["category", "code", "name", "unit", "unit_price"]

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> Material:
            # 转换数据类型
            material_data = {
                "category": row.get("category", "通信材料"),
                "code": row.get("code", ""),
                "name": row.get("name", ""),
                "description": row.get("description", ""),
                "unit": row.get("unit", ""),
                "unit_price": float(row.get("unit_price", 0) or 0),
                "supply_type": row.get("supply_type", "甲供"),
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 检查材料编号是否已存在
            existing_material = db.query(Material).filter(Material.code == material_data["code"]).first()
            if existing_material:
                raise ValueError(f"材料编号 '{material_data['code']}' 已存在")

            # 创建材料对象
            db_material = Material(**material_data)
            db.add(db_material)

            return db_material

        # 定义验证函数
        def validate_data(rows: List[Dict[str, Any]]) -> None:
            # 检查材料编号是否唯一
            codes = [row.get("code") for row in rows if row.get("code")]
            if len(codes) != len(set(codes)):
                raise ValueError("CSV文件中存在重复的材料编号")

        # 处理导入
        imported_materials = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row,
            validate_func=validate_data
        )

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
