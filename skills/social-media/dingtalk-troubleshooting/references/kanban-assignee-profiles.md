# Kanban Assignee 配置规范

## 问题描述

在 kanban 看板中选择负责人时，出现了员工姓名（如"赵九峰"），但实际应该使用 profile 名称。

## 根本原因

`kanban_db.known_assignees()` 函数返回两个来源的 assignee：

```python
def known_assignees(conn):
    on_disk = set(list_profiles_on_disk())  # profiles on disk: default, dingtalk-worker
    counts = conn.execute("SELECT assignee, status, COUNT(*) FROM tasks ...")
    names = sorted(on_disk | set(counts.keys()))  # 合并 profiles + 任务中的 assignee
    return [{"name": name, "on_disk": name in on_disk, ...} for name in names]
```

**问题**：
1. `employee_mapping.yaml` 包含员工姓名（"赵九峰"、"员工A" 等）
2. 任务被分配给员工姓名（而非 profile）
3. `known_assignees()` 返回所有曾作为 assignee 的名字

## 正确做法

### Assignee 应该使用 profile，而不是员工姓名

| 场景 | 推荐 assignee | 说明 |
|------|---------------|------|
| AI 执行任务 | `dingtalk-worker` | 独立 AI 实例 |
| 人工执行任务 | `default` | 默认 profile |
| 特定员工 | 创建专门 profile | 如 `employee-a` |

### 员工姓名仅用于 `employee_mapping.yaml` 映射

```yaml
# employee_mapping.yaml
赵九峰:
  user_id: "$:LWCP_v1:$VqWUaB7Bw9Guqgnj1pPqOw=="
  chat_id: "cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M="

员工A:
  user_id: ""  # 待捕获
  chat_id: "cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M="
```

**注意**：`employee_mapping.yaml` 中的员工姓名**不用于** kanban assignee，仅用于：
- DingTalk 消息推送时的 User ID 映射
- 任务描述中的人名引用

## 修复步骤

### 1. 将任务的 assignee 改回 profile

```bash
# 查看当前 assignee
hermes kanban list --json | grep -B 5 '"assignee": "赵九峰"'

# 修改 assignee
hermes kanban assign <task-id> default
hermes kanban assign <task-id> dingtalk-worker
```

### 2. 验证修复

```bash
hermes kanban assignees
```

**修复前**：
```
NAME                  ON DISK   COUNTS
default               yes       done=13
dingtalk-worker       yes       done=5
赵九峰                   no        done=2    ← 问题
```

**修复后**：
```
NAME                  ON DISK   COUNTS
default               yes       done=15
dingtalk-worker       yes       done=5
```

### 3. 如需按员工分配任务

**创建专门 profile**：
```bash
hermes profile create employee-a --clone
```

**修改 employee_mapping.yaml**：
```yaml
员工A:
  user_id: "<captured-user-id>"
  profile: "employee-a"  # 关联到 profile
```

**任务分配**：
```bash
hermes kanban create "任务标题" --assignee employee-a
```

## 常见 Pitfalls

| Pitfall | 说明 | 解决 |
|---------|------|------|
| 直接用员工姓名作为 assignee | `known_assignees()` 会返回该名字 | 使用 profile 名称 |
| `employee_mapping.yaml` 中的姓名被误用 | 仅用于 User ID 映射，不用于 assignee | 明确区分 |
| 任务被错误重新分配 | 手动修改或 AI 错误分配 | 使用 `hermes kanban assign` 修正 |

## 配置检查清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| 当前 assignees | `hermes kanban assignees` | 只有 profile 名称 |
| 任务 assignee | `hermes kanban list --json \| grep assignee` | 都是 profile |
| employee_mapping.yaml | `cat employee_mapping.yaml` | 员工姓名映射到 User ID |

## 调试命令

```bash
# 查看所有任务的 assignee
hermes kanban list --json | jq '.[].assignee' | sort | uniq -c

# 查看特定任务的分配历史
hermes kanban show <task-id>

# 检查 employee_mapping.yaml
cat /root/.hermes/profiles/dingtalk-worker/employee_mapping.yaml
```