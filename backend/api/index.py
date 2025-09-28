import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

# 导入应用实例
from backend.app import app as backend_app

# 导出应用实例
app = backend_app