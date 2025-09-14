#!/bin/bash
# -*- coding: utf-8 -*-
"""
股票分析系统启动脚本
Stock Analysis System Startup Script
"""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PYTHON_PATH="/usr/bin/python3"
PROJECT_DIR="/Volumes/Work/SynologyDrive/claude"
AGENT_SCRIPT="$PROJECT_DIR/stock_notification_agent_enhanced.py"
SCHEDULER_SCRIPT="$PROJECT_DIR/stock_scheduler_service.py"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"

# 创建必要的目录
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

echo -e "${BLUE}🚀 股票分析定时发送系统${NC}"
echo -e "${BLUE}===========================================${NC}"

# 检查Python
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo -e "${RED}❌ Python3 未找到${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3 已找到: $PYTHON_PATH${NC}"

# 检查脚本文件
if [ ! -f "$AGENT_SCRIPT" ]; then
    echo -e "${RED}❌ 主程序文件不存在: $AGENT_SCRIPT${NC}"
    exit 1
fi

if [ ! -f "$SCHEDULER_SCRIPT" ]; then
    echo -e "${RED}❌ 定时服务文件不存在: $SCHEDULER_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 程序文件检查通过${NC}"

# 功能菜单
show_menu() {
    echo ""
    echo -e "${YELLOW}请选择操作:${NC}"
    echo "1. 📧 立即发送一次分析报告"
    echo "2. ⏰ 启动定时调度器（前台运行）"
    echo "3. 🔄 启动定时服务（守护进程）"
    echo "4. 🛑 停止定时服务"
    echo "5. 📊 查看服务状态"
    echo "6. 📋 查看运行日志"
    echo "7. ⚙️  设置系统级定时任务"
    echo "8. 🗑️  清理系统级定时任务"
    echo "9. 🔧 测试系统连接"
    echo "0. 🚪 退出"
    echo -n "请输入选择 (0-9): "
}

# 立即发送报告
send_report() {
    echo -e "${YELLOW}📧 正在发送分析报告...${NC}"
    cd "$PROJECT_DIR"
    $PYTHON_PATH "$AGENT_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 报告发送成功${NC}"
    else
        echo -e "${RED}❌ 报告发送失败${NC}"
    fi
}

# 启动前台调度器
start_scheduler() {
    echo -e "${YELLOW}⏰ 启动定时调度器（前台运行）...${NC}"
    echo -e "${BLUE}按 Ctrl+C 停止程序${NC}"
    echo ""
    
    cd "$PROJECT_DIR"
    $PYTHON_PATH "$AGENT_SCRIPT"
}

# 启动守护进程
start_daemon() {
    echo -e "${YELLOW}🔄 启动定时服务（守护进程）...${NC}"
    
    cd "$PROJECT_DIR"
    nohup $PYTHON_PATH "$SCHEDULER_SCRIPT" --daemon \
        --pid-file "$PID_DIR/stock_scheduler.pid" \
        > "$LOG_DIR/scheduler.log" 2>&1 &
    
    PID=$!
    echo $PID > "$PID_DIR/stock_scheduler.pid"
    
    echo -e "${GREEN}✅ 守护进程已启动 (PID: $PID)${NC}"
    echo -e "${BLUE}日志文件: $LOG_DIR/scheduler.log${NC}"
}

# 停止服务
stop_service() {
    PID_FILE="$PID_DIR/stock_scheduler.pid"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ 服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  服务未运行${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️  PID文件不存在，服务可能未运行${NC}"
    fi
}

# 查看状态
check_status() {
    PID_FILE="$PID_DIR/stock_scheduler.pid"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 服务正在运行 (PID: $PID)${NC}"
            
            # 检查日志
            if [ -f "$LOG_DIR/scheduler.log" ]; then
                echo -e "${BLUE}📋 最近日志:${NC}"
                tail -5 "$LOG_DIR/scheduler.log"
            fi
        else
            echo -e "${RED}❌ 服务已停止（残留PID文件）${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  服务未运行${NC}"
    fi
}

# 查看日志
view_logs() {
    if [ -f "$LOG_DIR/scheduler.log" ]; then
        echo -e "${BLUE}📋 服务日志:${NC}"
        echo "-------------------------------------------"
        tail -20 "$LOG_DIR/scheduler.log"
    else
        echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
    fi
}

# 设置系统级定时任务
setup_crontab() {
    echo -e "${YELLOW}⚙️  设置系统级定时任务...${NC}"
    
    # 备份当前crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null
    
    # 创建新的定时任务
    TEMP_CRON="/tmp/stock_crontab_$$"
    
    # 导出现有任务
    crontab -l 2>/dev/null > "$TEMP_CRON"
    
    # 添加股票分析任务（如果不存在）
    if ! grep -q "stock_notification_agent_enhanced" "$TEMP_CRON" 2>/dev/null; then
        echo "" >> "$TEMP_CRON"
        echo "# 股票分析定时任务" >> "$TEMP_CRON"
        echo "0 10,16 * * * $PYTHON_PATH $AGENT_SCRIPT --auto-run" >> "$TEMP_CRON"
        echo "" >> "$TEMP_CRON"
        
        # 安装新的crontab
        crontab "$TEMP_CRON"
        rm -f "$TEMP_CRON"
        
        echo -e "${GREEN}✅ 系统级定时任务已设置${NC}"
        echo -e "${BLUE}任务将在每天 10:00 和 16:00 自动运行${NC}"
        echo -e "${YELLOW}使用 'crontab -l' 查看所有定时任务${NC}"
    else
        echo -e "${YELLOW}⚠️  定时任务已存在${NC}"
        rm -f "$TEMP_CRON"
    fi
}

# 清理定时任务
cleanup_crontab() {
    echo -e "${YELLOW}🗑️  清理系统级定时任务...${NC}"
    
    TEMP_CRON="/tmp/stock_crontab_$$"
    
    # 导出并过滤任务
    crontab -l 2>/dev/null | grep -v "stock_notification_agent_enhanced" > "$TEMP_CRON" 2>/dev/null
    
    # 安装过滤后的crontab
    crontab "$TEMP_CRON" 2>/dev/null
    rm -f "$TEMP_CRON"
    
    echo -e "${GREEN}✅ 系统级定时任务已清理${NC}"
}

# 测试连接
test_connections() {
    echo -e "${YELLOW}🔧 测试系统连接...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 测试网络
    echo -e "${BLUE}测试网络连接...${NC}"
    if curl -s --connect-timeout 10 https://www.baidu.com > /dev/null; then
        echo -e "${GREEN}✅ 网络连接正常${NC}"
    else
        echo -e "${RED}❌ 网络连接失败${NC}"
    fi
    
    # 测试Gmail
    echo -e "${BLUE}测试Gmail连接...${NC}"
    $PYTHON_PATH -c "
from stock_notification_agent_enhanced import StockNotificationAgent
agent = StockNotificationAgent()
if agent.test_gmail_connection():
    print('✅ Gmail连接正常')
else:
    print('❌ Gmail连接失败')
" 2>/dev/null
}

# 主循环
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            send_report
            ;;
        2)
            start_scheduler
            ;;
        3)
            start_daemon
            ;;
        4)
            stop_service
            ;;
        5)
            check_status
            ;;
        6)
            view_logs
            ;;
        7)
            setup_crontab
            ;;
        8)
            cleanup_crontab
            ;;
        9)
            test_connections
            ;;
        0)
            echo -e "${BLUE}👋 再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选择，请重新输入${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}按回车键继续...${NC}"
    read -r
done