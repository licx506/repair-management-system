from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"  # 管理员
    WORKER = "worker"  # 施工人员
    MANAGER = "manager"  # 项目经理

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone = Column(String)
    role = Column(String, default=UserRole.WORKER.value)
    is_active = Column(Boolean, default=True)

    # 关系
    team_memberships = relationship("TeamMember", back_populates="user")
    assigned_tasks = relationship("Task", back_populates="assigned_to", foreign_keys="Task.assigned_to_id")
    created_tasks = relationship("Task", back_populates="created_by", foreign_keys="Task.created_by_id")
    created_projects = relationship("Project", back_populates="created_by")
    tasks = relationship("TaskWorker", back_populates="user")
