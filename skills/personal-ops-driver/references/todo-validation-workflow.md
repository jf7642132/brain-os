# 待办验证工作流

> **核心原则**: 处理待办前必须先验证问题是否仍存在。这是用户明确要求的第一优先级规则。

## 触发条件

当收到以下请求时，必须执行待办验证：
- "处理前先核验证该待办问题是否还存在"
- "确认哪些待办是真实需要修复的"
- "这些待办是否还需要执行"
- 史官/观察者提取的待办需要创建 Kanban 卡片前

## 验证步骤

### 步骤 1: 检查系统状态

验证与待办相关的系统组件是否正常运行：

```bash
# Gateway 状态
systemctl is-active hermes-gateway

# 平台连接状态
hermes status

# 钉钉鉴权状态
hermes status  # 查看 DingTalk 行
```

**判断标准**：
- 服务状态为 `active` → 可能已解决
- 平台显示 `✓ configured` → 连接正常
- 平台显示 `✗ not configured` → 可能已禁用或配置丢失

### 步骤 2: 检查文件/目录

验证待办涉及的文件或目录是否存在：

```bash
# 检查目录存在
ls -la /path/to/directory

# 检查文件存在
ls -la /path/to/file.md

# 检查文件内容
cat /path/to/file.md | head -50
```

**判断标准**：
- 目录/文件存在且有内容 → 可能仍在处理中
- 目录/文件不存在 → 可能已解决（或需重装）

### 步骤 3: 检查配置

验证待办涉及的配置项是否存在：

```bash
# 检查配置项
grep -r "keyword" /root/.hermes/

# 检查 .env 配置
cat /root/.hermes/.env | grep KEYWORD
```

**判断标准**：
- 配置存在 → 可能仍在处理中
- 配置不存在 → 可能已移除或禁用

### 步骤 4: 对比计数

对于涉及数量的待办（如"443 个文件缺失 frontmatter"），对比当前计数：

```bash
# 统计缺失 frontmatter 的文件数
grep -rL "^---" --include="*.md" /root/.hermes/knowledge/ | wc -l

# 统计断链数
grep -r "\[.*\](.*:.*:)" /root/.hermes/knowledge/ | wc -l
```

**判断标准**：
- 当前计数 = 0 → 已解决
- 当前计数 < 原始计数 → 部分解决
- 当前计数 ≈ 原始计数 → 仍存在

### 步骤 5: 分类结果

将每个待办项分类为以下状态：

| 状态 | 说明 | 后续行动 |
|------|------|----------|
| ✅ **已解决** | 问题已修复，无需处理 | 标记为 resolved，清理 |
| 🟡 **部分解决** | 有改善但未完全解决 | 需进一步验证或处理 |
| 🔴 **仍存在** | 问题仍存在 | 需要真实处理 |

## 验证结果模板

```markdown
## 待办项验证结果

| ID | 问题 | 原状态 | 当前验证 | 结论 |
|----|------|--------|----------|------|
| H001 | 443 个文件缺失 frontmatter | open | 当前 123 个缺失 | 🟡 部分解决 |
| TODO-004 | Telegram 推送错误 | 阻塞 | Telegram ✓ 正常 | ✅ 已解决 |
| TODO-011 | 钉钉鉴权失败 308 次 | 阻塞 | 已配置，需确认 | 🟡 需进一步验证 |

## 统计

- ✅ 已解决: X 项
- 🟡 部分解决/需确认: Y 项
- 🔴 问题仍存在: Z 项
```

## 常见待办类型验证模式

### 系统服务类（Gateway、定时任务等）

```bash
systemctl is-active <service-name>
hermes status
```

### 平台连接类（Telegram、钉钉、微信等）

```bash
hermes status  # 查看各平台状态
```

### 文件/目录类

```bash
ls -la /path/to/directory
find /path -name "*.md" | wc -l
```

### 配置类

```bash
grep -r "keyword" /root/.hermes/
cat /root/.hermes/.env | grep KEYWORD
```

### 数量统计类

```bash
grep -rL "^---" --include="*.md" /root/.hermes/knowledge/ | wc -l
```

## 注意事项

1. **不要盲目执行**: 史官提取的待办可能包含重复/冗余记录，部分问题可能已在项目过程中自动解决。

2. **用户确认优先**: 验证完成后，向用户呈现结果并等待确认，不要自行决定哪些需要处理。

3. **记录验证过程**: 将验证结果写入报告，便于后续追溯。

4. **Git 历史恢复**: 如果待办数据被归档/重构，使用 `git log -p` 恢复历史内容：
   ```bash
   cd /root/.hermes/knowledge
   git log --all -p -- <file-path>
   ```

5. **数据流理解**: 史官待办提取的数据流：
   - 扫描 149 个文件 → 初步提取 6106 条（含大量重复）
   - 去重后 4218 条
   - 精准模式筛选 → 71 条 → 65 条 → 21 条（最终有效）
   - 归档到 `archive/` 目录

## 参考文件

- `todo-backlog-dirty-data-patterns.md` — 脏数据模式识别
- `chronicle-agent` 技能 — 史官待办提取流程
