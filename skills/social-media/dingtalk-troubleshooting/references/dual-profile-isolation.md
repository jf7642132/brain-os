# Dual-Profile DingTalk Isolation Pattern

## Problem
A single Hermes instance connected to DingTalk exposes the user's memory, conversation history, and knowledge base to anyone who @mentions the bot in a group chat. This is unacceptable when the bot needs to serve a team (e.g., sending task notifications) while keeping personal context private.

## Solution
Run two independent Hermes profiles:
- **Main instance**: Full memory, personal assistant, all platforms
- **DingTalk worker**: Memory disabled, only DingTalk enabled, only team-notification tools

## Discovery Path

This pattern emerged from a session where the user needed to:
1. Connect DingTalk to send kanban task notifications to 4 team members
2. Prevent team members from accessing the user's personal memory/conversation history, memories, knowledge base

The user rejected option A (use main instance with strict allowlist) and option B (manual notification via script). Chose option C: separate Agent instance.

## Implementation Timeline

### Phase 1 — Quick Test (Discarded)
Created a second instance by setting HERMES_HOME=/root/.hermes-dingtalk-worker. This worked but was fragile and non-standard. Replaced with official profile approach.

### Phase 2 — Official Profile (Current)
Used `hermes profile create dingtalk-worker --clone` — the canonical way to create independent instances.

### Phase 3 — systemd Service
Created a systemd service so the worker starts on boot independently of the main gateway.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Use `hermes profile create --clone` instead of manual HERMES_HOME override | Official, maintainable, configs stay in .hermes/ |
| Disable all memory (both memory_enabled and user_profile_enabled) | Prevents any persistence of team member conversations |
| Disable all platforms except DingTalk | Worker should only handle DingTalk messages |
| Set tool permissions to kanban, terminal, file, web | Worker only needs task mgmt tools |
| Disable DingTalk in main instance before starting worker | Stream API does not allow dual connections |

## DingTalk Stream API Constraint

The DingTalk Stream Mode WebSocket connection is per-bot-token. If two gateways connecting to the same bot will cause:
- First connection: succeeds
- Second connection: either fails (server rejects duplicate) or creates race condition on message routing

Resolution: The main instance must have `platforms.dingtalk.enabled: false` before the worker starts.

## Emoji Message Limitation

The DingTalk adapter filters out messages with no text content and no media attachments (line 624-626 in gateway/platforms/dingtalk.py). This means pure emoji messages are silently dropped. To capture a user's DingTalk User ID, they must send a text message (even a text message.

## Profile Structure

```
~/.hermes/
├── config.yaml                    # Main instance config
├── .env                           # Main instance env vars
├── logs/                          # Main instance logs
├── profiles/
│   └── dingtalk-worker/
│       ├── config.yaml            # Worker config (memory off, dingtalk only)
│       ├── .env                   # Worker env vars (only dingtalk credentials)
│       └── logs/                  # Worker logs
```

## systemd Service File

```ini
[Unit]
Description=Hermes DingTalk Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=HOME=/root
ExecStart=/root/.nix-profile/bin/hermes --profile dingtalk-worker gateway run
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Note: `ExecStart` uses `hermes dingtalk-worker gateway run` — this is how profile-specific profile gateway is launched from the main hermes CLI. The profile name becomes a subcommand.