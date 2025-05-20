from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from passlib.context import CryptContext
import logging

from database import get_db
from models.user import User, UserRole
from schemas.user import User as UserSchema, UserUpdate
from utils.auth import get_current_active_user, get_current_user
from utils.import_utils import process_import

# 创建日志记录器
logger = logging.getLogger(__name__)

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users")

@router.get("/", response_model=List[UserSchema])
def get_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户列表，可以按角色和状态筛选
    只有管理员可以访问
    """
    # 检查权限
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    # 查询用户
    query = db.query(User)

    # 应用筛选条件
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.all()
    return users

@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定用户的详细信息
    只有管理员或用户本人可以访问
    """
    # 检查权限
    if current_user.role != UserRole.ADMIN.value and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户信息
    只有管理员或用户本人可以更新
    只有管理员可以更改角色和状态
    """
    # 检查权限
    if current_user.role != UserRole.ADMIN.value and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 非管理员不能修改角色和状态
    if current_user.role != UserRole.ADMIN.value:
        if user_update.role is not None or user_update.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限修改角色或状态"
            )

    # 更新用户信息
    if user_update.email is not None:
        # 检查邮箱是否已被其他用户使用
        existing_user = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
        user.email = user_update.email

    if user_update.full_name is not None:
        user.full_name = user_update.full_name

    if user_update.phone is not None:
        user.phone = user_update.phone

    if user_update.role is not None and current_user.role == UserRole.ADMIN.value:
        user.role = user_update.role

    if user_update.is_active is not None and current_user.role == UserRole.ADMIN.value:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户
    只有管理员可以删除用户
    """
    # 检查权限
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )

    db.delete(user)
    db.commit()
    return None

@router.options("/import")
async def options_import_users():
    """处理OPTIONS预检请求"""
    logger.info("收到用户导入OPTIONS预检请求")
    return {}

@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_users(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入用户"""
    # 检查权限
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持CSV文件格式"
        )

    try:
        # 读取文件内容
        file_content = file.file.read()

        # 定义必需字段
        required_fields = ["username", "password", "email", "role"]

        # 定义处理每一行数据的函数
        def process_row(row: Dict[str, Any]) -> User:
            # 检查用户名是否已存在
            username = row.get("username", "").strip()
            if not username:
                raise ValueError("用户名不能为空")

            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                raise ValueError(f"用户名 '{username}' 已存在")

            # 检查邮箱是否已存在
            email = row.get("email", "").strip()
            if not email:
                raise ValueError("邮箱不能为空")

            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                raise ValueError(f"邮箱 '{email}' 已被使用")

            # 检查角色是否有效
            role = row.get("role", "").strip()
            valid_roles = [r.value for r in UserRole]
            if role not in valid_roles:
                raise ValueError(f"角色 '{role}' 无效，有效角色为: {', '.join(valid_roles)}")

            # 哈希密码
            password = row.get("password", "").strip()
            if not password:
                raise ValueError("密码不能为空")

            hashed_password = pwd_context.hash(password)

            # 创建用户对象
            user_data = {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "role": role,
                "full_name": row.get("full_name", ""),
                "phone": row.get("phone", ""),
                "is_active": True,
                "created_at": datetime.now()
            }

            db_user = User(**user_data)
            db.add(db_user)

            return db_user

        # 定义验证函数
        def validate_data(rows: List[Dict[str, Any]]) -> None:
            # 检查用户名是否唯一
            usernames = [row.get("username", "").strip() for row in rows if row.get("username")]
            if len(usernames) != len(set(usernames)):
                raise ValueError("CSV文件中存在重复的用户名")

            # 检查邮箱是否唯一
            emails = [row.get("email", "").strip() for row in rows if row.get("email")]
            if len(emails) != len(set(emails)):
                raise ValueError("CSV文件中存在重复的邮箱")

        # 处理导入
        imported_users = process_import(
            file_content=file_content,
            required_fields=required_fields,
            process_row_func=process_row,
            validate_func=validate_data
        )

        # 提交事务
        db.commit()

        return {"message": f"成功导入 {len(imported_users)} 个用户"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        print(f"导入用户失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入用户失败: {str(e)}"
        )
    finally:
        file.file.close()
