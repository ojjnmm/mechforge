#!/usr/bin/env python3
"""
MechForge AI - 生成产品展示图片
使用 Pillow 创建模拟界面截图
"""

from PIL import Image, ImageDraw, ImageFont
import random
import math
from pathlib import Path


def create_chat_interface():
    """创建 AI 对话界面截图"""
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # 颜色定义
    dark_bg = (15, 23, 42)
    card_bg = (30, 41, 59)
    primary = (59, 130, 246)
    text_white = (255, 255, 255)
    text_gray = (148, 163, 184)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    # 侧边栏
    sidebar_width = 280
    draw.rectangle([0, 0, sidebar_width, height], fill=(30, 41, 59))
    
    # 侧边栏标题
    draw.text((20, 20), "MechForge AI", font=font_large, fill=text_white)
    draw.text((20, 50), "机械设计师的智能助手", font=font_small, fill=text_gray)
    
    # 新对话按钮
    draw.rectangle([20, 90, sidebar_width-20, 130], fill=primary)
    draw.text((sidebar_width//2-40, 105), "+ 新对话", font=font_medium, fill=text_white)
    
    # 历史对话列表
    history_items = [
        "悬臂梁挠度计算",
        "材料强度查询",
        "弹簧设计优化",
        "CAE 分析设置"
    ]
    y_pos = 160
    for item in history_items:
        draw.text((20, y_pos), f"• {item}", font=font_small, fill=text_gray)
        y_pos += 35
    
    # 主聊天区域背景
    draw.rectangle([sidebar_width, 0, width, height], fill=dark_bg)
    
    # 顶部标题栏
    draw.rectangle([sidebar_width, 0, width, 60], fill=card_bg)
    draw.text((sidebar_width+20, 20), "AI 助手 - 工程计算模式", font=font_large, fill=text_white)
    
    # 用户消息气泡
    chat_y = 100
    bubble_width = 200
    draw.rectangle([width-bubble_width-20, chat_y, width-20, chat_y+40], fill=(59, 130, 246))
    draw.text((width-bubble_width+10, chat_y+12), "计算悬臂梁挠度", font=font_small, fill=text_white)
    
    # AI 回复区域
    chat_y = 160
    ai_box_width = 600
    draw.rectangle([sidebar_width+20, chat_y, sidebar_width+ai_box_width, chat_y+180], fill=card_bg)
    draw.text((sidebar_width+30, chat_y+15), "我来为您计算悬臂梁的挠度...", font=font_small, fill=text_white)
    
    # 工具调用框
    tool_y = chat_y + 50
    draw.rectangle([sidebar_width+35, tool_y, sidebar_width+580, tool_y+70], fill=(15, 23, 42))
    draw.text((sidebar_width+45, tool_y+10), "工具: calculate_cantilever_deflection", font=font_small, fill=(16, 185, 129))
    draw.text((sidebar_width+45, tool_y+30), "参数: {\"length\": 100, \"force\": 1000, ...}", font=font_small, fill=text_gray)
    
    # 计算结果
    result_y = tool_y + 90
    draw.text((sidebar_width+35, result_y), "结果: 最大挠度为 0.0254 mm", font=font_small, fill=(16, 185, 129))
    draw.text((sidebar_width+35, result_y+25), "计算公式: δ = FL³ / (3EI)", font=font_small, fill=text_gray)
    
    # 第二个用户消息
    chat_y = 360
    draw.rectangle([width-bubble_width-20, chat_y, width-20, chat_y+40], fill=primary)
    draw.text((width-bubble_width+10, chat_y+12), "谢谢，请解释计算过程", font=font_small, fill=text_white)
    
    # 第二个 AI 回复
    chat_y = 420
    draw.rectangle([sidebar_width+20, chat_y, sidebar_width+ai_box_width, chat_y+120], fill=card_bg)
    explanation = """计算过程如下:
1. 惯性矩 I = b*h³/12 = 833.33 mm⁴
2. 挠度 δ = FL³/(3EI) = 0.0254 mm
3. 其中 F=1000N, L=100mm, E=210000MPa"""
    
    y_offset = 15
    for line in explanation.split('\n'):
        draw.text((sidebar_width+30, chat_y+y_offset), line, font=font_small, fill=text_white)
        y_offset += 22
    
    # 输入框
    input_y = height - 80
    draw.rectangle([sidebar_width+20, input_y, width-20, height-20], fill=card_bg)
    draw.text((sidebar_width+35, input_y+20), "输入消息...", font=font_small, fill=(100, 116, 139))
    
    # 发送按钮
    draw.rectangle([width-100, input_y+10, width-30, input_y+50], fill=primary)
    draw.text((width-80, input_y+22), "发送", font=font_small, fill=text_white)
    
    return img


def create_cae_visualization():
    """创建 CAE 分析可视化图"""
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    # 标题
    draw.text((30, 20), "CAE 分析结果 - 悬臂梁应力分布", font=font_large, fill=(255, 255, 255))
    
    # 3D 网格区域（模拟）
    mesh_area = [30, 70, 600, 550]
    draw.rectangle(mesh_area, fill=(30, 41, 59))
    
    # 绘制模拟的 3D 悬臂梁网格
    # 基座
    base_points = [(100, 500), (150, 480), (180, 520), (130, 540)]
    draw.polygon(base_points, fill=(100, 116, 139), outline=(148, 163, 184))
    
    # 梁体 - 使用颜色渐变表示应力
    beam_length = 350
    beam_height = 60
    beam_start = (180, 460)
    
    for i in range(20):
        x = beam_start[0] + (beam_length * i // 20)
        width_segment = beam_length // 20 + 1
        # 应力颜色：从蓝色（低应力）到红色（高应力）
        stress_ratio = i / 20
        if stress_ratio < 0.3:
            color = (59, 130, 246)  # 蓝色
        elif stress_ratio < 0.6:
            color = (245, 158, 11)  # 橙色
        else:
            color = (239, 68, 68)   # 红色
        
        draw.rectangle([x, beam_start[1], x + width_segment, beam_start[1] + beam_height], 
                       fill=color, outline=(0, 0, 0))
    
    # 受力箭头
    arrow_x = beam_start[0] + beam_length - 20
    draw.polygon([(arrow_x, beam_start[1] - 30), (arrow_x-10, beam_start[1] - 50), 
                  (arrow_x+10, beam_start[1] - 50)], fill=(255, 255, 255))
    draw.text((arrow_x-5, beam_start[1] - 70), "F", font=font_medium, fill=(255, 255, 255))
    
    # 固定约束符号
    draw.rectangle([80, 520, 200, 540], fill=(100, 100, 100))
    for i in range(5):
        x = 90 + i * 20
        draw.polygon([(x, 540), (x-5, 555), (x+5, 555)], fill=(150, 150, 150))
    
    # 右侧信息面板
    panel_x = 640
    draw.rectangle([panel_x, 70, width-30, 550], fill=(30, 41, 59))
    
    # 面板标题
    draw.text((panel_x+20, 90), "分析结果", font=font_medium, fill=(255, 255, 255))
    
    # 结果数据
    results = [
        ("最大应力:", "125.60 MPa"),
        ("最大位移:", "0.0254 mm"),
        ("单元数量:", "12,456"),
        ("节点数量:", "8,234"),
        ("求解时间:", "2.34 s"),
    ]
    
    y_pos = 130
    for label, value in results:
        draw.text((panel_x+20, y_pos), label, font=font_small, fill=(148, 163, 184))
        draw.text((panel_x+150, y_pos), value, font=font_small, fill=(16, 185, 129))
        y_pos += 30
    
    # 图例
    legend_y = 300
    draw.text((panel_x+20, legend_y), "应力图例", font=font_medium, fill=(255, 255, 255))
    
    legend_items = [
        ((59, 130, 246), "低应力 (0-50 MPa)"),
        ((245, 158, 11), "中应力 (50-100 MPa)"),
        ((239, 68, 68), "高应力 (>100 MPa)"),
    ]
    
    y_pos = legend_y + 35
    for color, text in legend_items:
        draw.rectangle([panel_x+20, y_pos, panel_x+50, y_pos+20], fill=color)
        draw.text((panel_x+60, y_pos+3), text, font=font_small, fill=(255, 255, 255))
        y_pos += 30
    
    # 底部按钮
    button_y = 580
    draw.rectangle([30, button_y, 150, button_y+40], fill=(59, 130, 246))
    draw.text((55, button_y+12), "导出结果", font=font_small, fill=(255, 255, 255))
    
    draw.rectangle([170, button_y, 290, button_y+40], fill=(30, 41, 59))
    draw.text((195, button_y+12), "重新分析", font=font_small, fill=(255, 255, 255))
    
    return img


def create_feature_showcase():
    """创建产品功能展示图"""
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_medium = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    # 标题
    draw.text((width//2-250, 40), "MechForge AI - 功能特性", font=font_large, fill=(255, 255, 255))
    draw.text((width//2-200, 90), "机械设计师的智能工作台", font=font_medium, fill=(148, 163, 184))
    
    # 功能卡片
    features = [
        {
            "title": "AI 对话",
            "desc": "多模型支持\n流式响应\n工具调用",
            "color": (59, 130, 246),
            "pos": (50, 150)
        },
        {
            "title": "知识库",
            "desc": "RAG 检索\n多格式支持\n原文呈现",
            "color": (16, 185, 129),
            "pos": (430, 150)
        },
        {
            "title": "CAE 分析",
            "desc": "网格划分\nFEA 求解\n3D 可视化",
            "color": (245, 158, 11),
            "pos": (810, 150)
        },
        {
            "title": "Web 界面",
            "desc": "响应式设计\n实时通信\n三模式集成",
            "color": (139, 92, 246),
            "pos": (50, 420)
        },
        {
            "title": "本地模型",
            "desc": "Ollama 支持\nGGUF 推理\n统一管理",
            "color": (6, 182, 212),
            "pos": (430, 420)
        },
        {
            "title": "MCP 协议",
            "desc": "标准化工具\n可扩展\n外部连接",
            "color": (236, 72, 153),
            "pos": (810, 420)
        },
    ]
    
    card_width = 340
    card_height = 220
    
    for feature in features:
        x, y = feature["pos"]
        color = feature["color"]
        
        # 卡片背景
        draw.rectangle([x, y, x+card_width, y+card_height], fill=(30, 41, 59))
        
        # 顶部色条
        draw.rectangle([x, y, x+card_width, y+6], fill=color)
        
        # 标题
        draw.text((x+20, y+25), feature["title"], font=font_medium, fill=(255, 255, 255))
        
        # 描述
        desc_y = y + 65
        for line in feature["desc"].split('\n'):
            draw.text((x+20, desc_y), f"✓ {line}", font=font_small, fill=(148, 163, 184))
            desc_y += 28
    
    # 底部特性
    bottom_y = 680
    techs = ["Python 3.10+", "FastAPI", "Pydantic v2", "MCP", "WebSocket"]
    tech_x = 100
    for tech in techs:
        draw.rectangle([tech_x, bottom_y, tech_x+len(tech)*12+20, bottom_y+30], fill=(30, 41, 59))
        draw.text((tech_x+10, bottom_y+7), tech, font=font_small, fill=(255, 255, 255))
        tech_x += len(tech)*12 + 40
    
    # 底部标语
    draw.text((width//2-200, 750), "Made with ❤️ for Mechanical Engineers", 
              font=font_small, fill=(100, 116, 139))
    
    return img


def main():
    """主函数"""
    print("=" * 60)
    print("MechForge AI Image Generator")
    print("=" * 60)
    print()
    
    output_dir = Path(__file__).parent
    
    images_to_generate = [
        ("chat-interface.png", create_chat_interface, "AI 对话界面"),
        ("cae-analysis.png", create_cae_visualization, "CAE 分析可视化"),
        ("feature-showcase.png", create_feature_showcase, "产品功能展示"),
    ]
    
    for filename, generator_func, description in images_to_generate:
        print(f"Generating: {description}...")
        try:
            img = generator_func()
            output_path = output_dir / filename
            img.save(output_path, 'PNG')
            size = output_path.stat().st_size
            print(f"  [OK] {filename} ({size:,} bytes)")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")
    
    print()
    print("=" * 60)
    print("All images generated!")
    print("=" * 60)
    print()
    
    # 列出生成的文件
    png_files = sorted(output_dir.glob("*.png"))
    if png_files:
        print(f"Generated {len(png_files)} files:")
        for f in png_files:
            size = f.stat().st_size
            print(f"  - {f.name:30} ({size:>8,} bytes)")


if __name__ == "__main__":
    main()
