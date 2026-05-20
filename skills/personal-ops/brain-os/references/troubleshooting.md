# Brain OS 故障排查

## 目录结构问题

### 问题：发现中文目录

```bash
find /root/.hermes/knowledge -type d -name '*[一-龥]*'
```

**修复步骤**：
1. 梳理中文目录内容，确定归类目标
2. 按 llm-wiki Layer 1/2 架构重新整理
3. 更新所有路径引用
4. 删除空目录

### 问题：todo-backlog.md 路径不一致

**症状**：
- 消费者任务无法读取 todo
- kanban-sync.py 报错文件不存在

**修复**：
```bash
# 确认正确路径
ls -la /root/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md

# 更新 kanban-sync.py
sed -i 's/待办跟进/todo-tracking/g' /root/.hermes/scripts/kanban-sync.py

# 更新 cron 任务
# 编辑 jobs.json，将所有 "03-个人运营/03-待办跟进/" 替换为 "06-context/todo-tracking/"
```

## 数据流问题

### 问题：生产者直接输出到 Kanban

**症状**：
- todo 中没有新发现的问题
- Kanban 卡片数量异常增长
- 同一问题被多次创建卡片

**原因**：生产者任务使用了标准模式（`--output`）而非 `--write-todo` 模式。

**修复**：
1. 检查 cron 任务配置，确认使用 `--write-todo` 模式
2. 更新任务 prompt，明确要求使用 `--write-todo`
3. 考虑移除 kanban-sync.py 的标准模式，只保留 `--write-todo`、`--read-todo`、`--update-todo`

### 问题：Kanban → todo 回写失败

**症状**：
- Kanban 卡片已关闭，但 todo 中仍显示 open
- 无法追踪问题解决进度

**原因**：
1. `--update-todo` 模式未实现或未使用
2. Kanban 状态变更时未触发回写

**修复**：
```bash
# 手动回写
python /root/.hermes/scripts/kanban-sync.py \
  --task kanban-manager \
  --update-todo \
  --kanban-id <card_id> \
  --status resolved \
  --completed-date 2026-05-18

# 创建自动化任务
# 在 cron 中添加定期运行 --read-todo 的任务，同时检查 Kanban 状态变更
```

### 问题：防重复机制失效

**症状**：
- 同一问题被多次创建 Kanban 卡片
- todo 中出现重复条目

**原因**：
1. 问题摘要相似度检测阈值过高
2. 未检查 Kanban 卡片 ID
3. 不同生产者报告同一问题

**修复**：
1. 降低相似度阈值（前 30 字符匹配）
2. 增加 Kanban 卡片 ID 检查
3. 在写入 todo 前先检查是否已存在

## 路径引用问题

### 问题：脚本中的路径使用中文目录名

**症状**：
```python
# 错误
TRACKERS_DIR = os.path.join(KNOWLEDGE_PATH, "99-系统", "trackers")
TODO_PATH = os.path.join(KNOWLEDGE_PATH, "06-context", "待办跟进", "todo-backlog.md")

# 正确
TRACKERS_DIR = os.path.join(KNOWLEDGE_PATH, "99-system", "trackers")
TODO_PATH = os.path.join(KNOWLEDGE_PATH, "06-context", "todo-tracking", "todo-backlog.md")
```

**修复**：
```bash
# 全局替换
find /root/.hermes/scripts -name "*.py" -exec sed -i 's/99-系统/99-system/g' {} \;
find /root/.hermes/scripts -name "*.py" -exec sed -i 's/待办跟进/todo-tracking/g' {} \;
find /root/.hermes/cron -name "*.json" -exec sed -i 's/待办跟进/todo-tracking/g' {} \;
```

### 问题：消费者任务 prompt 中路径引用错误

**症状**：
- 每日早报无法读取 todo
- 待办提醒找不到待办列表

**修复**：
1. 打开 `/root/.hermes/cron/jobs.json`
2. 找到消费者任务（每日早报、待办提醒、晚间待办提醒、每周计划、月度总结）
3. 将 `03-个人运营/03-待办跟进/todo-backlog.md` 替换为 `06-context/todo-tracking/todo-backlog.md`

## 语法检查

### 问题：kanban-sync.py 语法错误

```bash
# 语法检查
python3 -m py_compile /root/.hermes/scripts/kanban-sync.py

# 查看帮助
python3 /root/.hermes/scripts/kanban-sync.py --help
```

### 问题：参数缺失

**症状**：
```
⚠️ --write-todo 模式需要 --output 参数
⚠️ --update-todo 模式需要 --kanban-id 参数
⚠️ --update-todo 模式需要 --status 参数
```

**修复**：确保调用时提供必需参数。

## 验证命令

### 验证目录结构

```bash
# 检查是否有中文目录
find /root/.hermes/knowledge -type d -name '*[一-龥]*'

# 检查 todo-backlog.md
ls -la /root/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md

# 检查 tracker 目录
ls -la /root/.hermes/knowledge/99-system/trackers/
```

### 验证数据流

```bash
# 测试 --write-todo
python /root/.hermes/scripts/kanban-sync.py \
  --task observer-self-check \
  --write-todo \
  --output /tmp/test-output.txt \
  --dry-run

# 测试 --read-todo
python /root/.hermes/scripts/kanban-sync.py \
  --task kanban-manager \
  --read-todo \
  --dry-run

# 测试 --update-todo
python /root/.hermes/scripts/kanban-sync.py \
  --task kanban-manager \
  --update-todo \
  --kanban-id 12345 \
  --status resolved \
  --dry-run
```

### 验证路径引用

```bash
# 检查 kanban-sync.py
grep -n "TODO_PATH\|TRACKERS_DIR" /root/.hermes/scripts/kanban-sync.py

# 检查 cron 任务
grep -r "03-个人运营\|待办跟进" /root/.hermes/cron/jobs.json

# 检查所有脚本
grep -r "99-系统\|待办跟进" /root/.hermes/scripts/
```
