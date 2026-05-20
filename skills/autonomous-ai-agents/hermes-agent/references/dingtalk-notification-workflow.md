# DingTalk Notification Subscription Workflow

## Overview

This document describes the workflow for setting up DingTalk task notifications for team collaboration using Hermes Kanban.

## Prerequisites

1. DingTalk credentials configured in `.env`:
   ```
   DINGTALK_CLIENT_ID=dingnwbbcakq2zgjnesj
   DINGTALK_CLIENT_SECRET=ROhMSzzHak3DfB_Z62QL9gy8lL9-hjIDQtZG8XMExHwvGMLi99Sd0Muli7CmLI9F
   ```

2. Gateway connected to DingTalk Stream Mode (verified in logs: `✓ dingtalk connected`)

3. `DINGTALK_ALLOW_ALL_USERS=true` set in `.env` (or add specific User IDs to `DINGTALK_ALLOWED_USERS`)

## Workflow

### Step 1: Capture User IDs

When team members send messages in the DingTalk group, their encrypted User IDs are logged in the gateway:

```
2026-05-15 08:49:35,973 INFO gateway.run: inbound message: platform=dingtalk user=赵九峰 chat=cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M= msg='你好'
```

**User ID format**: `$:LWCP_v1:$VqWUaB7Bw9Guqgnj1pPqOw==` (encrypted, cannot be obtained from DingTalk admin backend)

**Chat ID (group)**: `cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=`

### Step 2: Create Kanban Tasks

```bash
dingtalk-worker kanban create "T1 系统运维清单整理" --body "梳理公司所有系统的运维清单"
dingtalk-worker kanban create "T2 OA+安全运维现状整理" --body "整理OA系统和安全运维现状"
# ... etc
```

### Step 3: Subscribe Notifications

```bash
# Subscribe to a specific task
dingtalk-worker kanban notify-subscribe <task_id> --platform dingtalk --chat-id <chat_id>

# Example:
dingtalk-worker kanban notify-subscribe t_6d0d72ca --platform dingtalk --chat-id cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=
```

### Step 4: Verify Subscription

```bash
dingtalk-worker kanban list
```

Output shows subscription status for each task.

## Notification Behavior

- **Channel**: Notifications are sent to the group chat, not private DM
- **Format**: Message includes `@<user>` mention to notify the responsible person
- **Trigger**: Task status changes (ready → in_progress → done)

## Security Considerations

1. **Memory isolation**: For public-facing agents, set `memory.memory_enabled = false` to prevent data leakage
2. **User authorization**: Use `DINGTALK_ALLOW_ALL_USERS=true` for open groups, or specify `DINGTALK_ALLOWED_USERS` for restricted access
3. **Credential protection**: DingTalk credentials in `.env` are redacted from logs and responses

## Troubleshooting

### "Unauthorized user" warning in logs

**Cause**: User ID not in allowlist

**Fix**: 
- Option A: Set `DINGTALK_ALLOW_ALL_USERS=true`
- Option B: Add specific User IDs to `DINGTALK_ALLOWED_USERS`

### "Weixin bot token already in use"

**Cause**: Multiple gateways trying to use the same DingTalk/Weixin credentials

**Fix**: Ensure only one gateway instance uses each platform's credentials. Use separate profiles for different platforms.

### Task notifications not arriving

**Check**:
1. Gateway is running: `dingtalk-worker gateway status`
2. DingTalk connected: Check logs for `✓ dingtalk connected`
3. Subscription exists: `dingtalk-worker kanban list`
4. Task status changed: Tasks must transition from `ready` to `in_progress` or `done`

## Reference

- Official docs: https://hermes-agent.nousresearch.com/docs/user-guide/profiles
- DingTalk integration: https://hermes-agent.nousresearch.com/docs/user-guide/messaging