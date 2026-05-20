# Skill Verification & Config Modification Guide

## Session: 2026-05-17 — Skill Library Audit

### Problem Discovered

Self-created skills (not in `bundled_manifest`) may contain outdated or incorrect information. During this session:

1. **`hermes-custom-llm-config`** contained example configs using `astron-code-latest` (讯飞星火，已停用) as the primary model
2. **MEMORY** contained stale information about "429 exhausted" and "双Gateway令牌冲突" that no longer reflected actual state
3. **Config modification** was done via direct `patch`/`write_file` instead of official `hermes config` commands

### Resolution

1. Deleted `hermes-custom-llm-config` (absorbed into `hermes-agent`)
2. Updated MEMORY with accurate current state
3. Added config modification best practices to `hermes-agent` SKILL.md

### Key Verification Steps

Before claiming a problem exists or following a skill's guidance:

```bash
# 1. Check if skill is official
cat ~/.hermes/skills/.bundled_manifest | grep <skill-name>

# 2. Verify actual auth.json state (not assumed)
cat ~/.hermes/auth.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('credential_pool',{}), indent=2))"

# 3. Verify actual config state
hermes config
cat ~/.hermes/config.yaml

# 4. Verify profile .env for multi-profile setups
cat ~/.hermes/profiles/<profile-name>/.env

# 5. Check running processes
pgrep -fa "hermes.*gateway"
```

### Official vs Self-Created Skills

| Type | Location | Authority |
|------|----------|-----------|
| Official | `~/.hermes/skills/.bundled_manifest` | ✅ Definitive |
| Self-created | `~/.hermes/skills/<category>/<name>/` | ⚠️ Verify before using |

### Config Modification Commands

```bash
# View current config
hermes config

# Set a single value
hermes config set model.default sensenova-6.7-flash-lite

# Edit full config
hermes config edit

# Validate config
hermes config check

# Migrate to new schema
hermes config migrate
```

### Pitfall: Stale MEMORY Entries

MEMORY may contain outdated information from previous sessions. Always verify against actual system state:

- `auth.json` shows real credential status (not assumed)
- `.env` files show real environment variables
- `config.yaml` shows real configuration

If MEMORY conflicts with actual state, trust actual state and update MEMORY.
