#!/bin/bash
# Brain OS 快速部署脚本
# 用法: ./scripts/deploy.sh

set -e

echo "=== Brain OS 部署脚本 ==="

# 检查环境变量
HERMES_ROOT="${HERMES_ROOT:-$HOME/.hermes}"
export HERMES_ROOT

echo "HERMES_ROOT: $HERMES_ROOT"

# 检查 Hermes CLI
if ! command -v hermes &> /dev/null; then
    echo "❌ Hermes CLI 未安装，请先安装 Hermes Agent"
    echo "   参考: https://hermes-agent.nousresearch.com/docs/installation"
    exit 1
fi

echo "✅ Hermes CLI 已安装"

# 检查技能仓库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "项目根目录: $PROJECT_ROOT"

# 检查技能
echo ""
echo "检查依赖技能..."
REQUIRED_SKILLS=(
    "chronicle-agent"
    "observer"
    "llm-wiki"
    "article-notes-integration"
    "conversation-knowledge-flywheel"
    "knowledge-flywheel-amplifier"
    "cron-git-state-monitoring"
)

for skill in "${REQUIRED_SKILLS[@]}"; do
    if hermes skills list 2>/dev/null | grep -q "$skill"; then
        echo "  ✅ $skill"
    else
        echo "  ⚠️ $skill 未找到（Hermes 内置技能，无需额外安装）"
    fi
done

# 检查 kanban-sync.py
echo ""
echo "检查 kanban-sync.py..."
if [ -f "$PROJECT_ROOT/src/kanban-sync.py" ]; then
    echo "  ✅ src/kanban-sync.py 存在"
    chmod +x "$PROJECT_ROOT/src/kanban-sync.py"
else
    echo "  ❌ src/kanban-sync.py 不存在"
    exit 1
fi

# 测试 kanban-sync.py
echo ""
echo "测试 kanban-sync.py..."
python3 "$PROJECT_ROOT/src/kanban-sync.py" --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ kanban-sync.py 运行正常"
else
    echo "  ❌ kanban-sync.py 运行失败"
    exit 1
fi

# 初始化 git 仓库（如果不存在）
GIT_REPO="$HERMES_ROOT/brain-os"
if [ ! -d "$GIT_REPO/.git" ]; then
    echo ""
    echo "📦 初始化 Git 仓库: $GIT_REPO"
    mkdir -p "$GIT_REPO"
    cp -r "$PROJECT_ROOT"/* "$GIT_REPO/"
    cd "$GIT_REPO"
    git init
    git add .
    git commit -m "Initial commit: Brain OS skills"
    echo "  ✅ Git 仓库已初始化"
fi

echo ""
echo "✅ 部署检查完成"
echo ""
echo "下一步:"
echo "  1. 编辑 config/jobs-template.json，调整任务配置"
echo "  2. 运行: hermes cron import config/jobs-template.json"
echo "  3. 运行: hermes cron list 查看任务状态"
echo "  4. 运行: hermes cron run nightly-article-integration 测试"