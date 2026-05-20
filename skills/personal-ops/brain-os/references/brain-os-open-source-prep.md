# Brain OS 开源准备流程

## 背景

将 Brain OS 技能体系整理为可开源的独立仓库，灵感来源于 OpenClaw 的 git-backed brain 设计。

## 核心原则

1. **定位为技能体系**：不是独立系统，而是一套可组合的技能集合
2. **排除个人数据**：不包含 Paperclip、红果短剧、化工品贸易等个人项目内容
3. **简化部署**：hermes 直接读取技能目录，无需复杂配置
4. **参数化路径**：所有硬编码路径替换为环境变量

## 步骤

### 1. 清理个人数据

检查并移除以下内容：
- Paperclip 相关内容（公司项目、TradeRisk、TrendRadar）
- 红果短剧项目内容
- 化工品贸易相关内容
- 个人运营数据

```bash
# 搜索个人数据引用
grep -r "paperclip\|Paperclip\|化工\|红果\|短剧\|trade-risk\|TrendRadar" <repo-dir>
```

### 2. 参数化路径

将所有硬编码路径替换为环境变量：

```python
HERMES_ROOT = os.environ.get("HERMES_ROOT", str(Path.home() / ".hermes"))
HERMES_KNOWLEDGE = os.environ.get("HERMES_KNOWLEDGE", str(Path(HERMES_ROOT) / "knowledge"))
HERMES_TODO_PATH = os.environ.get(
    "HERMES_TODO_PATH",
    str(Path(HERMES_KNOWLEDGE) / "06-context" / "todo-tracking" / "todo-backlog.md")
)
```

### 3. 创建开源仓库结构

```
brain-os/
├── src/
│   └── kanban-sync.py          # 参数化同步工具
├── config/
│   └── jobs-template.json      # 任务配置模板
├── docs/
│   └── brain-os-architecture.md
├── scripts/
│   └── deploy.sh               # 简化部署脚本
├── README.md                   # 技能体系说明
├── LICENSE                     # MIT
├── .env.example                # 环境变量示例
└── .gitignore                  # Git 忽略规则
```

### 4. 编写 README

关键要点：
- 明确定位为"技能体系"
- 标注灵感来源（OpenClaw git-backed brain）
- 列出所有依赖技能（均为 Hermes 内置）
- 提供简化部署方式

### 5. 配置 .gitignore

排除个人数据目录：

```
# 个人数据（不公开）
knowledge/00-raw/transcripts/
knowledge/01-entities/projects/
knowledge/09-personal-ops/

# 敏感信息
.env
*.env.local
secrets.json
```

### 6. 最终验证

```bash
# 检查个人数据引用
grep -rE "paperclip|Paperclip|化工|红果|短剧|trade-risk|TrendRadar" .

# 检查仓库结构
find . -type f | head -20

# 检查文件大小
du -sh .
```

## 部署方式（简化版）

```bash
# 方式一：克隆 + 配置技能路径
git clone <repo> ~/.hermes/brain-os
hermes config set skills.paths+=~/.hermes/brain-os/skills

# 方式二：直接复制技能
cp -r ~/.hermes/brain-os/skills/* ~/.hermes/skills/

# 方式三：环境变量
export HERMES_SKILLS_PATH=~/.hermes/brain-os/skills
hermes
```

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 定位为"系统" | 未理解技能体系本质 | README 开头明确说明 |
| 包含 Paperclip 内容 | 未彻底清理 | grep 搜索并移除 |
| 部署复杂 | 过度设计 | 简化为环境变量 + 目录挂载 |
| 路径硬编码 | 未参数化 | 使用 HERMES_ROOT 等环境变量 |

## 参考

- OpenClaw: https://github.com/openclaw/openclaw
- OpenClaw git-backed brain: https://artifacthub.io/packages/helm/openclaw-with-brain/openclaw-with-brain