# Cron Task Empty Response Diagnosis and Fix

## Problem

Cron tasks return `last_status: "error"` with message:
```
Agent completed but produced empty response (model error, timeout, or misconfiguration)
```

## Diagnosis

### Step 1: Check Task Prompt

```python
import json
with open('/root/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)

for task in data['jobs']:
    if task['last_status'] == 'error':
        print(f"Task: {task['name']}")
        print(f"  Prompt length: {len(task.get('prompt', ''))}")
        print(f"  Prompt preview: {task.get('prompt', '')[:500]}")
        print()
```

### Step 2: Check Output Directory

```bash
# Check if task produces output files
ls -la /root/.hermes/knowledge/03-个人运营/04-回顾反思/
# If empty, task never successfully generated output
```

### Step 3: Check Model/Provider

```bash
# Verify model is working
hermes doctor

# Check if model supports long outputs
# Some models have output token limits that cause truncation
```

## Common Causes

### 1. Prompt Too Simple

**Symptom**: Prompt < 1000 characters, no specific instructions

**Fix**: Enhance prompt with:
- Clear data sources (file paths, directories to read)
- Structured output format (sections, tables, markdown)
- Specific deliverables (file path, frontmatter, format)
- Step-by-step instructions

### 2. No Data Sources Specified

**Symptom**: Task asks to "review monthly data" but doesn't say where to find it

**Fix**: Add explicit data source paths:
```markdown
## 数据来源

1. **每日简报**: 读取 `03-个人运营/01-每日简报/` 目录下本月所有文件
2. **计划日程**: 读取 `03-个人运营/02-计划日程/` 目录下本月所有文件
3. **待办跟进**: 读取 `03-个人运营/03-待办跟进/todo-backlog.md`
```

### 3. Output Directory Doesn't Exist

**Symptom**: Task writes to a directory that doesn't exist

**Fix**: Ensure output directory exists or use `write_file` tool which creates parent directories

### 4. Model Output Truncation

**Symptom**: Task starts but response is cut off

**Fix**: 
- Reduce prompt complexity
- Request shorter outputs
- Use `max_tokens` in provider config

## Fix: Enhance Prompt

```python
import json

with open('/root/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)

for task in data['jobs']:
    if task['id'] == 'df75453a8904':  # Monthly summary
        task['prompt'] = '''作为 Brain OS 主 Agent，生成月度总结报告：

## 数据来源

1. **每日简报**: 读取 `03-个人运营/01-每日简报/` 目录下本月所有文件
2. **计划日程**: 读取 `03-个人运营/02-计划日程/` 目录下本月所有文件  
3. **待办跟进**: 读取 `03-个人运营/03-待办跟进/todo-backlog.md`
4. **频道历史**: 读取 `03-个人运营/05-频道历史/` 目录下本月所有文件
5. **知识库**: 扫描 `01-项目/` 和 `02-工作产出/` 目录下的项目进展

## 输出结构

### 1. 本月概览
- 总任务数、完成率、延期率
- 重点项目进展状态

### 2. 完成事项
- 按项目/主题分类的完成事项列表

### 3. 未完成事项
- 延期/未完成的任务列表及原因分析

### 4. 成功模式沉淀
- 本月表现最好的工作方法/流程

### 5. 失败教训
- 遇到的问题及根本原因

### 6. 下月规划
- 优先级排序的目标列表

## 交付要求

1. 写入文件: `03-个人运营/04-回顾反思/月度总结-YYYY-MM.md`
2. 文件开头添加 frontmatter
3. 使用 Markdown 格式，包含表格和列表
4. 最后输出简洁摘要（3-5 行）

工作目录: /root/.hermes/knowledge'''
        print(f"✅ Prompt enhanced: {task['name']}")
        print(f"   New length: {len(task['prompt'])} chars")

with open('/root/.hermes/cron/jobs.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## Verification

### Test the Task Manually

```bash
hermes cron run <task_id>
```

### Check Output

```bash
# Wait for task to complete, then check:
ls -la /root/.hermes/knowledge/03-个人运营/04-回顾反思/
cat /root/.hermes/knowledge/03-个人运营/04-回顾反思/月度总结-*.md | head -50
```

### Check Delivery

```bash
# Check if notification was sent
# For Telegram: check your Telegram chat
# For WeChat: check gateway logs for delivery errors
tail -50 ~/.hermes/logs/gateway.log | grep -i "send\|delivery"
```

## Prevention

### Prompt Template for Summary Tasks

```markdown
# {Task Name}

## 数据来源

{List all data sources with explicit paths}

## 输出结构

{Define sections with specific content requirements}

## 交付要求

1. 写入文件: `{output_path}`
2. 格式: Markdown with frontmatter
3. 语言: 中文
4. 长度: {specify if needed}

工作目录: {working_directory}
```

### Checklist Before Creating Cron Task

- [ ] Prompt has explicit data source paths
- [ ] Output directory exists or will be created by write_file
- [ ] Output format is specified (Markdown, JSON, etc.)
- [ ] Prompt length > 1000 characters for complex tasks
- [ ] Model supports required output length
- [ ] Delivery channel is configured correctly

## Related

- `references/cron-delivery-channel-switch.md` - Switching delivery channels
- `hermes cron` CLI reference in SKILL.md