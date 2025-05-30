#!/bin/bash

# 维修项目管理系统环境初始化脚本
# 此脚本用于在新环境中自动安装和配置运行环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/redhat-release ]; then
        OS="Red Hat Enterprise Linux"
        VER=$(cat /etc/redhat-release | sed 's/.*release //' | sed 's/ .*//')
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 安装包管理器工具
install_package_manager() {
    if command_exists dnf; then
        PKG_MANAGER="dnf"
        PKG_INSTALL="dnf install -y"
        PKG_UPDATE="dnf update -y"
    elif command_exists yum; then
        PKG_MANAGER="yum"
        PKG_INSTALL="yum install -y"
        PKG_UPDATE="yum update -y"
    elif command_exists apt; then
        PKG_MANAGER="apt"
        PKG_INSTALL="apt install -y"
        PKG_UPDATE="apt update && apt upgrade -y"
    elif command_exists pacman; then
        PKG_MANAGER="pacman"
        PKG_INSTALL="pacman -S --noconfirm"
        PKG_UPDATE="pacman -Syu --noconfirm"
    else
        log_error "未找到支持的包管理器"
        exit 1
    fi
    
    log_info "使用包管理器: $PKG_MANAGER"
}

# 安装Python和pip
install_python() {
    log_info "检查Python环境..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python已安装: $PYTHON_VERSION"
    else
        log_info "安装Python3..."
        if [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
            $PKG_INSTALL python3 python3-pip python3-devel
        elif [ "$PKG_MANAGER" = "apt" ]; then
            $PKG_INSTALL python3 python3-pip python3-dev
        elif [ "$PKG_MANAGER" = "pacman" ]; then
            $PKG_INSTALL python python-pip
        fi
        log_success "Python3安装完成"
    fi
    
    # 检查pip
    if ! command_exists pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
        log_info "安装pip..."
        if [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
            $PKG_INSTALL python3-pip
        elif [ "$PKG_MANAGER" = "apt" ]; then
            $PKG_INSTALL python3-pip
        fi
        log_success "pip安装完成"
    else
        log_success "pip已安装"
    fi
}

# 安装Node.js和npm
install_nodejs() {
    log_info "检查Node.js环境..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        # 检查Node.js版本是否满足要求（>=16）
        NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR_VERSION" -ge 16 ]; then
            log_success "Node.js已安装: $NODE_VERSION"
            return
        else
            log_warning "Node.js版本过低: $NODE_VERSION，需要升级到16+版本"
        fi
    fi
    
    log_info "安装Node.js 18..."
    
    if [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
        # 使用NodeSource仓库安装Node.js 18
        curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
        # 如果有旧版本，先卸载
        if command_exists node; then
            $PKG_MANAGER remove nodejs npm -y || true
        fi
        $PKG_INSTALL nodejs
    elif [ "$PKG_MANAGER" = "apt" ]; then
        # 使用NodeSource仓库安装Node.js 18
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        $PKG_INSTALL nodejs
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        $PKG_INSTALL nodejs npm
    fi
    
    # 验证安装
    if command_exists node && command_exists npm; then
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        log_success "Node.js安装完成: $NODE_VERSION"
        log_success "npm安装完成: $NPM_VERSION"
    else
        log_error "Node.js安装失败"
        exit 1
    fi
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    if [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
        $PKG_INSTALL curl wget git gcc gcc-c++ make sqlite
    elif [ "$PKG_MANAGER" = "apt" ]; then
        $PKG_INSTALL curl wget git build-essential sqlite3
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        $PKG_INSTALL curl wget git base-devel sqlite
    fi
    
    log_success "系统依赖安装完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_warning "未找到requirements.txt文件"
    fi
}

# 安装前端依赖
install_frontend_dependencies() {
    log_info "安装前端依赖..."
    
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        
        # 清理可能存在的node_modules和lock文件
        if [ -d "node_modules" ]; then
            log_info "清理旧的node_modules..."
            rm -rf node_modules package-lock.json
        fi
        
        npm install
        cd ..
        log_success "前端依赖安装完成"
    else
        log_warning "未找到frontend目录或package.json文件"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p data logs uploads
    
    log_success "目录创建完成"
}

# 初始化数据库
initialize_database() {
    log_info "初始化数据库..."
    
    # 启动后端服务进行数据库初始化
    cd backend
    python3 -c "
import sys
sys.path.append('.')
from database import init_db
init_db()
print('数据库初始化完成')
" 2>/dev/null || log_warning "数据库初始化可能失败，请手动检查"
    cd ..
    
    log_success "数据库初始化完成"
}

# 测试环境
test_environment() {
    log_info "测试环境配置..."
    
    # 测试Python环境
    if python3 -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
        log_success "Python环境测试通过"
    else
        log_error "Python环境测试失败"
        return 1
    fi
    
    # 测试Node.js环境
    if [ -d "frontend" ]; then
        cd frontend
        if npm list >/dev/null 2>&1; then
            log_success "Node.js环境测试通过"
        else
            log_warning "Node.js环境测试失败，可能需要重新安装依赖"
        fi
        cd ..
    fi
    
    log_success "环境测试完成"
}

# 显示使用说明
show_usage() {
    echo ""
    log_success "环境初始化完成！"
    echo ""
    echo "使用说明："
    echo "1. 启动系统："
    echo "   python3 run.py"
    echo ""
    echo "2. 创建管理员用户："
    echo "   python3 run.py --create-admin"
    echo ""
    echo "3. 访问系统："
    echo "   前端: http://localhost:8458"
    echo "   后端: http://localhost:8000"
    echo ""
    echo "4. 使用Docker部署（推荐生产环境）："
    echo "   bash docker-run.sh"
    echo ""
}

# 主函数
main() {
    echo "========================================"
    echo "维修项目管理系统环境初始化脚本"
    echo "========================================"
    echo ""
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        log_warning "建议使用root权限运行此脚本以安装系统依赖"
        echo "如果您没有root权限，请确保已安装Python3、Node.js等依赖"
        echo ""
    fi
    
    detect_os
    install_package_manager
    
    # 更新系统包
    log_info "更新系统包..."
    $PKG_UPDATE || log_warning "系统包更新失败，继续执行..."
    
    install_system_dependencies
    install_python
    install_nodejs
    create_directories
    install_python_dependencies
    install_frontend_dependencies
    initialize_database
    test_environment
    
    show_usage
}

# 执行主函数
main "$@"
