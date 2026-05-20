# Credential Pool Debugging Workflow

## Quick Reference

### Checking Credential Status

```bash
cat ~/.hermes/auth.json | jq '.credential_pool.<provider>'
```

### Key Fields to Check

| Field | Meaning | Action if problematic |
|-------|---------|----------------------|
| `last_status` | Current credential status | `ok` = working, `exhausted` = needs update |
| `last_error_code` | HTTP error code | 429 = rate limit, 401 = auth failure |
| `last_error_message` | Error description | "rpm exhausted" = rate limit hit |
| `last_status_at` | When status was last checked | Old timestamp = stale state |

### Common Scenarios

**1. `last_status: "exhausted"` with `last_error_message: "rpm exhausted"`**
- The credential has hit rate limits
- **Fix:** Wait for reset OR update the credential with a new key
- **Reset command:** `hermes auth reset <provider>`

**2. `last_status: "ok"` but API calls fail with 401**
- Credential pool state is stale
- **Fix:** `hermes auth reset <provider>` to clear cached state

**3. `last_error_code: 401` with "Forbidden"**
- API key is invalid or expired
- **Fix:** Update key in `.env` and run `hermes auth reset <provider>`

**4. Provider not in `credential_pool`**
- Key exists in `.env` but not registered in auth.json
- **Fix:** Run `hermes auth add` to register the credential

### API Key Format Confusion

| Format | Example | Typical Provider |
|--------|---------|------------------|
| Standard OpenAI-style | `sk-xxx` | OpenRouter, DeepSeek, OpenAI |
| Colon-separated | `xxx:yyy` | 火山引擎, 讯飞, some Chinese providers |
| Custom format | Varies | Check provider docs |

**Important:**
- The `:` format may require special handling or may be for a different provider entirely
- **Always verify which provider a key belongs to before configuring**
- Check `auth.json` to see which provider a key is registered under

### Provider Name Matching

Provider names in `config.yaml` must match `auth.json` credential_pool keys exactly:

```yaml
# config.yaml
fallback_providers:
  - provider: custom:token.sensenova.cn  # Must match auth.json key
    model: sensenova-6.7-flash-lite
    base_url: https://token.sensenova.cn/v1
    # api_key omitted - reads from auth.json credential_pool
```

```json
// auth.json
"credential_pool": {
  "custom:token.sensenova.cn": [
    {
      "access_token": "sk-xxx...",
      "base_url": "https://token.sensenova.cn/v1",
      ...
    }
  ]
}
```

### Debugging Steps

1. **Check auth.json status:**
   ```bash
   cat ~/.hermes/auth.json | jq '.credential_pool.<provider> | .[] | {last_status, last_error_code, last_error_message}'
   ```

2. **Check .env for the key:**
   ```bash
   grep <KEY_NAME> ~/.hermes/.env
   ```

3. **Test the API directly:**
   ```python
   import requests
   response = requests.post(
       "https://provider.example.com/v1/chat/completions",
       headers={"Authorization": f"Bearer YOUR_KEY"},
       json={"model": "test-model", "messages": [{"role": "user", "content": "test"}]}
   )
   print(response.status_code, response.text[:200])
   ```

4. **Reset credential state:**
   ```bash
   hermes auth reset <provider>
   ```

5. **Restart gateway:**
   ```bash
   hermes gateway restart
   ```
