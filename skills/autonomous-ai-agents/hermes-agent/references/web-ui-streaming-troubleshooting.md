# Web UI Streaming Troubleshooting

## Problem
Web UI chat responses appear instantly without streaming animation, or streaming stops mid-response.

## Known Issues in hermes-agent

| Issue # | Description | Fix |
|---------|-------------|-----|
| #25676 | `display.streaming: true` config silently ignored | Update to latest hermes-agent |
| #25723 | Streaming disabled for entire session after one error | Start fresh session or update |
| #25583 | SSE connection drops cause message disappearance | Update to latest hermes-agent |

## Streaming Architecture

```
Web UI Frontend (EventSource)
    ↓ SSE connection
Web UI Backend (/api/chat/stream)
    ↓ WebSocket/API call
Hermes Gateway
    ↓ LLM streaming response
```

- **Protocol**: Server-Sent Events (SSE)
- **Endpoint**: `/api/chat/stream`
- **Client API**: `new EventSource('/api/chat/stream')`
- **Data format**: JSON chunks with `content` field

## Debugging Steps

### 1. Check hermes-agent version
```bash
hermes --version
# Compare with latest release on GitHub
```

### 2. Check gateway logs for streaming errors
```bash
grep -i "stream\|sse\|error" ~/.hermes/logs/gateway.log | tail -20
```

### 3. Check browser console
Open browser DevTools → Console tab:
- Look for errors related to `EventSource`
- Look for failed network requests to `/api/chat/stream`

### 4. Check browser network tab
Open browser DevTools → Network tab:
- Filter by "stream" or "sse"
- Look for:
  - 404 errors (endpoint not found)
  - 500 errors (server error)
  - Connection failures (CORS, firewall)
  - Successful connections but no data

### 5. Test with fresh session
```bash
hermes chat -q "Test streaming response"
```

### 6. Verify model supports streaming
Some models/providers don't support streaming:
- Check provider documentation
- Test with a known streaming-capable model

## Configuration

In `config.yaml`:
```yaml
display:
  streaming: true  # Enable streaming in CLI (not Web UI)

# Web UI streaming is controlled by the Web UI backend, not this config
```

**Note**: `display.streaming: true` only affects CLI output, not Web UI. Web UI streaming is determined by:
1. hermes-agent version (must include streaming bug fixes)
2. Model/provider streaming support
3. Web UI backend configuration

## References
- hermes-agent issues: #25676, #25723, #25583
- Web UI source: `/root/.hermes/node/lib/node_modules/hermes-web-ui/`
- Server SSE implementation: `dist/server/index.js` (search for `socket.on`)