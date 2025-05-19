from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import *
from routers import auth, projects, tasks, materials, work_items, teams, statistics, users

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="维修项目管理系统")

# 配置CORS
origins = [
    "http://localhost:5173",  # Vite默认端口
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8458",  # 自定义前端端口
    "http://localhost",
    "http://xin.work.gd:8458",  # 外部访问域名
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(projects.router, prefix="/api", tags=["维修项目"])
app.include_router(tasks.router, prefix="/api", tags=["工单"])
app.include_router(materials.router, prefix="/api", tags=["材料"])
app.include_router(work_items.router, prefix="/api", tags=["工作内容"])
app.include_router(teams.router, prefix="/api", tags=["施工队伍"])
app.include_router(statistics.router, prefix="/api", tags=["统计"])
app.include_router(users.router, prefix="/api", tags=["用户管理"])

@app.get("/")
def read_root():
    return {"message": "欢迎使用维修项目管理系统API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
