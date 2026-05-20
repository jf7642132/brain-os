# Gateway Log Error Pattern Reference

This document documents the actual error patterns found in Hermes Agent logs, for use by the Observer skill when scanning gateway logs.

## 503 Errors - Model Not Found

**Pattern**: `Error code: 503`

**Common format**:
```
Error code: 503 - {'error': {'code': 'model_not_found', 'message': 'No available channel for model deepseek-v4-nothink-expert under group default (distributor) (request id: ...)', 'type': 'new_api_error'}}
```

**Model names to watch**:
- `deepseek-v4-nothink-expert` (high frequency)
- `deepseek-v3`
- `deepseek-chat`

**Root cause**: Model quota exhausted or provider service down

**Prevention**: Add fallback providers in config

## 401 Errors - Authentication Failed

**Pattern**: `Error code: 401`

**Common format**:
```
Error code: 401 - {'error': {'code': 'invalid_token', 'message': 'Invalid API key or token expired'}}
```

**Root cause**: API key expired, token revoked, or incorrect configuration

**Prevention**: Regular token rotation, monitor token expiry

## 429 Errors - Rate Limiting

**Pattern**: `Error code: 429`

**Common formats** (two variants seen):

1. OpenRouter free model ratelimit:
```
Error code: 429 - {'error': {'message': 'Provider returned error', 'code': 429, 'metadata': {'raw': 'deepseek/deepseek-v4-flash:free is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Crucible', 'is_byok': False}}}
```

2. Sensetime generic ratelimit:
```
Error code: 429 - {'error': {'message': 'Service temporarily unavailable', 'type': 'rate_limit_error', 'code': '3'}}
```

**Models frequently affected**:
- `deepseek/deepseek-v4-flash:free` via OpenRouter/Crucible
- `google/gemma-4-31b-it:free` via Google AI Studio
- `sensenova-6.7-flash-lite` via Sensetime

**Root cause**: Free-tier provider rate limits; single long-running sessions accumulate many 429s (82% from one session on 2026-05-17)

**Prevention**: Add paid API keys, configure fallback_providers, or throttle request rate

**Detection tip**: Extract session IDs from 429 log entries to identify concentration — `grep 'Error code: 429' errors.log | grep -oP '(?<=\\[)[^\\]]+(?=\\])' | sort | uniq -c | sort -rn`

## 500 Errors - Server Error

**Pattern**: `Error code: 500`

**Common format**:
```
Error code: 500 - {'error': {'code': 'internal_error', 'message': 'Internal server error'}}
```

**Root cause**: Provider-side issue, temporary service disruption

**Prevention**: Implement circuit breaker pattern, add fallback providers

## Session Summary Failures

**Pattern**: `Session summarization failed after 3 attempts`

**Common format**:
```
WARNING [session_id] root: Session summarization failed after 3 attempts: Error code: 503
```

**Root cause**: Model unavailability during summary phase

**Prevention**: Use降级模型 (degraded model) for summarization, implement retry with exponential backoff

## Fallback Triggers

**Pattern**: `fallback` (case-insensitive)

**Common triggers**:
- `FailoverError`
- `embedded run failover`
- `candidate_failed`

**Meaning**: System attempted to switch to backup model/provider

**Prevention**: Ensure fallback_providers are properly configured with healthy models

## Chinese Language Output Requirement

All Observer output must be in Chinese:
- Section headers: 基础设施异常，Agent 执行异常，今日建议改进
- Status indicators: 🟢 (健康), 🟡 (警告), 🔴 (严重)
- All descriptions and explanations in Chinese

## Config Fallback - YAML Parsing Failure

**Pattern**: `Falling back to default config`

**Common format**:
```
  in "/root/.hermes/config.yaml", line {N}, column {M}. Falling back to default config — every user override (auxiliary providers, fallback chain, model settings) is being IGNORED. Fix the YAML and restart.
```

**Root cause**: YAML syntax error in config.yaml prevents parser from loading custom configuration. The location (line/column) indicates where the parser stopped, not necessarily the exact error location.

**Impact**: Critical - all custom config ignored:
- fallback_providers not loaded (model failover broken)
- Model settings / provider configs not applied
- Auxiliary provider chain disabled

**Detection**: Always grep errors.log separately for this pattern — it appears on every startup/check cycle. On 2026-05-17 it appeared 57 times.

**Prevention**: Run `hermes config validate` after any config.yaml change. Monitor startup logs for this warning.

## Reasoning-Only Response After Exhausting Retries

**Pattern**: `Reasoning-only response (no visible content) after exhausting retries and fallback`

**Common format**:
```
WARNING [session_id] run_agent: Reasoning-only response (no visible content) after exhausting retries and fallback. Reasoning: {garbled_text}
```

**Root cause**: Upstream model API returns valid HTTP response but the `choices[0].delta.content` is always empty while `choices[0].delta.reasoning` is populated. This happens when:
1. The model produces reasoning tokens but no final output
2. Fallback chain is either absent or also uses reasoning-only models
3. The config fallback issue (above) means fallback_providers config is ignored

**Impact**: User sees an empty/incomplete response. 8 occurrences on 2026-05-17.

**Prevention**: Fix config.yaml so fallback chain works. Add content validation middleware that rejects responses with content=None. Use a non-reasoning model as the final fallback target.