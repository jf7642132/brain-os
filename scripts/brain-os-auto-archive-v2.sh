#!/bin/bash
# Brain OS 任务自动归档脚本 v2
# 检查周计划和 todo-backlog，自动归档已完成的任务

set -e

WIKI_DIR="${HERMES_KNOWLEDGE:-$HOME/.hermes/knowledge}"
TODO_BACKLOG="$WIKI_DIR/01-个人运营/03-待办跟进/todo-backlog.md"
LOG_FILE="$WIKI_DIR/01-个人运营/05-运营日志/任务归档.log"

# 获取当前日期
CURRENT_DATE=$(date +%Y-%m-%d)

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "开始执行任务自动归档..."
log "当前日期：$CURRENT_DATE"
log "=========================================="

# 检查 todo-backlog.md 是否存在
if [ ! -f "$TODO_BACKLOG" ]; then
    log "❌ todo-backlog.md 不存在"
    exit 1
fi

# 检查高优先级是否有已完成任务
HIGH_COMPLETED=$(grep -A 10 "## 高优先级" "$TODO_BACKLOG" | grep "\[x\]" | wc -l)

if [ "$HIGH_COMPLETED" -eq 0 ]; then
    log "✅ 无已完成的高优先级任务"
    log "任务归档完成"
    exit 0
fi

log "发现 $HIGH_COMPLETED 个已完成的高优先级任务"

# 提取已完成任务
COMPLETED_TASKS=$(grep -A 10 "## 高优先级" "$TODO_BACKLOG" | grep "\[x\]")

# 将已完成任务移动到已完成部分
# 先删除已完成任务
for task in $COMPLETED_TASKS; do
    sed -i "/$task/d" "$TODO_BACKLOG"
done

# 添加到已完成部分
echo "" >> "$TODO_BACKLOG"
echo "## 已完成/已归档" >> "$TODO_BACKLOG"
echo "$COMPLETED_TASKS" | while read -r line; do
    if [ -n "$line" ]; then
        echo "$line" >> "$TODO_BACKLOG"
    fi
done

log "✅ 已完成任务已归档"
log "=========================================="
log "任务归档完成"
log "=========================================="
