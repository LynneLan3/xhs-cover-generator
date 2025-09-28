# 小红书封面生成器 (XHS Cover Generator)

基于AI的小红书封面生成工具，支持多种风格模板，快速生成吸引眼球的封面图片。

## 功能特点

- 🎨 多种封面风格模板
- 🚀 快速生成封面
- 💾 智能缓存机制
- 🖼 实时预览效果
- 📱 响应式设计

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python, FastAPI
- AI：DeepSeek API

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动后端服务：
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

3. 访问前端页面：
打开 `frontend/index.html`

## 使用说明

1. 输入标题和作者
2. 选择喜欢的封面风格
3. 点击生成按钮
4. 等待生成完成
5. 下载或复制生成的封面

## 缓存机制

- 相同的标题和风格组合会启用缓存
- 缓存有效期为24小时
- 支持自动清理过期缓存

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

