# config-modification-best-practices

## 核心原则

**必须**使用 `hermes config set/edit/check` 命令修改 config.yaml。

**禁止**直接用 `patch`、`write_file`、`sed` 修改 `/root/.hermes/config.yaml`。

## 命令参考

| 操作 | 命令 |
|------|------|
| 查看当前值 | `hermes config check <key>` |
| 设置值 | `hermes config set <key> '<value>'` |
| 交互式编辑 | `hermes config edit` |
| 验证配置 | `hermes config check` |
| 迁移 schema | `hermes config migrate` |

## 常见场景

### 设置 fallback_providers

```bash
# 第一步：用 hermes config set 设置
hermes config set fallback_providers '[deepseek]'

# 第二步：检查存储格式
grep fallback_providers ~/.hermes/config.yaml
# 如果显示: fallback_providers: '[deepseek]'  ← 这是字符串，格式错误！

# 第三步：手动修正为 YAML 列表格式
# fallback_providers:
#   - deepseek
```

### 设置单个值

```bash
hermes config set model.default 'deepseek-v4-flash'
hermes config set compression.threshold '0.85'
```

### 修改后重启 Gateway

```bash
hermes gateway restart
# 或 systemctl restart hermes-gateway
```

## 为什么禁止直接修改

1. `hermes config` 命令会做语法验证
2. 修改后自动触发 Gateway 热重载或提示重启
3. 有审计日志，知道谁在什么时候改了什么
4. 防止多个进程同时修改导致竞态条件

## 例外情况

**仅当 CLI 工具本身有 bug 时**（如 list 序列化问题），才允许手动修正格式。修正后应记录 bug 详情，以便未来修复 CLI 工具。

## 复盘记录

**2026-05-17**: 直接 patch config.yaml 添加 fallback_providers，违反规范。后续发现 `hermes config set` 的 list 序列化 bug（存成字符串而非 YAML 列表），需手动修正格式。
