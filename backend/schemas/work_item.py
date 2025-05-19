from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from models.work_item import WorkItemCategory

class WorkItemBase(BaseModel):
    category: str = Field(default=WorkItemCategory.POWER.value, description="项目分类")
    project_number: str = Field(..., max_length=20, description="唯一项目编号")
    name: str = Field(..., max_length=50, description="工作项名称")
    description: Optional[str] = Field(None, description="工作项描述")
    unit: str = Field(..., max_length=20, description="计量单位")
    unit_price: float = Field(..., gt=0, description="单价")

class WorkItemCreate(WorkItemBase):
    pass

class WorkItemUpdate(BaseModel):
    category: Optional[str] = Field(None, description="项目分类")
    project_number: Optional[str] = Field(None, max_length=20, description="唯一项目编号")
    name: Optional[str] = Field(None, max_length=50, description="工作项名称")
    description: Optional[str] = Field(None, description="工作项描述")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    unit_price: Optional[float] = Field(None, gt=0, description="单价")
    is_active: Optional[bool] = Field(None, description="是否启用")

class WorkItem(WorkItemBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
