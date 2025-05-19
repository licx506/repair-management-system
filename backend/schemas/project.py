from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    contact_name: str
    contact_phone: str
    priority: int = 1

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class Project(ProjectBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        orm_mode = True

class ProjectDetail(Project):
    tasks_count: int
    completed_tasks_count: int
    
    class Config:
        orm_mode = True
