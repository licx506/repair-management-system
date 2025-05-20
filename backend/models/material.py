from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class MaterialCategory(enum.Enum):
    CABLE = "电缆类"
    PIPE = "管道类"
    DEVICE = "设备类"
    TOOL = "工具类"
    OTHER = "其他"

class MaterialSupplyType(enum.Enum):
    COMPANY = "甲供"
    SELF = "自购"
    BOTH = "两者皆可"

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, default=MaterialCategory.OTHER.value, index=True)  # 材料分类
    code = Column(String(20), unique=True, index=True)  # 材料编号
    name = Column(String, index=True)  # 材料名称
    description = Column(String, nullable=True)  # 材料描述
    unit = Column(String)  # 单位（个、米、平方米等）
    unit_price = Column(Float)  # 单价
    supply_type = Column(String, default=MaterialSupplyType.BOTH.value)  # 供应类型（甲供、自购、两者皆可）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    task_usages = relationship("TaskMaterial", back_populates="material")
