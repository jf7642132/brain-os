#!/bin/bash
# Brain OS 任务自动归档脚本
# 检查周计划中的任务状态，自动归档已完成的任务

set -e

WIKI_DIR="/root/wiki"
TODO_BACKLOG="$WIKI_DIR/01-个人运营/03-待办跟进/todo-backlog.md"
WEEK_PLAN_DIR="$WIKI_DIR/01-个人运营/02-计划日程"
LOG_FILE="$WIKI_DIR/01-个人运营/05-运营日志/任务归档.log"

# 获取当前日期
CURRENT_DATE=$(date +%Y-%m-%d)

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始执行任务自动归档..."

# 检查 todo-backlog.md 是否有高优先级任务
HIGH_PRIORITY=$(grep -A 10 "## 高优先级" "$TODO_BACKLOG" | grep -v "##" | grep -v "（空）" | grep -v "^---$" | wc -l)

if [ "$HIGH_PRIORITY" -eq 0 ]; then
    log "✅ 无高优先级待办，跳过归档"
    exit 0
fi

# 提取高优先级任务
TASKS=$(grep -A 20 "## 高优先级" "$TODO_BACKLOG" | grep -v "##" | grep -v "（空）" | grep -v "^---$" | grep "\[x\]" | head -5)

if [ -z "$TASKS" ]; then
    log "✅ 无已完成任务，跳过归档"
    exit 0
fi

# 将已完成任务移动到已完成部分
echo "" >> "$TODO_BACKLOG"
echo "## 已完成/已归档" >> "$TODO_BACKLOG"
echo "$TASKS" | grep "\[x\]" >> "$TODO_BACKLOG"

log "✅ 已完成任务已归档到 todo-backlog.md"
log "归档完成"
