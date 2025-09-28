import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.app import app

# 确保模板文件存在
templates_json = root_dir / 'templates.json'
if not templates_json.exists():
    raise FileNotFoundError(f'templates.json not found at {templates_json}')