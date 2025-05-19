from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class TaskWorker(Base):
    """
    工单与施工人员的多对多关系表
    """
    __tablename__ = "task_workers"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_primary = Column(Boolean, default=False)  # 是否为主要负责人
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    task = relationship("Task", back_populates="workers")
    user = relationship("User", back_populates="tasks")
