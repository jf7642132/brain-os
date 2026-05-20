# Cron 任务路径更新模式

## 场景

当知识库目录结构重构后（如中文目录改为英文），cron 任务提示词中引用的路径需要批量更新。

## 问题模式

```
❌ 旧路径: 03-个人运营/01-每日简报/
❌ 旧路径: 04-知识库/02-工作整理/01-文章笔记
❌ 旧路径: 99-系统/
❌ 旧路径: 06-context/todo-tracking/ (部分正确，但需确认)
```

## 更新流程

### 1. 识别所有受影响的 cron 任务

```python
import json

with open('/root/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)

# 搜索 Brain OS 相关任务
for job in data['jobs']:
    if 'Brain OS' in job.get('name', ''):
        print(f"[{job['id']}] {job['name']}")
```

### 2. 定义路径映射表

```python
path_replacements = {
    '03-个人运营/01-每日简报/': '03-personal-ops/01-daily-brief/',
    '03-个人运营/02-计划日程/': '03-personal-ops/02-plans-schedules/',
    '03-个人运营/05-频道历史/': '03-personal-ops/05-channel-history/',
    '04-知识库/02-工作整理/01-文章笔记': '02-concepts/',
    '04-知识库/99-系统/03-整合报告/': '99-system/03-integrated-reports/',
    '04-知识库/01-阅读消化/04-摘要汇总/': '05-outputs/',
    '99-系统/': '99-system/',
}
```

### 3. 批量替换并验证

```python
fixed_count = 0
for job in data['jobs']:
    if 'Brain OS' in job.get('name', ''):
        old_prompt = job.get('prompt', '')
        new_prompt = old_prompt
        for old_path, new_path in path_replacements.items():
            if old_path in new_prompt:
                new_prompt = new_prompt.replace(old_path, new_path)
                fixed_count += 1
                print(f"[{job['id']}] {job['name']}: '{old_path}' → '{new_path}'")
        job['prompt'] = new_prompt

# 验证无残留
remaining = []
for job in data['jobs']:
    if 'Brain OS' in job.get('name', ''):
        for old_path in ['03-个人运营', '04-知识库', '99-系统']:
            if old_path in job.get('prompt', ''):
                remaining.append(f"[{job['id']}] 仍有 '{old_path}'")

if remaining:
    print(f"⚠️ {len(remaining)} 残留引用需手动处理")
else:
    print("✅ 所有路径引用已更新")
```

### 4. 提交变更

```bash
cd /root/.hermes/knowledge
git add -A
git commit -m "P2 修复：更新 cron 任务路径引用"
```

## 注意事项

1. **逐条验证**：替换后必须检查每个任务是否还有残留引用
2. **不要一次性替换**：分批替换，每批验证后再继续
3. **注意上下文路径**：某些任务可能引用多个路径，确保全部更新
4. **保留中文文件名**：目录改为英文，但文件名保留中文（可读性优先）
5. **更新后测试**：等待下次 cron 执行，确认任务正常运行

## 常见路径映射

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `03-个人运营/01-每日简报/` | `03-personal-ops/01-daily-brief/` | 每日简报 |
| `03-个人运营/02-计划日程/` | `03-personal-ops/02-plans-schedules/` | 计划日程 |
| `03-个人运营/04-回顾反思/` | `03-personal-ops/04-retrospectives/` | 回顾反思 |
| `03-个人运营/05-频道历史/` | `03-personal-ops/05-channel-history/` | 频道历史 |
| `04-知识库/` | `02-concepts/` 或 `05-outputs/` | 根据内容归类 |
| `99-系统/` | `99-system/` | 系统级 |
| `06-context/todo-tracking/` | `06-context/todo-tracking/` | 已正确 |

## 相关 pitfall

- **pitfall 5.3 路径引用不一致**（见 SKILL.md）
- **pitfall 5.1 中文目录陷阱**（见 SKILL.md）
