import os
import httpx
import time
from typing import Dict, Any


class DeepSeekClient:
    def __init__(self) -> None:
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '').strip()
        if not self.api_key:
            raise RuntimeError('DEEPSEEK_API_KEY 未设置')
        # 可覆盖基础地址与模型名
        self.base_url = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com').rstrip('/')
        self.model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')

    def chat(self, messages: list[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json',
        }
        payload: Dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        # 简单指数退避重试
        attempts = int(os.environ.get('DEEPSEEK_RETRY', '3'))
        base_delay = float(os.environ.get('DEEPSEEK_RETRY_BASE', '0.8'))
        timeout = float(os.environ.get('DEEPSEEK_TIMEOUT', '60'))
        last_exc: Exception | None = None
        for i in range(attempts):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    return data['choices'][0]['message']['content']
            except Exception as e:
                last_exc = e
                if i < attempts - 1:
                    time.sleep(base_delay * (2 ** i))
        raise RuntimeError(f"DeepSeek请求失败: {last_exc}")


def build_prompt_html(title: str, author: str, template: Dict[str, Any]) -> list[Dict[str, str]]:
    # 将模板信息串联成系统与用户消息
    system = (
        "你是一名资深网页与营销视觉设计师，返回完整、可运行的HTML页面（内联CSS/JS允许），"
        "确保比例3:4，文字为主体，并遵循给定设计风格要点。仅返回HTML字符串，不要解释。"
    )

    style_desc = template.get('style_details', {})
    requirements = template.get('requirements', {})

    parts = [
        template.get('prompt_template', ''),
        '\n\n【基本要求】',
        '\n'.join([f"- {k}：{v}" for k, v in requirements.items() if v]),
        '\n\n【设计风格】',
        style_desc.get('设计风格', ''),
        '\n\n【文字排版风格】',
        style_desc.get('文字排版风格', ''),
        '\n\n【视觉元素风格】',
        style_desc.get('视觉元素风格', ''),
        '\n\n【用户输入】',
        f"- 标题：{title}",
        f"- 作者：{author or ''}",
    ]

    user = '\n'.join([p for p in parts if p])
    return [
        { 'role': 'system', 'content': system },
        { 'role': 'user', 'content': user }
    ]


def generate_cover_html(title: str, author: str, template: Dict[str, Any]) -> str:
    from .cache_service import cache_service
    
    style_id = template.get('id', '')
    
    # 尝试从缓存获取
    cached_html = cache_service.get(title, author, style_id)
    if cached_html:
        print(f"缓存命中: {title} - {style_id}")
        return cached_html
    
    # 缓存未命中，调用AI生成
    print(f"缓存未命中，调用AI生成: {title} - {style_id}")
    client = DeepSeekClient()
    messages = build_prompt_html(title, author, template)
    content = client.chat(messages)
    
    # 去除可能的Markdown代码围栏
    content = content.strip()
    if content.startswith('```'):
        # 形如 ```html\n...\n``` 或 ```\n...\n```
        parts = content.split('\n', 1)
        if len(parts) == 2:
            body = parts[1]
            if body.endswith('```'):
                body = body[:-3]
            content = body.strip()
    
    # 将结果存入缓存
    cache_service.set(title, author, style_id, content)
    
    return content


