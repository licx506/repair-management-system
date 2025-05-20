from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class TaskStatus(enum.Enum):
    PENDING = "pending"  # 待接单
    ASSIGNED = "assigned"  # 已接单
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String, index=True)  # 工单主题
    description = Column(String, nullable=True)  # 工单内容
    attachment = Column(String, nullable=True)  # 派单附件
    work_list = Column(String, nullable=True)  # 工作量清单
    company_material_list = Column(String, nullable=True)  # 甲供材清单
    self_material_list = Column(String, nullable=True)  # 自购料清单
    labor_cost = Column(Float, default=0.0)  # 施工费
    material_cost = Column(Float, default=0.0)  # 材料费
    company_material_cost = Column(Float, default=0.0)  # 甲供材料费
    self_material_cost = Column(Float, default=0.0)  # 自购材料费
    status = Column(String, default=TaskStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    total_cost = Column(Float, default=0.0)  # 总费用

    # 关系
    project = relationship("Project", back_populates="tasks")
    created_by = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    assigned_to = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])
    team = relationship("Team", back_populates="tasks")
    materials = relationship("TaskMaterial", back_populates="task")
    work_items = relationship("TaskWorkItem", back_populates="task")
    workers = relationship("TaskWorker", back_populates="task")

class TaskMaterial(Base):
    __tablename__ = "task_materials"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Float)
    is_company_provided = Column(Boolean, default=False)  # 是否甲供
    unit_price = Column(Float)  # 单价
    total_price = Column(Float)  # 总价

    # 关系
    task = relationship("Task", back_populates="materials")
    material = relationship("Material", back_populates="task_usages")

class TaskWorkItem(Base):
    __tablename__ = "task_work_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    quantity = Column(Float)
    unit_price = Column(Float)  # 单价
    total_price = Column(Float)  # 总价

    # 关系
    task = relationship("Task", back_populates="work_items")
    work_item = relationship("WorkItem", back_populates="task_usages")
