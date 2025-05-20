from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    project_id: Optional[int] = None
    title: str  # 工单主题
    description: Optional[str] = None  # 工单内容
    attachment: Optional[str] = None  # 派单附件
    work_list: Optional[str] = None  # 工作量清单
    company_material_list: Optional[str] = None  # 甲供材清单
    self_material_list: Optional[str] = None  # 自购料清单
    labor_cost: float = 0.0  # 施工费
    material_cost: float = 0.0  # 材料费
    company_material_cost: float = 0.0  # 甲供材料费
    self_material_cost: float = 0.0  # 自购材料费

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    project_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    attachment: Optional[str] = None
    work_list: Optional[str] = None
    company_material_list: Optional[str] = None
    self_material_list: Optional[str] = None
    labor_cost: Optional[float] = None
    material_cost: Optional[float] = None
    company_material_cost: Optional[float] = None
    self_material_cost: Optional[float] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None
    team_id: Optional[int] = None
    work_items: Optional[str] = None  # JSON字符串，包含工作内容列表
    materials: Optional[str] = None  # JSON字符串，包含材料列表

class TaskMaterialBase(BaseModel):
    material_id: int
    quantity: float
    is_company_provided: bool = False

class TaskMaterialCreate(TaskMaterialBase):
    pass

class TaskMaterial(TaskMaterialBase):
    id: int
    task_id: int
    unit_price: float
    total_price: float

    class Config:
        orm_mode = True

class TaskWorkItemBase(BaseModel):
    work_item_id: int
    quantity: float

class TaskWorkItemCreate(TaskWorkItemBase):
    pass

class TaskWorkItem(TaskWorkItemBase):
    id: int
    task_id: int
    unit_price: float
    total_price: float

    class Config:
        orm_mode = True

class Task(TaskBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by_id: int
    assigned_to_id: Optional[int] = None
    team_id: Optional[int] = None
    total_cost: float

    class Config:
        orm_mode = True

class TaskDetail(Task):
    materials: List[TaskMaterial] = []
    work_items: List[TaskWorkItem] = []

    class Config:
        orm_mode = True

class TaskComplete(BaseModel):
    materials: List[TaskMaterialCreate] = []
    work_items: List[TaskWorkItemCreate] = []
