## 小红书封面生成器（基础框架）

### 快速开始

1) 安装依赖

```bash
pip3 install -r requirements.txt
```

2) 启动后端

```bash
uvicorn backend.app:app --reload --port 8000
```

3) 打开前端

直接在浏览器中打开 `frontend/index.html`（建议用VSCode Live Server或任意静态HTTP服务）

4) 使用AI生成（可选）

在终端设置环境变量后再启动后端：

```bash
export DEEPSEEK_API_KEY="你的密钥"
# 可选：
# export DEEPSEEK_API_BASE="https://api.deepseek.com"
# export DEEPSEEK_MODEL="deepseek-chat"
uvicorn backend.app:app --reload --port 8000
```

前端可在控制台设置 `window.useAI = true` 后提交表单，即会调用 `/generate/ai` 接口。

### 现有接口

- GET `/styles`：返回可选风格（从 `templates.json` 读取）
- POST `/generate/preview`：根据标题/作者/风格返回占位HTML（后续可接入AI生成）

### 后续计划

- 集成 DeepSeek/其他模型，产出真实HTML/CSS/JS
- 丰富前端预览、下载为图片等能力

