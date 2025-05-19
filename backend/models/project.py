from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class ProjectStatus(enum.Enum):
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    location = Column(String)
    contact_name = Column(String)
    contact_phone = Column(String)
    status = Column(String, default=ProjectStatus.PENDING.value)
    priority = Column(Integer, default=1)  # 1-5，5为最高优先级
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # 关系
    created_by = relationship("User", back_populates="created_projects")
    tasks = relationship("Task", back_populates="project")
    teams = relationship("ProjectTeam", back_populates="project")
