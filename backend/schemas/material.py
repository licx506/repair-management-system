from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.material import MaterialCategory, MaterialSupplyType

class MaterialBase(BaseModel):
    category: str = Field(default=MaterialCategory.OTHER.value, description="材料分类")
    code: str = Field(..., max_length=20, description="唯一材料编号")
    name: str = Field(..., description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    unit: str = Field(..., description="计量单位")
    unit_price: float = Field(..., gt=0, description="单价")
    supply_type: str = Field(default=MaterialSupplyType.BOTH.value, description="供应类型（甲供、自购、两者皆可）")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    category: Optional[str] = Field(None, description="材料分类")
    code: Optional[str] = Field(None, max_length=20, description="唯一材料编号")
    name: Optional[str] = Field(None, description="材料名称")
    description: Optional[str] = Field(None, description="材料描述")
    unit: Optional[str] = Field(None, description="计量单位")
    unit_price: Optional[float] = Field(None, gt=0, description="单价")
    supply_type: Optional[str] = Field(None, description="供应类型（甲供、自购、两者皆可）")
    is_active: Optional[bool] = Field(None, description="是否启用")

class Material(MaterialBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
