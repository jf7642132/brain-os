# Web UI 认证失败 / 速率限制锁定修复

## 问题现象

Web UI 界面显示"未连接"，或 API 请求返回以下错误：
- `{"error":"Unauthorized"}`
- `{"error":"Too many login attempts, please try again later"}`

即使 Web UI 服务进程正常运行且端口 8648 正常监听。

## 根因分析

### 1. 速率限制触发
Web UI 内置基于 IP 的速率限制机制，失败次数达到阈值后锁定 IP：
- **阈值**：`ir=3` 次失败触发单 IP 锁定（60分钟）
- **全局阈值**：`yr=50` 次全局失败触发全局限额（30分钟）
- **锁定文件**：`~/.hermes-web-ui/.login-lock.json`

当多次使用过期/错误的 token 请求 API 时，触发速率限制，后续即使使用正确 token 也会被拒绝。

### 2. Token 文件与运行实例不匹配
Web UI 启动时会读取 `~/.hermes-web-ui/.token` 作为认证令牌。如果：
- token 文件被手动修改
- Web UI 重启后重新生成了 token（旧 token 失效）
- 多个 Web UI 实例使用不同 token

会导致客户端使用的 token 与服务器不匹配。

### 3. 多实例端口冲突
旧 Web UI 进程未完全退出，新进程无法绑定端口，导致服务看似运行但实际未正常响应。

## 修复步骤

### 快速修复（推荐）
```bash
# 1. 清除速率限制
echo '{}' > ~/.hermes-web-ui/.login-lock.json

# 2. 获取当前有效 token
TOKEN=$(cat ~/.hermes-web-ui/.token)

# 3. 验证 API 响应
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8648/api/hermes/memory
```

### 完整修复（含重启）
```bash
# 1. 清除速率限制
echo '{}' > ~/.hermes-web-ui/.login-lock.json

# 2. 杀死所有旧 Web UI 进程
pkill -f "hermes-web-ui"
pkill -f "index.js.*8648"
sleep 2

# 3. 验证端口已释放
ss -tlnp | grep 8648  # 应无输出

# 4. 重启 Web UI
cd /root/.hermes/node/lib/node_modules/hermes-web-ui
/root/.hermes/node/bin/node dist/server/index.js --port 8648 &

# 5. 验证修复
sleep 3
TOKEN=$(cat ~/.hermes-web-ui/.token)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8648/api/hermes/memory
```

## 速率限制文件结构

```json
{
  "passwordIpMap": {},
  "tokenIpMap": {
    "127.0.0.1": {
      "failures": 2,
      "lockedUntil": 0,
      "firstFailureAt": 1778904090892
    }
  },
  "globalMinuteCount": 1,
  "globalMinuteWindow": 1779017607146,
  "globalTotalFailures": 16,
  "globalLockedUntil": 0
}
```

| 字段 | 说明 |
|------|------|
| `tokenIpMap.<ip>.failures` | 该 IP 使用 token 认证的失败次数 |
| `tokenIpMap.<ip>.lockedUntil` | 锁定截止时间（毫秒时间戳），>0 表示已锁定 |
| `globalTotalFailures` | 全局失败总次数 |
| `globalLockedUntil` | 全局限额截止时间 |

## 预防措施

1. **避免频繁失败请求**：确保使用正确的 token，不要反复尝试错误 token
2. **重启前清理进程**：重启 Web UI 前先用 `pkill` 清理旧进程
3. **使用 systemd 管理**：通过 `systemctl restart hermes-web-ui` 而非手动启动，避免多实例冲突

## 相关代码位置

- 速率限制逻辑：`dist/server/index.js` 中的 `gY()` 和 `gr()` 函数
- Token 读取：`dist/server/services/auth.js` 中的 `getToken()` 函数
- 锁定文件路径：`~/.hermes-web-ui/.login-lock.json`
- Token 文件路径：`~/.hermes-web-ui/.token`
