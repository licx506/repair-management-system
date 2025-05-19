from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.user import User

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class TeamMemberBase(BaseModel):
    user_id: int
    is_leader: bool = False

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id: int
    team_id: int
    joined_at: datetime
    
    class Config:
        orm_mode = True

class TeamMemberWithUser(TeamMember):
    user: User
    
    class Config:
        orm_mode = True

class Team(TeamBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True

class TeamDetail(Team):
    members: List[TeamMemberWithUser] = []
    
    class Config:
        orm_mode = True
