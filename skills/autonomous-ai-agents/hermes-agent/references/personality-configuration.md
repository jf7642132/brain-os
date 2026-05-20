# Personality 配置参考

## Personality 三层架构

Hermes 的角色和风格由三个独立层面控制：

### 1. Personality (UI 表现层)

**配置位置**: `display.personality` in `config.yaml`

**作用**: 控制语气、表情、颜文字等视觉包装

**可选值**:
- `kawaii` — 可爱风格，使用颜文字和活泼语气
- `professional` — 专业风格
- `minimal` — 极简风格
- 自定义 — 在 `personalities:` 块中定义

**示例**:
```yaml
display:
  personality: "kawaii"

personalities:
  kawaii:
    system_prompt: "你是一个可爱的助手，喜欢用颜文字和活泼的语气..."
    emoji: true
    kaomoji: true
```

### 2. SOUL.md (系统提示词层)

**配置位置**: `SOUL.md` 文件

**作用**: 定义角色身份、行为准则、反驳原则

**核心内容**:
- 身份定义（自主操作者、思考伙伴）
- 主动性要求（主动发现机会、标记问题）
- 反驳原则（带证据强硬反驳）
- 授权边界（什么需要批准，什么可以直接做）
- 语气规范（私下直接，公开克制）

**重要**: SOUL.md 是**核心行为准则**，不受 personality 影响。即使 personality 是 `kawaii`，Agent 依然会：
- 主动标记问题
- 带证据反驳糟糕想法
- 不追着要许可

### 3. Model (模型层)

**配置位置**: `model.default` in `config.yaml`

**作用**: 决定使用哪个 LLM 模型

**注意**: 模型本身没有"人格"，但不同模型的推理风格可能不同

## 三层关系

```
┌─────────────────────────────────────────┐
│  Personality (kawaii)                   │
│  └── 可爱滤镜：颜文字、活泼语气          │
├─────────────────────────────────────────┤
│  SOUL.md                                │
│  └── 核心行为：主动、反驳、授权边界      │
├─────────────────────────────────────────┤
│  Model (deepseek-v4-flash:free)         │
│  └── 推理能力、知识基础                  │
└─────────────────────────────────────────┘
```

**三层互不冲突**：
- `kawaii` 只是给回复加了一层"可爱滤镜"
- 核心角色定位、决策逻辑、反驳行为由 SOUL.md 决定
- 模型决定推理能力和知识基础

## 自定义 Personality

在 `config.yaml` 中定义：

```yaml
display:
  personality: "my-custom"

personalities:
  my-custom:
    system_prompt: |
      你是一个专业的化工品外贸专家，语气直接简洁。
      核心职责：
      - 主动发现商业机会
      - 标记风险和问题
      - 推动工作向前
      - 该反对时带证据强硬反对
    emoji: false
    kaomoji: false
```

## 常见问题

### Q: 为什么改了 personality 没效果？

A: Personality 在 Gateway 启动时加载。需要重启 Gateway：
```bash
systemctl --user restart hermes-gateway
```

### Q: 为什么 Web UI 和 CLI 的 personality 不一样？

A: Web UI 和 CLI 是两个独立入口，可能使用不同的配置。检查：
- CLI: `~/.hermes/config.yaml`
- Web UI: Web UI 后端可能有独立的配置

### Q: 如何完全禁用 personality？

A: 设置 `display.personality: ""` 或 `display.personality: "none"`

## 相关文档

- [Hermes 配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration/)
- [SOUL.md 规范](https://hermes-agent.nousresearch.com/docs/contributing/soul-md/)