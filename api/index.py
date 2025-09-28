import os
import sys
import json
from pathlib import Path

# 获取当前文件的绝对路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))

# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

# 导入必要的模块
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 创建 FastAPI 应用
app = FastAPI(title='XHS Banner Generator API')

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 定义数据模型
class GeneratePayload(BaseModel):
    title: str
    author: str | None = ''
    style_id: str

# 模板数据 - 直接嵌入到代码中，避免文件路径问题
TEMPLATES_DATA = {
    "templates": [
        {
            "id": "style_1",
            "name": "柔和卡片风",
            "description": "温馨柔和的卡片设计风格",
            "example_image": "",
            "prompt_template": "你是一位优秀的网页和营销视觉设计师，具有丰富的UI/UX设计经验，曾为众多知名品牌打造过引人注目的营销视觉，擅长将现代设计趋势与实用营销策略完美融合。现在需要为我创建一张专业级小红书封面。",
            "requirements": {
                "尺寸与基础结构": "比例严格为3:4（宽:高），设计一个边框为0的div作为画布，确保生成图片无边界",
                "技术实现": "使用现代CSS技术（如flex/grid布局、变量、渐变）"
            },
            "style_details": {
                "设计风格": "柔和温馨的卡片风格",
                "文字排版风格": "清晰易读的现代字体",
                "视觉元素风格": "简洁优雅的视觉元素"
            }
        },
        {
            "id": "style_2", 
            "name": "现代简约风",
            "description": "简洁现代的设计风格",
            "example_image": "",
            "prompt_template": "创建现代简约风格的小红书封面",
            "requirements": {
                "尺寸与基础结构": "比例严格为3:4（宽:高）",
                "技术实现": "使用现代CSS技术"
            },
            "style_details": {
                "设计风格": "现代简约风格",
                "文字排版风格": "简洁的字体排版",
                "视觉元素风格": "极简的视觉元素"
            }
        },
        {
            "id": "style_3",
            "name": "活力橙色风",
            "description": "充满活力的橙色主题设计",
            "example_image": "",
            "prompt_template": "创建活力橙色风格的小红书封面",
            "requirements": {
                "尺寸与基础结构": "比例严格为3:4（宽:高）",
                "技术实现": "使用现代CSS技术"
            },
            "style_details": {
                "设计风格": "活力橙色风格",
                "文字排版风格": "动感的字体设计",
                "视觉元素风格": "充满活力的视觉元素"
            }
        }
    ]
}

@app.get('/')
def serve_index():
    """提供前端首页"""
    frontend_path = os.path.join(project_root, 'frontend', 'index.html')
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        return {"message": "Frontend not found", "project_root": project_root}

@app.get('/styles')
def list_styles():
    """获取风格列表"""
    try:
        templates = TEMPLATES_DATA['templates']
        return [{
            'id': t['id'],
            'name': t['name'],
            'description': t.get('description', ''),
            'example_image': t.get('example_image', ''),
        } for t in templates]
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"获取风格列表失败: {str(e)}"}
        )

@app.post('/generate/preview')
def generate_preview(payload: GeneratePayload):
    """生成预览"""
    try:
        templates = TEMPLATES_DATA['templates']
        target = next((t for t in templates if t['id'] == payload.style_id), None)
        if not target:
            return {'html': '<!doctype html><html><body>未找到该风格</body></html>'}

        title = payload.title
        author = payload.author or ''
        style_name = target['name']
        
        html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{style_name} - 预览</title>
  <style>
    body {{ margin:0; background:#f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }}
    .card {{ width: 720px; height: 960px; margin: 24px auto; background:#fff; display:flex; flex-direction:column; justify-content:center; align-items:center; border-radius: 8px; box-shadow:0 8px 24px rgba(0,0,0,.08); }}
    h1 {{ font-size: 48px; margin: 0 24px 12px; text-align:center; }}
    p {{ color:#666; margin: 0 24px; }}
  </style>
</head>
<body>
  <div class='card'>
    <h1>{title}</h1>
    <p>{author}</p>
    <p style='margin-top:24px;color:#999;'>风格：{style_name}</p>
  </div>
</body>
</html>"""
        return {'html': html}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"生成预览失败: {str(e)}"}
        )

@app.post('/generate/ai')
def generate_ai(payload: GeneratePayload):
    """AI 生成（暂时返回预览）"""
    return generate_preview(payload)

@app.get('/debug')
def debug_info():
    """调试信息"""
    return {
        "current_file": current_file,
        "project_root": project_root,
        "sys_path": sys.path[:3],
        "templates_count": len(TEMPLATES_DATA['templates']),
        "frontend_exists": os.path.exists(os.path.join(project_root, 'frontend', 'index.html'))
    }