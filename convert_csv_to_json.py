#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV转JSON转换脚本
将小红书封面生成提示词CSV文件转换为项目开发需要的JSON格式
"""

import csv
import json
import re
from typing import Dict, List, Any

def clean_text(text: str) -> str:
    """清理文本，移除多余的空白字符"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def extract_style_name(style_text: str) -> str:
    """从风格文本中提取风格名称"""
    if not style_text:
        return ""
    
    # 查找以#开头的风格名称
    match = re.search(r'#\s*([^#\n]+)', style_text)
    if match:
        return clean_text(match.group(1))
    return ""

def parse_requirements(requirements_text: str) -> Dict[str, str]:
    """解析基本要求文本"""
    if not requirements_text:
        return {}
    
    requirements = {}
    sections = re.split(r'\*\*([^*]+)\*\*', requirements_text)
    
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            section_name = sections[i].strip()
            section_content = sections[i + 1].strip()
            requirements[section_name] = clean_text(section_content)
    
    return requirements

def parse_style_details(style_text: str) -> Dict[str, str]:
    """解析风格详情文本"""
    if not style_text:
        return {}
    
    # 去掉首行以 # 开头的风格名描述，便于解析后续 ## 段落
    text = re.sub(r'^#.*?(?=\n##|\Z)', '', style_text, flags=re.S)

    style_details: Dict[str, str] = {}
    # 匹配形如：\n## 标题\n内容... 直到下一个 ## 或文本末尾
    for match in re.finditer(r'(^|\n)##\s*([^\n#]+)\n(.*?)(?=\n##|\Z)', text, flags=re.S):
        raw_heading = match.group(2).strip()
        body = match.group(3).strip()

        # 标题可能为 "设计风格- xxx"，将 "-" 之后的部分并入正文开头
        heading_main = raw_heading
        heading_extra = ''
        m2 = re.split(r'[\-—:：]\s*', raw_heading, maxsplit=1)
        if len(m2) == 2:
            heading_main = m2[0].strip()
            heading_extra = m2[1].strip()

        content = body
        if heading_extra:
            content = (heading_extra + "\n" + body).strip()

        # 规范常见标题名，便于后续取值
        normalized = heading_main
        if '设计风格' in heading_main:
            normalized = '设计风格'
        elif '文字排版风格' in heading_main or '排版风格' in heading_main:
            normalized = '文字排版风格'
        elif '视觉元素风格' in heading_main or '视觉元素' in heading_main:
            normalized = '视觉元素风格'

        style_details[normalized] = clean_text(content)

    return style_details

def parse_user_inputs(input_text: str) -> List[str]:
    """解析用户输入内容为字段名称列表（如：封面文案、账号名称、可选标语）"""
    if not input_text:
        return []

    inputs: List[str] = []
    for raw_line in input_text.split('\n'):
        line = raw_line.strip()
        if not line or '：' not in line:
            continue
        # 形如 "- 封面文案：[]" 或 "- 账号名称：[]"
        match = re.match(r'^-\s*([^：:]+)\s*[：:]', line)
        if match:
            field_name = match.group(1).strip()
            if field_name and field_name not in inputs:
                inputs.append(field_name)

    return inputs

def convert_csv_to_json(csv_file_path: str, json_file_path: str):
    """将CSV文件转换为JSON格式"""
    
    templates = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row_num, row in enumerate(reader, start=2):
            # 跳过空行
            if not any(row.values()):
                continue
                
            # 提取数据（保留原始换行，便于正则/分段解析）
            prompt = clean_text(row.get('提示词', '') or '')
            requirements_text = (row.get('基本要求', '') or '')
            style_text = (row.get('风格', '') or '')
            user_input_text = (row.get('用户输入内容', '') or '')
            style_name = clean_text(row.get('风格名称', ''))
            example_image = clean_text(row.get('风格示例图', ''))
            
            # 如果没有风格名称，尝试从风格文本中提取
            if not style_name and style_text:
                style_name = extract_style_name(style_text)
            
            # 解析基本要求
            requirements = parse_requirements(requirements_text)
            
            # 解析风格详情
            style_details = parse_style_details(style_text)
            
            # 解析用户输入
            user_inputs = parse_user_inputs(user_input_text)
            
            # 构建模板对象
            template = {
                "id": f"style_{row_num - 1}",
                "name": style_name or f"风格_{row_num - 1}",
                "description": style_details.get('设计风格', ''),
                "prompt_template": prompt,
                "requirements": requirements,
                "style_details": style_details,
                "user_inputs": user_inputs,
                "example_image": example_image,
                "variables": ["title", "author"],
                "category": "小红书封面",
                "priority": row_num - 1
            }
            
            templates.append(template)
    
    # 构建最终的JSON结构
    result = {
        "project_info": {
            "name": "小红书封面生成器",
            "description": "基于DeepSeek AI的小红书封面自动生成工具",
            "version": "1.0.0",
            "created_at": "2024-01-01"
        },
        "templates": templates,
        "total_templates": len(templates)
    }
    
    # 保存JSON文件
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(result, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"转换完成！")
    print(f"CSV文件: {csv_file_path}")
    print(f"JSON文件: {json_file_path}")
    print(f"共转换了 {len(templates)} 个模板")

if __name__ == "__main__":
    csv_file = "小红书封面生成提示词.csv"
    json_file = "templates.json"
    
    try:
        convert_csv_to_json(csv_file, json_file)
    except FileNotFoundError:
        print(f"错误：找不到文件 {csv_file}")
    except Exception as e:
        print(f"转换过程中出现错误：{e}")
