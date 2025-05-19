from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None
    unit: str
    unit_price: float

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    is_active: Optional[bool] = None

class Material(MaterialBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
