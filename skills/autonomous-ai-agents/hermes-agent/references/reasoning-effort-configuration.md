# reasoning_effort 配置架构详解

## 问题背景

用户反馈 Web UI 推理内容关不掉，经常出现重复思考、全英文思考、思考内容冗长等问题。

## 根本原因

`config.yaml` 中只有 `delegation.reasoning_effort: "none"`，但 Gateway 读取的是 `agent.reasoning_effort`。

## 作用域区分

| 配置项 | 位置 | 作用范围 |
|--------|------|----------|
| `agent.reasoning_effort` | `agent:` | **所有平台的主对话**（CLI + Web UI + Telegram + Discord + 所有 Gateway 平台） |
| `delegation.reasoning_effort` | `delegation:` | **仅子 Agent**（`delegate_task` 创建的子 agent） |

## Gateway 读取机制

```python
# gateway/run.py
def _load_reasoning_config() -> dict | None:
    """Load reasoning effort from config.yaml."""
    effort = str(cfg_get(cfg, "agent", "reasoning_effort", default="") or "").strip()
    result = parse_reasoning_effort(effort)
    ...
    return {"effort": result}  # or None if not set
```

Gateway 的 `_load_reasoning_config()` **只读取 `agent.reasoning_effort`**，不读取 `delegation.reasoning_effort`。

## 生效机制

```
Gateway 启动 → _load_reasoning_config() 读取 agent.reasoning_effort
    ↓
AIAgent(reasoning_config={"effort": "none"})
    ↓
custom provider build_api_kwargs_extras()
    ↓
extra_body["think"] = False  ← 发送给商汤 API
    ↓
商汤 API 关闭推理 → Web UI 不再显示推理内容
```

## 代码路径

| 文件 | 作用 |
|------|------|
| `gateway/run.py` | `_load_reasoning_config()` 读取 `agent.reasoning_effort` |
| `agent/transports/chat_completions.py` | 根据 `reasoning_config` 构建 API 参数 |
| `plugins/model-providers/custom/__init__.py` | custom provider 的 `build_api_kwargs_extras()` 发送 `extra_body["think"] = False` |

### custom provider 关键代码

```python
# plugins/model-providers/custom/__init__.py
def build_api_kwargs_extras(
    self,
    *,
    reasoning_config: dict | None = None,
    **ctx: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    extra_body: dict[str, Any] = {}

    # Disable thinking when reasoning is turned off
    if reasoning_config and isinstance(reasoning_config, dict):
        _effort = (reasoning_config.get("effort") or "").strip().lower()
        _enabled = reasoning_config.get("enabled", True)
        if _effort == "none" or _enabled is False:
            extra_body["think"] = False

    return extra_body, {}
```

**关键点**：只有当 `reasoning_config` 存在且 `effort == "none"` 或 `enabled == False` 时，才会发送 `extra_body["think"] = False`。

如果 `agent.reasoning_effort` 不存在，`reasoning_config` 为 `None`，这个条件不满足，推理不会被禁用。

## 有效值

| 值 | 含义 |
|----|------|
| `none` | 完全关闭推理 |
| `minimal` | 最小推理 |
| `low` | 低推理 |
| `medium` | 中等推理（默认） |
| `high` | 高推理 |
| `xhigh` | 极高推理 |

## 修复步骤

1. **检查当前配置**：
   ```bash
   grep reasoning_effort ~/.hermes/config.yaml
   ```

2. **添加 `agent.reasoning_effort`**：
   ```yaml
   agent:
     reasoning_effort: "none"
   ```

3. **重启 Gateway**：
   ```bash
   hermes gateway restart
   # 或
   systemctl --user restart hermes-gateway
   ```

4. **验证**：
   - 刷新 Web UI，推理内容应该不再显示
   - 检查 Gateway 日志：`grep reasoning ~/.hermes/logs/gateway.log`

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 只设置 `delegation.reasoning_effort` | 该配置只控制子 Agent | 添加 `agent.reasoning_effort` |
| 修改后不重启 Gateway | 配置在 Gateway 启动时加载 | `hermes gateway restart` |
| 用 `hermes config set` 设置 | CLI 对 list 值有 bug | 用 `hermes config edit` 或手动修改 |

## 相关

- `hermes-agent` skill: Pitfall "agent.reasoning_effort vs delegation.reasoning_effort 作用域区分"
- `custom` provider: `plugins/model-providers/custom/__init__.py`
- Gateway: `gateway/run.py` → `_load_reasoning_config()`
