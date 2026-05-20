# Brain OS 目录结构规范

> 基于 llm-wiki 技能扩展，2026-05-19 更新

---

## 编号体系

Brain OS 采用编号前缀体系，确保目录结构清晰、可扩展、无冲突。

### 标准编号方案

| 编号 | 目录 | 层级 | 用途 |
|------|------|------|------|
| `00` | `raw/` | Layer 1 | 原始来源（不可变） |
| `01` | `entities/` | Layer 2 | 实体/项目页面 |
| `02` | `concepts/` | Layer 2 | 概念/主题页面 |
| `03` | `comparisons/` | Layer 2 | 对比分析 |
| `04` | `queries/` | Layer 2 | 查询/模板 |
| `05` | `outputs/` | 扩展 | 工作产出 |
| `06` | `context/` | 扩展 | 上下文（决策、模式、教训） |
| `07` | `config/` | 扩展 | 配置 |
| `08` | `archive/` | 扩展 | 归档 |
| `09` | `personal-ops/` | 扩展 | 个人运营 |
| `99` | `system/` | 系统 | 系统运营（基础设施） |

### 根级文件（无编号）

以下文件位于知识库根目录，不属于任何编号子目录：

| 文件 | 用途 |
|------|------|
| `SCHEMA.md` | 知识库规范（目录/命名/frontmatter） |
| `index.md` | 内容索引（所有页面的目录） |
| `log.md` | 操作日志（append-only） |

---

## 命名规范

### 目录名

- **语言**: 英文（符合 llm-wiki 规范）
- **格式**: 小写，连字符分隔（kebab-case）
- **示例**: `01-entities/`, `06-context/`, `99-system/`

### 文件名

- **语言**: 中文（用户可读性优先）
- **格式**: 描述性名称，可含日期
- **示例**: `2026-05-19.md`, `化工产业链知识图谱.md`

### 子目录名

- **语言**: 英文（避免嵌套中文）
- **格式**: 小写，连字符分隔
- **示例**: `09-personal-ops/01-daily-brief/`

---

## 冲突检查

### 编号冲突

创建新目录前必须检查编号唯一性：

```bash
# 检查编号冲突
cd /root/.hermes/knowledge
for d in */; do
  num=$(echo "$d" | grep -oE '^[0-9]{2}')
  if [ -n "$num" ]; then
    count=$(ls -d ${num}-*/ 2>/dev/null | wc -l)
    if [ "$count" -gt 1 ]; then
      echo "❌ 编号 $num 冲突: $(ls -d ${num}-*/)"
    fi
  fi
done
```

### 路径引用同步

修改目录结构后，必须同步更新以下文件：

| 文件 | 更新内容 |
|------|----------|
| `cron/jobs.json` | 所有 cron 任务 prompt 中的路径引用 |
| `SCHEMA.md` | 目录结构说明 |
| `index.md` | 内容索引中的路径 |
| `scripts/kanban-sync.py` | TASK_CONFIG 中的任务配置 |

---

## 示例结构

```
knowledge/
├── SCHEMA.md                    # 根级：知识库规范
├── index.md                     # 根级：内容索引
├── log.md                       # 根级：操作日志
│
├── 00-raw/                      # Layer 1: 原始来源
│   ├── articles/
│   ├── transcripts/
│   └── assets/
│
├── 01-entities/                 # Layer 2: 实体
│   └── projects/
│
├── 02-concepts/                 # Layer 2: 概念
│
├── 03-comparisons/              # Layer 2: 对比
│
├── 04-queries/                  # Layer 2: 查询
│
├── 05-outputs/                  # 扩展：工作产出
│   └── work-reports/
│
├── 06-context/                  # 扩展：上下文
│   ├── todo-tracking/
│   ├── decisions/
│   └── patterns/
│
├── 07-config/                   # 扩展：配置
│
├── 08-archive/                  # 扩展：归档
│
├── 09-personal-ops/             # 扩展：个人运营
│   ├── 01-daily-brief/
│   └── 05-channel-history/
│
└── 99-system/                   # 系统：基础设施
    ├── BRAIN-OS-ARCHITECTURE.md
    ├── kanban/
    ├── lint-reports/
    └── trackers/
```

---

## 变更历史

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-05-18 | 初始创建 | 知识库结构重构 |
| 2026-05-19 | `03-personal-ops` → `06-personal-ops` | 避免与 `03-comparisons` 冲突 |
| 2026-05-19 | `05-system-config` → `09-system-config` | 避免与 `05-outputs` 冲突 |
| 2026-05-19 | `06-personal-ops` → `09-personal-ops` | 编号连续化 |
| 2026-05-19 | `09-system-config` 删除 | SCHEMA.md/log.md 应移至根级 |
| 2026-05-19 | `99-系统` → `99-system` | 统一英文目录名 |
