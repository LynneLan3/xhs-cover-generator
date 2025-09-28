from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from pathlib import Path
from services.deepseek_service import generate_cover_html
from services.cache_service import cache_service

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_JSON = ROOT / 'templates.json'
FRONTEND_DIR = ROOT / 'frontend'

app = FastAPI(title='XHS Banner Generator API')

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class GeneratePayload(BaseModel):
    title: str
    author: str | None = ''
    style_id: str


def load_templates():
    with TEMPLATES_JSON.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data['templates']


@app.get('/')
def serve_index():
    """提供前端首页"""
    return FileResponse(FRONTEND_DIR / 'index.html')


@app.get('/styles')
def list_styles():
    templates = load_templates()
    return [{
        'id': t['id'],
        'name': t['name'],
        'description': t.get('description', ''),
        'example_image': t.get('example_image', ''),
    } for t in templates]


@app.post('/generate/preview')
def generate_preview(payload: GeneratePayload):
    templates = load_templates()
    target = next((t for t in templates if t['id'] == payload.style_id), None)
    if not target:
        return {'html': '<!doctype html><html><body>未找到该风格</body></html>'}

    # 占位：这里不接AI，输出最小可用HTML，便于前端预览
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


@app.post('/generate/ai')
def generate_ai(payload: GeneratePayload):
    templates = load_templates()
    target = next((t for t in templates if t['id'] == payload.style_id), None)
    if not target:
        return JSONResponse(status_code=404, content={
            'error': {
                'code': 'STYLE_NOT_FOUND',
                'message': '未找到该风格'
            }
        })
    try:
        html = generate_cover_html(payload.title, payload.author or '', target)
        return { 'html': html }
    except Exception as e:
        return JSONResponse(status_code=500, content={
            'error': {
                'code': 'AI_GENERATE_FAILED',
                'message': f'AI生成失败: {e}'
            }
        })


@app.get('/cache/stats')
def get_cache_stats():
    """获取缓存统计信息"""
    return cache_service.get_cache_stats()


@app.post('/cache/clear')
def clear_cache():
    """清理所有缓存"""
    cleared_count = cache_service.clear_all()
    return {'message': f'已清理 {cleared_count} 个缓存文件'}


@app.post('/cache/clear-expired')
def clear_expired_cache():
    """清理过期缓存"""
    cleared_count = cache_service.clear_expired()
    return {'message': f'已清理 {cleared_count} 个过期缓存文件'}


