# OpenRouter Free Models Testing Workflow

## Quick Reference

### Free Tier Limits

| Account Status | Daily Limit | How to Unlock |
|----------------|-------------|---------------|
| Standard (no credit) | 50 requests | — |
| Boosted (≥$10 credit) | 1000 requests | Add $10+ credits |

**Key points:**
- Limit resets at **UTC 00:00 daily**
- Boosted tier is **permanent** (not temporary)
- Rate limits vary **per model** (some are always limited)
- Privacy settings affect availability (404 errors)

### Testing Workflow

**1. List available free models:**
```python
import requests

api_key = "your-openrouter-key"
response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
models = response.json().get('data', [])
free_models = [m for m in models if m.get('id', '').endswith(':free')]
```

**2. Test representative models:**
```python
test_models = [
    "deepseek/deepseek-v4-flash:free",  # 1M context, best overall
    "baidu/cobuddy:free",               # 131K, coding-focused
    "openrouter/free",                   # Auto-router
]

for model_id in test_models:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-app.local",
            "X-Title": "Your App"
        },
        json={"model": model_id, "messages": [{"role": "user", "content": "Test"}]},
        timeout=20
    )
    print(f"{model_id}: HTTP {response.status_code}")
```

**3. Categorize results:**
- ✅ **Working (200)**: Model is available and responsive
- ⚠️ **Rate Limited (429)**: May reset daily (UTC 00:00)
- ❌ **Privacy/Guardrail (404)**: Configure at [openrouter.ai/settings/privacy](https://openrouter.ai/settings/privacy)

### Recommended Free Models (2026-05)

| Model | Context | Best For | Status |
|-------|---------|----------|--------|
| `deepseek/deepseek-v4-flash:free` | 1M | General chat, coding, reasoning | ✅ Tested working |
| `baidu/cobuddy:free` | 131K | Coding, AI Agent workflows | ✅ Tested working |
| `openrouter/free` | Varies | Auto-routing to available model | ✅ Tested working |
| `google/gemma-4-26b-a4b-it:free` | 256K | General tasks | ⚠️ Rate limited |
| `meta-llama/llama-3.3-70b-instruct:free` | 131K | General tasks | ⚠️ Rate limited |

### Common Issues

**429 Rate Limit:**
- Wait a few minutes and retry
- Switch to another free model
- Some models have stricter limits than others

**404 Privacy/Guardrail:**
- Visit [openrouter.ai/settings/privacy](https://openrouter.ai/settings/privacy)
- Enable the required data policy for the provider
- Some providers require explicit consent for data logging

**Model not found:**
- Check if the model ID ends with `:free`
- Some models are only available to paid accounts
- Verify the provider supports the model
