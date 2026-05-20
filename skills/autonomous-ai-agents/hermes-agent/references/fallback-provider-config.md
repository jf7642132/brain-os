# Fallback Provider Configuration Reference

**Last updated:** 2026-05-17

## Overview

Hermes Agent supports multiple fallback providers for resilience when the primary model fails or hits rate limits.

## Configuration Location

`~/.hermes/config.yaml`

## Example Configuration

```yaml
model:
  default: deepseek/deepseek-v4-flash:free
  provider: openrouter

fallback_providers:
  # First fallback: Token.sensenova.cn (商汤)
  - provider: custom:token.sensenova.cn
    model: astron-code-latest
    base_url: https://token.sensenova.cn/v1
    api_key: ${ASTRON_API_KEY}
    
  # Second fallback: Baidu CoBuddy (free)
  - provider: openrouter
    model: baidu/cobuddy:free
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
    
  # Third fallback: OpenRouter auto-router (free)
  - provider: openrouter
    model: openrouter/free
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
```

## Provider Types

### OpenRouter

```yaml
- provider: openrouter
  model: <model-id>
  base_url: https://openrouter.ai/api/v1
  api_key: ${OPENROUTER_API_KEY}
```

### Custom Endpoint

```yaml
- provider: custom:<provider-name>
  model: <model-id>
  base_url: https://your-endpoint/v1
  api_key: ${YOUR_API_KEY}
```

### Direct Provider (DeepSeek, Anthropic, etc.)

```yaml
- provider: deepseek
  model: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1
  api_key: ${DEEPSEEK_API_KEY}
```

## Updating Configuration

### Method 1: Python yaml module (recommended)

```python
import yaml

with open('/root/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

config['fallback_providers'] = [
    {
        'provider': 'custom:token.sensenova.cn',
        'model': 'astron-code-latest',
        'base_url': 'https://token.sensenova.cn/v1',
        'api_key': '${ASTRON_API_KEY}'
    },
    {
        'provider': 'openrouter',
        'model': 'baidu/cobuddy:free',
        'base_url': 'https://openrouter.ai/api/v1',
        'api_key': '${OPENROUTER_API_KEY}'
    }
]

with open('/root/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
```

### Method 2: hermes config set

```bash
# View current config
hermes config

# Edit config file
hermes config edit
```

## Verification

After updating config, verify:

```bash
# Check config syntax
python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"

# Restart gateway to apply changes
systemctl --user restart hermes-gateway

# Check gateway status
systemctl --user status hermes-gateway
```

## Fallback Behavior

1. **Primary model** fails → Try **fallback 1**
2. **Fallback 1** fails → Try **fallback 2**
3. **Fallback 2** fails → Try **fallback 3**
4. All fail → Return error to user

## Common Pitfalls

### Pitfall 1: Config changes not taking effect

**Symptom:** Updated config.yaml but behavior unchanged

**Fix:**
- CLI: Exit and relaunch (`/quit` then `hermes`)
- Gateway: `systemctl --user restart hermes-gateway`

### Pitfall 2: Missing API key in .env

**Symptom:** Fallback provider returns 401 Unauthorized

**Fix:**
```bash
# Check .env has the key
grep ASTRON_API_KEY ~/.hermes/.env

# Add if missing
echo "ASTRON_API_KEY=your-key-here" >> ~/.hermes/.env
```

### Pitfall 3: Invalid YAML syntax

**Symptom:** Gateway fails to start with YAML parse error

**Fix:**
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml'))"

# Fix indentation (2 spaces per level)
```

### Pitfall 4: Wrong provider name

**Symptom:** Fallback not used, direct error from primary

**Fix:** Ensure provider name matches supported list:
- `openrouter`
- `anthropic`
- `openai`
- `deepseek`
- `custom:<name>`

## API Key Environment Variables

| Provider | Env Variable |
|----------|--------------|
| OpenRouter | `OPENROUTER_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Token.sensenova.cn | `ASTRON_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |

Keys should be stored in `~/.hermes/.env`, NOT in `config.yaml`.
