#!/usr/bin/env python3
"""
生成 MechForge AI 产品展示图片
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math
from pathlib import Path


def create_chat_interface():
    """创建 AI 对话界面截图"""
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color='#1e1e1e')
    draw = ImageDraw.Draw(img)
    
    # 侧边栏
    sidebar_width = 280
    draw.rectangle([0, 0, sidebar_width, height], fill='#252526')
    
    # 侧边栏标题
    draw.text((20, 20), "MechForge AI", fill='#ffffff', font=None)
    draw.text((20, 50), "v0.5.0", fill='#808080', font=None)
    
    # 新对话按钮
    draw.rounded_rectangle([20, 90, sidebar_width-20, 130], radius=6, fill='#3b82f6')
    draw.text((sidebar_width//2 - 40, 102), "+ 新对话", fill='#ffffff', font=None)
    
    # 历史对话列表
    y = 160
    for i, title in enumerate(["悬臂梁计算", "材料选择咨询", "齿轮设计", "CAE分析"]):
        color = '#3b82f6' if i == 0 else 'transparent'
        if color != 'transparent':
            draw.rectangle([0, y, sidebar_width, y+40], fill='#37373d')
        draw.text((20, y+10), f"{title}", fill='#cccccc', font=None)
        y += 45
    
    # 主聊天区域背景
    chat_bg = '#1e1e1e'
    
    # 顶部栏
    draw.rectangle([sidebar_width, 0, width, 60], fill='#2d2d30')
    draw.text((sidebar_width+20, 20), "AI 机械助手", fill='#ffffff', font=None)
    
    # 聊天内容区域
    chat_y = 80
    
    # 用户消息 1
    user_msg1 = "计算一个长100mm的悬臂梁挠度，截面10x10mm，受力1000N"
    bubble_width = len(user_msg1) * 10 + 40
    draw.rounded_rectangle([width-bubble_width-20, chat_y, width-20, chat_y+50], 
                           radius=12, fill='#3b82f6')
    draw.text((width-bubble_width, chat_y+15), user_msg1, fill='#ffffff', font=None)
    chat_y += 70
    
    # AI 回复 1
    ai_reply1 = "我来为您计算这个悬臂梁的挠度..."
    draw.rounded_rectangle([sidebar_width+20, chat_y, sidebar_width+600, chat_y+200], 
                           radius=12, fill='#2d2d30')
    draw.text((sidebar_width+35, chat_y+15), ai_reply1, fill='#ffffff', font=None)
    
    # 工具调用框
    tool_y = chat_y + 50
    draw.rounded_rectangle([sidebar_width+35, tool_y, sidebar_width+580, tool_y+80], 
                           radius=6, fill='#1e1e1e', outline='#3b82f6', width=2)
    draw.text((sidebar_width+45, tool_y+10), "使用工具: calculate_cantilever_deflection", 
              fill='#10b981', font=None)
    draw.text((sidebar_width+45, tool_y+35), '{"length": 100, "force": 1000, "width": 10, "height": 10}', 
              fill='#808080', font=None)
    
    # 结果
    result_y = tool_y + 90
    draw.text((sidebar_width+35, result_y), "结果: 最大挠度为 0.0254 mm", fill='#ffffff', font=None)
    draw.text((sidebar_width+35, result_y+25), "计算公式: δ = FL³ / (3EI)", fill='#808080', font=None)
    
    chat_y += 220
    
    # 用户消息 2
    user_msg2 = "谢谢！这个挠度在允许范围内吗？"
    bubble_width2 = len(user_msg2) * 10 + 40
    draw.rounded_rectangle([width-bubble_width2-20, chat_y, width-20, chat_y+50], 
                           radius=12, fill='#3b82f6')
    draw.text((width-bubble_width2, chat_y+15), user_msg2, fill='#ffffff', font=None)
    
    # 输入框
    input_y = height - 80
    draw.rounded_rectangle([sidebar_width+20, input_y, width-20, height-20], 
                           radius=25, fill='#2d2d30', outline='#3b82f6', width=2)
    draw.text((sidebar_width+40, input_y+20), "输入消息...", fill='#666666', font=None)
    
    return img


def create_web_dashboard():
    """创建 Web 仪表板界面"""
    width, height = 1400, 900
    img = Image.new('RGB', (width, height), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # 顶部导航栏
    draw.rectangle([0, 0, width, 70], fill='#1e293b')
    draw.text((30, 22), "MechForge AI", fill='#3b82f6', font=None)
    
    # 导航菜单
    nav_items = ["AI对话", "知识库", "CAE工作台", "设置"]
    x = 300
    for item in nav_items:
        if item == "AI对话":
            draw.rectangle([x-10, 15, x+len(item)*20+10, 55], fill='#3b82f6', radius=8)
            draw.text((x, 25), item, fill='#ffffff', font=None)
        else:
            draw.text((x, 25), item, fill='#94a3b8', font=None)
        x += len(item) * 20 + 40
    
    # 主内容区域 - 三列布局
    col_width = (width - 80) // 3
    
    # 左列 - AI 状态
    card1_x, card1_y = 30, 100
    draw.rounded_rectangle([card1_x, card1_y, card1_x+col_width-20, card1_y+200], 
                           radius=12, fill='#1e293b')
    draw.text((card1_x+20, card1_y+20), "AI 模型状态", fill='#ffffff', font=None)
    draw.text((card1_x+20, card1_y+60), "当前模型: Qwen2.5-1.5B", fill='#10b981', font=None)
    draw.text((card1_x+20, card1_y+90), "状态: 运行中", fill='#10b981', font=None)
    draw.text((card1_x+20, card1_y+120), "响应时间: 0.8s", fill='#94a3b8', font=None)
    
    # 中列 - 知识库统计
    card2_x = card1_x + col_width
    draw.rounded_rectangle([card2_x, card1_y, card2_x+col_width-20, card1_y+200], 
                           radius=12, fill='#1e293b')
    draw.text((card2_x+20, card1_y+20), "知识库统计", fill='#ffffff', font=None)
    draw.text((card2_x+20, card1_y+60), "文档数量: 156", fill='#3b82f6', font=None)
    draw.text((card2_x+20, card1_y+90), "索引状态: 已同步", fill='#10b981', font=None)
    draw.text((card2_x+20, card1_y+120), "最后更新: 2分钟前", fill='#94a3b8', font=None)
    
    # 右列 - CAE 项目
    card3_x = card2_x + col_width
    draw.rounded_rectangle([card3_x, card1_y, card3_x+col_width-20, card1_y+200], 
                           radius=12, fill='#1e293b')
    draw.text((card3_x+20, card1_y+20), "CAE 项目", fill='#ffffff', font=None)
    draw.text((card3_x+20, card1_y+60), "活跃项目: 3", fill='#f59e0b', font=None)
    draw.text((card3_x+20, card1_y+90), "已完成: 12", fill='#10b981', font=None)
    draw.text((card3_x+20, card1_y+120), "队列中: 0", fill='#94a3b8', font=None)
    
    # 下方大区域 - 最近活动
    activity_y = 330
    draw.rounded_rectangle([30, activity_y, width-30, height-30], 
                           radius=12, fill='#1e293b')
    draw.text((50, activity_y+20), "最近活动", fill='#ffffff', font=None)
    
    # 活动列表
    activities = [
        ("刚刚", "完成 CAE 分析: 悬臂梁应力计算", "#10b981"),
        ("5分钟前", "AI 对话: 材料选择咨询", "#3b82f6"),
        ("15分钟前", "知识库: 新增 3 个文档", "#f59e0b"),
        ("1小时前", "CAE 分析: 齿轮模态分析完成", "#10b981"),
    ]
    
    y = activity_y + 60
    for time, activity, color in activities:
        draw.text((50, y), time, fill='#64748b', font=None)
        draw.text((150, y), activity, fill=color, font=None)
        y += 40
    
    return img


def create_cae_analysis_viz():
    """创建 CAE 分析可视化图"""
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((30, 20), "CAE 分析结果 - 悬臂梁应力分布", fill='#ffffff', font=None)
    draw.text((30, 50), "模型: Cantilever_Beam | 网格: 12,345 节点 | 求解器: CalculiX", 
              fill='#94a3b8', font=None)
    
    # 左侧 - 3D 模型可视化区域
    viz_x, viz_y = 30, 90
    viz_width, viz_height = 600, 550
    
    # 绘制背景网格
    for i in range(0, viz_width, 20):
        draw.line([(viz_x+i, viz_y), (viz_x+i, viz_y+viz_height)], fill='#1e293b', width=1)
    for i in range(0, viz_height, 20):
        draw.line([(viz_x, viz_y+i), (viz_x+viz_width, viz_y+i)], fill='#1e293b', width=1)
    
    # 绘制悬臂梁模型（简化为长方体）
    beam_x, beam_y = viz_x + 50, viz_y + 200
    beam_width, beam_height = 500, 80
    
    # 创建应力渐变效果
    for i in range(beam_width):
        # 应力从左（固定端）到右（自由端）递减
        stress_ratio = 1 - (i / beam_width)
        
        # 颜色映射：红(高应力) -> 黄 -> 绿(低应力)
        if stress_ratio > 0.7:
            r, g, b = 239, int(68 + (1-stress_ratio)*100), 68
        elif stress_ratio > 0.3:
            r, g, b = int(239 + (0.7-stress_ratio)*100), 158, 11
        else:
            r, g, b = 68, int(158 + (0.3-stress_ratio)*100), 68
        
        draw.rectangle([beam_x+i, beam_y, beam_x+i+1, beam_y+beam_height], 
                       fill=(r, g, b))
    
    # 绘制网格线
    for i in range(0, beam_width, 25):
        draw.line([(beam_x+i, beam_y), (beam_x+i, beam_y+beam_height)], 
                  fill='#000000', width=1)
    for i in range(0, beam_height, 20):
        draw.line([(beam_x, beam_y+i), (beam_x+beam_width, beam_y+i)], 
                  fill='#000000', width=1)
    
    # 固定端标记
    draw.rectangle([beam_x-10, beam_y-10, beam_x+5, beam_y+beam_height+10], 
                   fill='#64748b')
    draw.text((beam_x-5, beam_y+beam_height+20), "固定端", fill='#94a3b8', font=None)
    
    # 受力标记
    force_x = beam_x + beam_width
    draw.polygon([(force_x, beam_y-30), (force_x-10, beam_y-10), (force_x+10, beam_y-10)], 
                 fill='#3b82f6')
    draw.line([(force_x, beam_y-30), (force_x, beam_y)], fill='#3b82f6', width=3)
    draw.text((force_x-20, beam_y-50), "1000N", fill='#3b82f6', font=None)
    
    # 右侧 - 图例和统计
    legend_x = viz_x + viz_width + 30
    
    # 应力图例
    draw.text((legend_x, 100), "应力图例 (MPa)", fill='#ffffff', font=None)
    
    legend_y = 140
    legend_items = [
        (125.6, "#ef4444"),
        (94.2, "#f97316"),
        (62.8, "#eab308"),
        (31.4, "#84cc16"),
        (0, "#22c55e"),
    ]
    
    for value, color in legend_items:
        draw.rectangle([legend_x, legend_y, legend_x+30, legend_y+20], fill=color)
        draw.text((legend_x+40, legend_y+2), f"{value}", fill='#ffffff', font=None)
        legend_y += 30
    
    # 统计信息
    stats_y = legend_y + 40
    draw.text((legend_x, stats_y), "分析结果", fill='#ffffff', font=None)
    draw.text((legend_x, stats_y+30), "最大应力: 125.60 MPa", fill='#ef4444', font=None)
    draw.text((legend_x, stats_y+55), "最大位移: 0.0254 mm", fill='#3b82f6', font=None)
    draw.text((legend_x, stats_y+80), "安全系数: 2.4", fill='#10b981', font=None)
    
    return img


def create_feature_showcase():
    """创建产品功能展示图"""
    width, height = 1600, 900
    img = Image.new('RGB', (width, height), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # 主标题
    draw.text((width//2 - 200, 50), "MechForge AI - 机械设计师的智能工作台", 
              fill='#ffffff', font=None)
    draw.text((width//2 - 150, 90), "真正懂机械、敢说真话、能真算", 
              fill='#94a3b8', font=None)
    
    # 四个功能卡片
    card_width = 350
    card_height = 280
    gap = 40
    start_x = (width - (card_width * 4 + gap * 3)) // 2
    start_y = 180
    
    features = [
        ("AI 对话", "#3b82f6", [
            "多模型支持 (OpenAI/Anthropic/Ollama)",
            "流式响应",
            "工具调用 (MCP)",
            "对话历史"
        ]),
        ("知识库", "#8b5cf6", [
            "RAG 检索增强",
            "多格式支持",
            "原文呈现",
            "智能切分"
        ]),
        ("CAE 工作台", "#10b981", [
            "Gmsh 几何/网格",
            "CalculiX 求解",
            "PyVista 可视化",
            "3D 云图"
        ]),
        ("Web 界面", "#f59e0b", [
            "FastAPI 后端",
            "WebSocket 实时",
            "响应式设计",
            "安全认证"
        ])
    ]
    
    for i, (title, color, items) in enumerate(features):
        x = start_x + i * (card_width + gap)
        
        # 卡片背景
        draw.rounded_rectangle([x, start_y, x+card_width, start_y+card_height], 
                               radius=16, fill='#1e293b', outline=color, width=3)
        
        # 标题栏
        draw.rounded_rectangle([x, start_y, x+card_width, start_y+50], 
                               radius=16, fill=color)
        draw.text((x+card_width//2-50, start_y+15), title, fill='#ffffff', font=None)
        
        # 功能列表
        y = start_y + 70
        for item in items:
            draw.text((x+20, y), f"✓ {item}", fill='#cccccc', font=None)
            y += 35
    
    # 底部技术栈
    tech_y = height - 150
    draw.text((width//2 - 100, tech_y), "技术栈", fill='#ffffff', font=None)
    
    techs = ["Python 3.10+", "FastAPI", "Pydantic v2", "Gmsh", "CalculiX", "PyVista", "MCP"]
    tech_x = width//2 - len(techs) * 70
    for tech in techs:
        draw.rounded_rectangle([tech_x, tech_y+40, tech_x+len(tech)*12+20, tech_y+70], 
                               radius=15, fill='#334155')
        draw.text((tech_x+10, tech_y+47), tech, fill='#94a3b8', font=None)
        tech_x += len(tech) * 12 + 30
    
    return img


def main():
    """主函数"""
    print("=" * 60)
    print("MechForge AI Image Generator")
    print("=" * 60)
    print()
    
    output_dir = Path(__file__).parent
    
    images = [
        ("chat-interface.png", create_chat_interface, "AI 对话界面"),
        ("web-dashboard.png", create_web_dashboard, "Web 仪表板"),
        ("cae-analysis.png", create_cae_analysis_viz, "CAE 分析可视化"),
        ("feature-showcase.png", create_feature_showcase, "产品功能展示"),
    ]
    
    for filename, generator, description in images:
        print(f"Generating: {description}...")
        try:
            img = generator()
            output_path = output_dir / filename
            img.save(output_path, 'PNG', quality=95)
            size = output_path.stat().st_size
            print(f"  [OK] {filename} ({size:,} bytes)")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")
    
    print()
    print("=" * 60)
    print("All images generated!")
    print("=" * 60)


if __name__ == "__main__":
    main()
