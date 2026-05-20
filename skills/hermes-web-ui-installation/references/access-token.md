# Hermes Web UI 访问令牌

## 令牌位置
- **npm 全局安装版**：`/root/.hermes-web-ui/.token`

## 令牌格式
```
<64字符十六进制字符串>
```

## 使用方式

### Web UI 登录
访问 `http://<host>:8648/` 时，系统会自动读取该令牌进行认证。

### API 调用
```bash
curl -H "Authorization: Bearer c1a49e34239e987ee5a33def2499018c2876fd424037642dd4c38e03b73605fa" \
  http://<YOUR_SERVER_IP>:8648/api/hermes/sessions
```

## 重置令牌
```bash
# 停止服务
sudo systemctl stop hermes-web-ui.service

# 删除旧令牌
sudo rm /root/.hermes-web-ui/.token

# 重启服务（会自动生成新令牌）
sudo systemctl start hermes-web-ui.service

# 获取新令牌
cat /root/.hermes-web-ui/.token
```

## 安全建议
- 令牌文件权限应为 `600`（仅所有者可读写）
- 不要将令牌提交到 Git 仓库
- 定期轮换令牌以提高安全性