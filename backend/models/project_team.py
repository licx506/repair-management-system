from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ProjectTeam(Base):
    """
    维修项目与施工队伍的多对多关系表
    """
    __tablename__ = "project_teams"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    project = relationship("Project", back_populates="teams")
    team = relationship("Team", back_populates="projects")
