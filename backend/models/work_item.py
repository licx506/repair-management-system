from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class WorkItemCategory(enum.Enum):
    POWER = "通信电源"
    WIRED = "有线通信"
    WIRELESS = "无线通信"
    LINE = "通信线路"
    PIPELINE = "通信管道"

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, default=WorkItemCategory.POWER.value, index=True)  # 项目分类
    project_number = Column(String(20), unique=True, index=True)  # 项目编号
    name = Column(String(50), index=True)  # 工作项名称
    description = Column(String, nullable=True)
    unit = Column(String(20))  # 计量单位（个、米、平方米等）
    unit_price = Column(Float)  # 单价
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    task_usages = relationship("TaskWorkItem", back_populates="work_item")
