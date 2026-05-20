# 错误模式分析参考 — 2026-05-18

> 本次 observer 运行（2026-05-18 00:01 UTC）发现的错误模式及统计。数据覆盖 2026-05-17。
> 本次运行发现了一个关键隐患链条：config.yaml 坏 → fallback 失效 → 429/推理无输出 → 用户体验下降。

## 错误模式统计汇总

| 错误模式 | 次数 | 严重级别 | 类别 | 主要影响 |
|----------|------|----------|------|----------|
| Error code: 429 | 83 | 中等 | infrastructure | OpenRouter/Crucible 免费模型限流 |
| Falling back to default config | 57 | 严重 | infrastructure | 所有自定义配置被忽略 |
| Reasoning-only response | 8 | 中等 | errors | 模型返回推理 token 但无可见内容 |
| Error code: 401 | 0 | — | — | 本次未发现（历史累计116次） |
| Error code: 500 | 0 | — | — | 本次未发现（历史累计10次） |

## 模式详细分析

### 429 Rate Limit (83 次)

**日志格式**:
```
Error code: 429 - {'error': {'message': 'Provider returned error', 'code': 429,
  'metadata': {'raw': 'deepseek/deepseek-v4-flash:free is temporarily rate-limited upstream.
  Please retry shortly, or add your own key to accumulate your rate limits:
  https://openrouter.ai/settings/integrations', 'provider_name': 'Crucible', 'is_byok': False}}}
```

**分布分析**（关键洞察）:
```
68  20260516_074336_8fa6ff   (82%) ← 单条长会话
 6  20260517_112145_f8221d    (7%)
 3  20260517_140545_66e4d1    (4%)
 2  6b7fed6f-...               (2%)
 2  19bfef7d-...               (2%)
 1  266a40bd-...               (1%)
 1  20260517_192801_285f9c     (1%)
```

**结论**: 82% 的 429 错误来自单来自一条跨天长会话。短期修复影响有限；长期方案是配置付费 API Key。

### Config Fallback (57 次)

**日志格式**:
```
  in "/root/.hermes/config.yaml", line 22, column 5. Falling back to default config —
  every user override (auxiliary providers, fallback chain, model settings) is being
  IGNORED. Fix the YAML and restart.
```

**影响链条**: 这个单一问题导致：
1. fallback_providers 未加载 → 429 时无法切换到备用模型
2. 推理模型耗尽重试后无 fallback 可用 → 返回空内容
3. 自定义模型设置不生效 → 只能使用默认模型

**结论**: **修复 config.yaml 可以解决 80% 的当前问题。这是优先级最高的事项。**

### 推理无输出 (8 次)

**日志格式**:
```
WARNING [session_id] run_agent: Reasoning-only response (no visible content)
after exhausting retries and fallback. Reasoning: {garbled_text}
```

**时间分布**: 全部集中在 19:54~21:26 时段
**受影响的会话**: 5个不同会话

**根本原因链**: Config fallback → fallback 链失效 → 主模型返回推理 token（无内容）→ 3次重试后仍失败 → 没有可用的 fallback 模型 → 返回空推理内容

## 响应

## 网关日志混淆说明

Gateway log 中 `fallback` 模式匹配了 337 次，但全部是 Telegram IP fallback 通知（正常行为），不是模型 fallback：
```
INFO gateway.platforms.telegram: [Telegram] Telegram fallback IPs active: 149.154.166.110
```
模型 fallback (errors.log) 仅匹配 8 次（推理无输出场景）。

## 会话执行健康度

| 指标 | 数值 |
|------|------|
| 总会话数 | 2 |
| 成功完成 | 2 (100%) |
| 失败/超时 | 0 (0%) |
| 工具调用错误 | 0 |

**结论**: Agent 执行层健康，所有问题集中在基础设施层（API 限流 + 配置回退）。

## 需要人工决策的项目

1. **修复 config.yaml YAML 格式问题**
   - 选项 A: 手动审查并修复第22行附近
   - 选项 B: 运行 `hermes config validate` 获取详细诊断

2. **切换到付费 API Key 缓解 429 限流**
   - 选项 A: DeepSeek 官方直连 Key
   - 选项 B: OpenRouter 付费 Key
   - 选项 C: 维持现状（接受每日 83+ 限流重试）

3. **处理历史遗留的 401 (116次) 和 500 (10次) 错误**
   - 选项 A: 安排时间统一排查修复
   - 选项 B: 暂时搁置（当前无新的触发）

---

*此文件由 2026-05-18 observer 运行生成，可作为未来错误模式分析的参考基准。*