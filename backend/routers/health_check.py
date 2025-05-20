from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from utils.auth import get_current_active_user

router = APIRouter(prefix="/health-check")

@router.get("/")
def health_check():
    """
    健康检查端点，用于测试API服务器是否正常运行
    不需要认证即可访问
    """
    return {
        "status": "ok",
        "message": "API服务器运行正常"
    }

@router.get("/auth")
def auth_health_check(current_user: User = Depends(get_current_active_user)):
    """
    需要认证的健康检查端点，用于测试认证是否正常
    """
    return {
        "status": "ok",
        "message": "认证正常",
        "user_id": current_user.id,
        "username": current_user.username
    }

@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    """
    数据库健康检查端点，用于测试数据库连接是否正常
    """
    try:
        # 执行一个简单的查询
        db.execute("SELECT 1").fetchall()
        return {
            "status": "ok",
            "message": "数据库连接正常"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库连接异常: {str(e)}"
        )
