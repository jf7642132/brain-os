# YAML Config Validation Reference

## Overview

The `config.yaml` file controls Hermes Agent behavior. YAML syntax errors cause the system to fall back to default configuration, ignoring all user customizations.

## Common YAML Errors

### Error 1: Block Mapping Syntax

**Error message**:
```
Failed to parse /root/.hermes/config.yaml: while parsing a block mapping
in "/root/.hermes/config.yaml", line 22, column 5
expected <block end>, but found '<block mapping start>'
```

**Cause**: Incorrect indentation or nested mapping syntax.

**Example problematic YAML**:
```yaml
agent:
  max_turns: 90
  reasoning_effort: "none"
    tool_use_enforcement: "auto"  # ← Wrong: extra indentation
```

**Fix**: Ensure consistent 2-space indentation:
```yaml
agent:
  max_turns: 90
  reasoning_effort: "none"
  tool_use_enforcement: "auto"  # ← Correct: same indentation level
```

### Error 2: Missing Colon

**Error message**:
```
while parsing a block mapping
expected <block end>, but found '<scalar>'
```

**Cause**: Missing colon after key.

**Fix**: Add the missing colon.

### Error 3: Unquoted Special Characters

**Error message**:
```
mapping values are not allowed here
```

**Cause**: Special characters in values without quotes.

**Fix**: Quote the value:
```yaml
# Wrong
model: sensenova-6.7-flash-lite

# Correct
model: "sensenova-6.7-flash-lite"
```

## Validation Commands

### Quick Validation

```bash
# Using Python
python -c "import yaml; yaml.safe_load(open('/root/.hermes/config.yaml'))" && echo "YAML valid" || echo "YAML invalid"
```

### Detailed Validation

```bash
# Using yamllint (if installed)
yamllint /root/.hermes/config.yaml
```

## Impact of Config Errors

| Error Type | Impact |
|------------|--------|
| YAML syntax error | All custom config ignored, fallback to defaults |
| Missing key | Default value used |
| Invalid value type | Error or default used |

**Critical**: When "Falling back to default config" appears in logs, ALL custom settings are ignored:
- `fallback_providers` — not used
- `model` settings — not applied
- `auxiliary providers` — not configured

## Detection in Observer

When scanning logs for "Falling back to default config":

```bash
grep -c 'Falling back to default config' errors.log
```

If count > 0:
1. Run YAML validation immediately
2. Report as high-severity infrastructure issue
3. Recommend config fix and gateway restart

## Historical Context

- 2026-05-17: 57 "Falling back to default config" warnings detected
- Root cause: YAML syntax error at line 22, column 5
- Status: YAML syntax now validates correctly, but historical warnings persist in logs
- Action: Monitor for new warnings; old warnings in rotated logs are informational only