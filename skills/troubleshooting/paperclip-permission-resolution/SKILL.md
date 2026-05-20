---
name: paperclip-permission-resolution
category: troubleshooting
description: Fix Paperclip agents failing to execute Hermes commands due to permission issues
---

# Paperclip Permission Issues Resolution

## Problem Description
Paperclip agents fail to execute Hermes commands with `spawn hermes EACCES` error due to permission restrictions on `/root/` directory hierarchy.

## Root Cause Analysis
The issue occurs when:
1. Paperclip runs as `paperclip` user
2. Hermes is installed in `/root/.hermes/hermes-agent/venv/bin/hermes`
3. The shebang points to `/root/.hermes/hermes-agent/venv/bin/python3` → `/root/.local/share/uv/python/.../python3.11`
4. Permission chain breaks at any level:
   - `/root/` (700) - blocks traversal
   - `/root/.hermes/` (700) - blocks traversal
   - `/root/.local/share/` (700) - blocks Python interpreter access

## Symptoms
- `spawn hermes EACCES(adapter_failed)` error
- `sudo -u paperclip /usr/local/bin/hermes --version` returns "Permission denied"
- TradeRisk-Forum and other agents cannot execute Hermes commands

## Resolution Steps

### 1. Fix Hermes Home Mode Default
**File**: `/root/.hermes/hermes-agent/hermes_cli/config.py`

**Before**:
```python
mode = int(mode_str, 8) if mode_str else 0o700
# ...
os.chmod(path, 0o700)
```

**After**:
```python
mode = int(mode_str, 8) if mode_str else 0o701
# ...
os.chmod(path, 0o701)
```

This ensures `/root/.hermes/` gets 701 permissions (allow traversal) by default, preventing automatic restoration to 700.

### 2. Fix Python Interpreter Access
**Directory**: `/root/.local/share/`

```bash
sudo chmod 751 /root/.local/share/
```

This allows `paperclip` user to traverse to the Python interpreter at `/root/.local/share/uv/python/.../python3.11`.

### 3. Fix Paperclip Database Permissions
**Directories**:
```bash
sudo chmod 700 /root/.paperclip/
sudo chmod 700 /root/.paperclip/instances/default/
sudo chmod 700 /root/.paperclip/instances/default/db/
```

PostgreSQL requires 700 permissions on database directories.

## Verification

### Test Hermes Execution
```bash
sudo -u paperclip /usr/local/bin/hermes --version
```

Expected output:
```
Hermes Agent v0.11.0 (2026.4.23)
Project: /root/.hermes/hermes-agent
Python: 3.11.15
OpenAI SDK: 2.31.0
```

### Test Agent Execution
```bash
paperclipai run --bind lan
```

Check logs for successful agent startup without EACCES errors.

## Prevention

### Systemd Configuration
If running Paperclip via systemd, ensure:
- `HERMES_HOME_MODE=0701` is set in environment
- `/root/.local/share/` has 751 permissions
- `/root/.paperclip/` hierarchy has 700 permissions

### Permission Monitoring
Set up monitoring for critical directories:
```bash
# Check current permissions
ls -ld /root/ /root/.hermes/ /root/.local/share/ /root/.paperclip/

# Verify paperclip user can access
sudo -u paperclip ls /root/.hermes/hermes-agent/venv/bin/python3
```

## Common Pitfalls

### 1. Automatic Permission Restoration
Hermes' `config.py` automatically resets `/root/.hermes/` permissions on every gateway startup. Always verify the default mode is 701, not 700.

### 2. Nested Permission Chain
Remember that permission checks are hierarchical:
- `/root/` must allow traversal (701)
- `/root/.hermes/` must allow traversal (701)
- `/root/.local/share/` must allow traversal (751)
- `/root/.paperclip/` must allow access (700 for PostgreSQL)

### 3. Empty Database Directory
If PostgreSQL fails to initialize, the database directory might be empty. Try:
```bash
rm -rf /root/.paperclip/instances/default/db/
paperclipai run --bind lan
```

## Related Issues
- TradeRisk-Forum agent not starting
- Paperclip agents failing with EACCES
- Hermes command not found by paperclip user
- PostgreSQL initialization failures in Paperclip

## References
- Hermes config: `/root/.hermes/hermes-agent/hermes_cli/config.py`
- Paperclip CLI: `/usr/local/lib/node_modules/paperclipai/dist/index.js`
- Embedded PostgreSQL: `/usr/local/lib/node_modules/paperclipai/node_modules/embedded-postgres/`