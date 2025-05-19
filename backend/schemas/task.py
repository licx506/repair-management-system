from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None
    team_id: Optional[int] = None

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
