# Web UI 迁移指南：源码构建 → 官方npm包（历史参考）

> ⚠️ **此迁移已完成（2026-05-17）**。旧源码目录 `/root/hermes-web-ui/` 已删除，**不再支持源码构建部署**。

## 背景

Hermes Web UI 原本有两种部署方式：
1. **源码构建**（旧）：从 GitHub 克隆源码，本地 `npm install` + `npm run build`
2. **官方npm包**（推荐）：`npm install -g hermes-web-ui`

两种方式的**数据目录完全相同**（`/root/.hermes-web-ui/`），因此迁移时数据自动保留。

## 迁移原因

| | 源码构建 | npm包 |
|---|---|---|
| 更新方式 | 手动 `git pull` + `npm run build` | `npm update -g` |
| 路径管理 | 自定义 `/root/hermes-web-ui/` | 全局 npm 路径 |
| 修改源码 | 可以，但容易和官方冲突 | 不推荐，升级会覆盖 |
| 稳定性 | 依赖本地构建环境 | 预构建，更稳定 |

## 迁移步骤（已完成）

### 1. 停止当前服务
```bash
systemctl stop hermes-web-ui
pkill -f "hermes-web-ui/dist/server/index.js"
sleep 2
ss -tlnp | grep 8648  # 确认端口已释放
```

### 2. 安装官方npm包
```bash
npm config set registry https://registry.npmjs.org
npm install -g hermes-web-ui@latest
```

### 3. 确认安装
```bash
# 版本
cat /root/.hermes/node/lib/node_modules/hermes-web-ui/package.json | grep '"version"'

# CLI命令
ls -la /root/.hermes/node/bin/hermes-web-ui
```

### 4. 更新 systemd 服务
```ini
[Unit]
Description=Hermes Web UI (npm package)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.hermes
ExecStart=/root/.hermes/node/bin/node /root/.hermes/node/lib/node_modules/hermes-web-ui/dist/server/index.js --port 8648
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=BIND_HOST=::
Environment=PORT=8648

[Install]
WantedBy=multi-user.target
```

### 5. 重启并验证
```bash
systemctl daemon-reload
systemctl start hermes-web-ui
sleep 3

# HTTP响应
curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8648/

# 健康检查
curl -s http://127.0.0.1:8648/health | jq '.'

# 数据完整性
cat /root/.hermes-web-ui/.token
ls -lh /root/.hermes-web-ui/hermes-web-ui.db
```

### 6. 清理旧源码
```bash
rm -rf /root/hermes-web-ui
```

## 数据目录说明

两种部署方式共享同一数据目录 `/root/.hermes-web-ui/`：

| 文件/目录 | 用途 |
|-----------|------|
| `.token` | 认证令牌 |
| `hermes-web-ui.db` | SQLite 数据库（会话、配置等） |
| `upload/` | 用户上传文件 |
| `logs/` | 日志文件 |
| `examples/` | 示例文件 |

迁移时**无需拷贝任何数据**，因为路径完全一致。

## 当前状态（2026-05-17）

✅ 迁移已完成，当前仅使用官方npm包部署。
✅ 旧源码目录已删除。
✅ 数据完整保留（token、数据库、上传文件）。
✅ 服务运行正常，HTTP 200。