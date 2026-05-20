# Paperclip API CRUD Patterns

> Auth + mutation patterns discovered while persisting Phase 1 Issues

## Authentication

Paperclip uses **session cookies** (not bearer tokens) for API auth:

```bash
# Login - get cookie
COOKIE=$(curl -s -c - -X POST "http://localhost:3100/api/auth/sign-in/email" \
  -H "Content-Type: application/json" -H "Origin: http://localhost:3100" \
  -d '{"email":"admin@example.com","password":"..."}' \
  | grep session_token | awk '{print $NF}')
```

## Mutations (Create/Update/Delete)

Every mutation request **must** include:
- Cookie header: `-b "paperclip-default.session_token=$COOKIE"`
- Origin header: `-H "Origin: http://localhost:3100"`
- Content-Type: `-H "Content-Type: application/json"`

Without Origin header → `"Board mutation requires trusted browser origin"` (401)

## Create Issue

```python
import requests
s = requests.Session()
s.post(f"{BASE}/api/auth/sign-in/email",
    json={"email": "...", "password": "..."},
    headers={"Origin": BASE})

s.headers.update({"Origin": BASE})

r = s.post(f"{BASE}/api/companies/{company_id}/issues",
    json={
        "projectId": project_id,
        "title": "Issue title",
        "description": "Issue description with \n newlines",
        "status": "todo",  # backlog/todo/in_progress/done/blocked
        "assigneeAgentId": agent_id,  # full UUID, not short form
        "priority": "high"  # high/medium/low
    })
# Status: 201 Created
# Returns full issue object with identifier (e.g. "CMP-57")
```

## Get Agents (to find correct UUIDs)

```python
r = s.get(f"{BASE}/api/companies/{company_id}/agents")
agents = {a['name']: a for a in r.json()}
ceo_id = agents['CEO']['id']
```

## Update Goal

```python
r = s.patch(f"{BASE}/api/companies/{company_id}/goals/{goal_id}",
    json={"description": "Updated description"})
```

## Common Issue Fields

| Field | Type | Example |
|-------|------|---------|
| projectId | UUID | bebdac53-... |
| title | string | "📋 Product line input" |
| description | string | "Detailed task..." |
| status | enum | backlog/todo/in_progress/done/blocked |
| assigneeAgentId | UUID or null | adda628a-... |
| priority | enum | high/medium/low |
| parentId | UUID or null | For sub-issues |

## Notes

- Cannot delete issues via API (DELETE returns 404 even for valid IDs)
- Duplicate creation is possible (no idempotency key on create endpoint)
- Python requests library works better than curl for chained calls
- A `requests.Session()` preserves cookies across calls
