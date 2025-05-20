from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from pathlib import Path

from database import engine, Base, get_db
from models import *
from routers import auth, projects, tasks, materials, work_items, teams, statistics, users, upload, health_check

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="维修项目管理系统")

# 配置CORS
origins = [
    "http://localhost:5173",  # Vite默认端口
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8458",  # 自定义前端端口
    "http://localhost:8459",  # 备用前端端口
    "http://localhost",
    "http://xin.work.gd:8458",  # 外部访问域名
    "http://xin.work.gd:8459",  # 外部访问备用端口
    "http://xin.work.gd:8000",  # 后端服务器
    "http://xin.work.gd",      # 域名根
    "*"                        # 允许所有源（开发环境使用，生产环境应该限制）
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
    max_age=600  # 缓存预检请求结果10分钟
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
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(health_check.router, prefix="/api", tags=["健康检查"])

@app.get("/")
def read_root():
    return {"message": "欢迎使用维修项目管理系统API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

templates_dir = static_dir / "templates"
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# 挂载上传文件目录
uploads_dir = Path(__file__).parent / "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

app.mount("/templates", StaticFiles(directory=str(templates_dir)), name="templates")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
