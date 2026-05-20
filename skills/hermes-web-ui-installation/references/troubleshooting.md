# Hermes Web UI 服务故障排查指南

## 问题现象
- Web UI 无法访问（浏览器连接被拒绝或超时）
- `systemctl status hermes-web-ui` 命令超时/卡住
- 服务配置看起来正确但端口未监听

## 诊断步骤（按优先级）

### 1. 检查端口监听状态（最可靠）
```bash
ss -tlnp | grep 8648
```
- ✅ 有输出（`*:8648`）→ 端口正常监听，问题可能在防火墙/路由
- ❌ 无输出 → 服务未运行，继续下一步

### 2. 检查进程状态
```bash
ps aux | grep "index.js" | grep -v grep
```
- ✅ 有进程 → 服务在运行但可能卡住，尝试重启
- ❌ 无进程 → 服务未启动，检查日志

### 3. 验证 HTTP 响应
```bash
curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8648/
```
- ✅ `HTTP 200` → 服务正常，问题在外部（防火墙、网络路由、浏览器）
- ❌ 连接拒绝 → 服务未正常启动，继续下一步

### 4. 检查服务配置
```bash
cat /etc/systemd/system/hermes-web-ui.service
```
确认 ExecStart 指向 **npm 包路径**：
```
ExecStart=/root/.hermes/node/bin/node /root/.hermes/node/lib/node_modules/hermes-web-ui/dist/server/index.js --port 8648
```

### 5. 重启服务（恢复卡住状态）
```bash
systemctl stop hermes-web-ui
systemctl start hermes-web-ui
sleep 3
ss -tlnp | grep 8648
```

## ⚠️ 重要注意事项

### `systemctl status` 会超时
`systemctl status hermes-web-ui` 命令可能卡住/超时，**不要依赖它作为主要诊断工具**。改用 `ss -tlnp` 和 `curl` 检查。

### 服务卡住时的恢复
如果服务进程存在但端口未监听，或 `systemctl status` 卡住：
1. `systemctl stop hermes-web-ui` 等待服务完全停止
2. `systemctl start hermes-web-ui` 重新启动
3. 验证端口监听和 HTTP 响应

### 防火墙检查
如果本地 `curl http://127.0.0.1:8648/` 返回 200 但远程无法访问：
```bash
# 检查防火墙规则
iptables -L -n | grep 8648
# 或
firewall-cmd --list-ports
```

### 端口冲突
如果端口被其他进程占用：
```bash
ss -tlnp | grep 8648
# 查看占用进程，确认是否为正确的 hermes-web-ui 进程
```

## 快速诊断脚本
```bash
#!/bin/bash
echo "=== Hermes Web UI 诊断 ==="
echo "1. 端口监听:"
ss -tlnp | grep 8648 || echo "   ❌ 端口 8648 未监听"
echo "2. 进程状态:"
ps aux | grep "index.js" | grep -v grep || echo "   ❌ 无相关进程"
echo "3. HTTP 响应:"
curl -s -o /dev/null -w "   HTTP %{http_code}\n" http://127.0.0.1:8648/ || echo "   ❌ 连接失败"
echo "4. 服务配置:"
cat /etc/systemd/system/hermes-web-ui.service | grep -E "ExecStart|Environment" || echo "   ❌ 配置缺失"
```