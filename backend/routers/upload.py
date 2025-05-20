from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import shutil
from typing import List
import uuid
from datetime import datetime

from database import get_db
from models.user import User
from utils.auth import get_current_active_user

router = APIRouter(prefix="/upload")

# 确保上传目录存在
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传单个文件"""
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 按日期创建子目录
        today = datetime.now().strftime("%Y%m%d")
        upload_subdir = os.path.join(UPLOAD_DIR, today)
        os.makedirs(upload_subdir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_subdir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 生成可访问的URL
        file_url = f"/uploads/{today}/{unique_filename}"
        
        return {
            "filename": file.filename,
            "url": file_url,
            "size": os.path.getsize(file_path),
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )
    finally:
        file.file.close()

@router.post("/multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传多个文件"""
    result = []
    for file in files:
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 按日期创建子目录
            today = datetime.now().strftime("%Y%m%d")
            upload_subdir = os.path.join(UPLOAD_DIR, today)
            os.makedirs(upload_subdir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_subdir, unique_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 生成可访问的URL
            file_url = f"/uploads/{today}/{unique_filename}"
            
            result.append({
                "filename": file.filename,
                "url": file_url,
                "size": os.path.getsize(file_path),
                "content_type": file.content_type
            })
        except Exception as e:
            # 记录错误但继续处理其他文件
            result.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            file.file.close()
    
    return result
