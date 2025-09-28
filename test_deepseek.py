#!/usr/bin/env python3
"""
测试 DeepSeek API 连接和响应的脚本
"""
import os
import sys
import json
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from services.deepseek_service import DeepSeekClient, generate_cover_html

def test_deepseek_client():
    """测试 DeepSeek 客户端基本功能"""
    print("=== 测试 DeepSeek 客户端 ===")
    
    try:
        # 初始化客户端
        client = DeepSeekClient()
        print(f"✓ 客户端初始化成功")
        print(f"  - API Base: {client.base_url}")
        print(f"  - Model: {client.model}")
        print(f"  - API Key: {client.api_key[:10]}...")
        
        # 测试简单对话
        messages = [
            {"role": "user", "content": "请回复'测试成功'"}
        ]
        
        print("\n发送测试请求...")
        response = client.chat(messages, max_tokens=50)
        print(f"✓ API 响应成功: {response}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_template_loading():
    """测试模板文件加载"""
    print("\n=== 测试模板文件 ===")
    
    try:
        templates_file = Path(__file__).parent / 'templates.json'
        if not templates_file.exists():
            print(f"✗ 模板文件不存在: {templates_file}")
            return False
            
        with open(templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        templates = data.get('templates', [])
        print(f"✓ 模板文件加载成功，共 {len(templates)} 个模板")
        
        if templates:
            first_template = templates[0]
            print(f"  - 第一个模板: {first_template.get('name', 'Unknown')}")
            print(f"  - 模板ID: {first_template.get('id', 'Unknown')}")
            
        return True, templates
        
    except Exception as e:
        print(f"✗ 模板文件加载失败: {e}")
        return False, []

def test_cover_generation():
    """测试封面生成功能"""
    print("\n=== 测试封面生成 ===")
    
    try:
        # 加载模板
        success, templates = test_template_loading()
        if not success or not templates:
            print("✗ 无法加载模板，跳过封面生成测试")
            return False
            
        # 使用第一个模板进行测试
        template = templates[0]
        title = "测试标题"
        author = "测试作者"
        
        print(f"使用模板: {template.get('name')}")
        print(f"标题: {title}")
        print(f"作者: {author}")
        
        # 生成封面
        html_content = generate_cover_html(title, author, template)
        
        print(f"✓ 封面生成成功")
        print(f"  - HTML 长度: {len(html_content)} 字符")
        print(f"  - 前100字符: {html_content[:100]}...")
        
        # 保存测试结果
        output_file = Path(__file__).parent / 'test_output.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  - 测试结果已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ 封面生成失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试 DeepSeek 接口...")
    
    # 检查环境变量
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("✗ 错误: DEEPSEEK_API_KEY 环境变量未设置")
        print("请先设置: export DEEPSEEK_API_KEY='your-api-key'")
        return False
    
    # 运行测试
    tests = [
        ("DeepSeek 客户端", test_deepseek_client),
        ("模板文件", lambda: test_template_loading()[0]),
        ("封面生成", test_cover_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print(f"\n{'='*50}")
    print("测试总结:")
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)