---
name: gradio-webui
description: 快速搭建基于 Gradio 的 Hermes Agent 可视化网页界面
author: Hermes
tags: [webui, gradio, frontend, visualization]
---

# Hermes Gradio WebUI 搭建技能

快速为 Hermes Agent 搭建一个基于 Gradio 的可视化网页聊天界面。

## 步骤

1. **创建项目目录**
   ```bash
   mkdir -p /root/hermes-webui
   ```

2. **创建主程序 `app.py`**
   - 使用 Gradio ChatInterface 实现流式对话
   - 兼容 OpenAI API 格式
   - 支持环境变量配置 API 地址、API Key、模型名称

3. **创建依赖文件 `requirements.txt`**
   ```
   gradio>=4.0.0
   requests>=2.31.0
   ```

4. **创建启动脚本 `start.sh`**
   - 自动检测虚拟环境路径
   - 使用 hermes-agent 已有的 Python 环境

5. **启动服务**
   ```bash
   cd /root/hermes-webui && ./start.sh
   ```

## 环境变量配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| HERMES_API_URL | API 地址 | http://localhost:8000/v1/chat/completions |
| HERMES_API_KEY | API 密钥 | (空) |
| HERMES_MODEL | 模型名称 | ark-code-latest |
| HOST | 监听地址 | 0.0.0.0 |
| PORT | 监听端口 | 7860 |

## 注意事项

- Gradio 6.x 版本 API 变化较大，ChatInterface 参数和旧版本不兼容：
  - `theme` 参数已从构造函数移除
  - `retry_btn`, `undo_btn`, `clear_btn` 等参数不再支持
  - 需要简化参数列表才能正常运行
- 需要使用兼容 OpenAI 格式的 API 服务
- 默认监听 0.0.0.0:7860，可通过浏览器直接访问

## 文件结构

```
/root/hermes-webui/
├── app.py          # 主程序
├── requirements.txt
└── start.sh        # 启动脚本
```

## 开机自启（可选）

创建 `/etc/systemd/system/hermes-webui.service`：
```ini
[Unit]
Description=Hermes WebUI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/hermes-webui
ExecStart=/root/hermes-webui/start.sh
Restart=always
Environment=HOST=0.0.0.0
Environment=PORT=7860

[Install]
WantedBy=multi-user.target
```

启用：
```bash
systemctl daemon-reload
systemctl enable hermes-webui
systemctl start hermes-webui
```
