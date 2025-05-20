#!/bin/bash

# 工作内容测试脚本运行器

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到Python。请安装Python 3.6+${NC}"
    exit 1
fi

# 检查Python版本
python --version 2>&1 | grep -q "Python 3"
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: 可能不是Python 3。脚本需要Python 3.6+${NC}"
fi

# 显示菜单
show_menu() {
    echo -e "${GREEN}===== 工作内容测试脚本 =====${NC}"
    echo "1. 添加单个工作内容 (test_add_work_item.py)"
    echo "2. 批量添加工作内容 (batch_add_work_items.py --csv work_items.csv)"
    echo "3. 添加预定义的单个工作内容 (batch_add_work_items.py --single)"
    echo "4. 设置用户名和密码"
    echo "5. 设置API URL"
    echo "6. 查看使用说明"
    echo "0. 退出"
    echo -e "${GREEN}===========================${NC}"

    if [ ! -z "$USERNAME" ]; then
        echo -e "当前用户名: ${YELLOW}$USERNAME${NC}"
    fi

    if [ ! -z "$API_URL" ]; then
        echo -e "当前API URL: ${YELLOW}$API_URL${NC}"
    fi
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作 [0-6]: " choice

    case $choice in
        1)
            CMD="python test_add_work_item.py"
            if [ ! -z "$USERNAME" ]; then
                CMD="$CMD --username $USERNAME"
            fi
            if [ ! -z "$PASSWORD" ]; then
                CMD="$CMD --password $PASSWORD"
            fi
            echo -e "${GREEN}正在运行: $CMD${NC}"
            eval $CMD
            ;;
        2)
            CMD="python batch_add_work_items.py --csv work_items.csv --output results.csv"
            if [ ! -z "$USERNAME" ]; then
                CMD="$CMD --username $USERNAME"
            fi
            if [ ! -z "$PASSWORD" ]; then
                CMD="$CMD --password $PASSWORD"
            fi
            if [ ! -z "$API_URL" ]; then
                CMD="$CMD --api-url \"$API_URL\""
            fi
            echo -e "${GREEN}正在运行: $CMD${NC}"
            eval $CMD
            ;;
        3)
            CMD="python batch_add_work_items.py --single"
            if [ ! -z "$USERNAME" ]; then
                CMD="$CMD --username $USERNAME"
            fi
            if [ ! -z "$PASSWORD" ]; then
                CMD="$CMD --password $PASSWORD"
            fi
            if [ ! -z "$API_URL" ]; then
                CMD="$CMD --api-url \"$API_URL\""
            fi
            echo -e "${GREEN}正在运行: $CMD${NC}"
            eval $CMD
            ;;
        4)
            echo -e "${YELLOW}设置用户名和密码${NC}"
            read -p "请输入用户名: " USERNAME
            read -s -p "请输入密码: " PASSWORD
            echo
            export USERNAME
            export PASSWORD
            echo -e "${GREEN}用户名和密码已设置${NC}"
            ;;
        5)
            echo -e "${YELLOW}设置API URL${NC}"
            read -p "请输入API URL (例如 http://localhost:8000/api): " API_URL
            export API_URL
            echo -e "${GREEN}API URL已设置为: $API_URL${NC}"
            ;;
        6)
            echo -e "${GREEN}使用说明:${NC}"
            cat test_scripts_README.md
            ;;
        0)
            echo -e "${GREEN}再见!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效的选择，请重试${NC}"
            ;;
    esac

    echo
    read -p "按Enter键继续..."
    clear
done
