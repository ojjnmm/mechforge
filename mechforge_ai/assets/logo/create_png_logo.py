#!/usr/bin/env python3
"""
使用 Pillow 创建 MechForge AI 的 PNG 标志
"""

from PIL import Image, ImageDraw, ImageFont
import math
from pathlib import Path


def create_gear_path(center_x, center_y, outer_radius, inner_radius, teeth):
    """创建齿轮路径点"""
    points = []
    angle_step = 2 * math.pi / teeth
    
    for i in range(teeth):
        angle = i * angle_step
        
        # 齿顶外边缘
        x1 = center_x + outer_radius * math.cos(angle - angle_step * 0.15)
        y1 = center_y + outer_radius * math.sin(angle - angle_step * 0.15)
        points.append((x1, y1))
        
        # 齿顶
        x2 = center_x + outer_radius * math.cos(angle)
        y2 = center_y + outer_radius * math.sin(angle)
        points.append((x2, y2))
        
        # 齿顶外边缘（另一侧）
        x3 = center_x + outer_radius * math.cos(angle + angle_step * 0.15)
        y3 = center_y + outer_radius * math.sin(angle + angle_step * 0.15)
        points.append((x3, y3))
        
        # 齿根
        x4 = center_x + inner_radius * math.cos(angle + angle_step * 0.35)
        y4 = center_y + inner_radius * math.sin(angle + angle_step * 0.35)
        points.append((x4, y4))
        
        # 齿根中心
        x5 = center_x + inner_radius * math.cos(angle + angle_step * 0.5)
        y5 = center_y + inner_radius * math.sin(angle + angle_step * 0.5)
        points.append((x5, y5))
    
    return points


def draw_gradient_circle(draw, center, radius, color1, color2):
    """绘制渐变圆形（模拟）"""
    for r in range(radius, 0, -1):
        ratio = r / radius
        r_color = int(color1[0] * ratio + color2[0] * (1 - ratio))
        g_color = int(color1[1] * ratio + color2[1] * (1 - ratio))
        b_color = int(color1[2] * ratio + color2[2] * (1 - ratio))
        draw.ellipse(
            [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
            fill=(r_color, g_color, b_color)
        )


def create_logo(size):
    """创建指定尺寸的标志"""
    # 创建透明背景
    img = Image.new('RGBA', (size, size), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # 颜色定义
    blue = (59, 130, 246)
    indigo = (99, 102, 241)
    purple = (139, 92, 246)
    emerald = (16, 185, 129)
    cyan = (6, 182, 212)
    white = (255, 255, 255)
    dark_bg = (15, 23, 42)
    
    # 外齿轮
    outer_radius = int(size * 0.42)
    inner_radius = int(size * 0.32)
    gear_points = create_gear_path(center, center, outer_radius, inner_radius, 12)
    
    # 绘制齿轮渐变效果
    for i, radius in enumerate(range(outer_radius, inner_radius, -2)):
        ratio = (radius - inner_radius) / (outer_radius - inner_radius)
        r = int(blue[0] * (1 - ratio) + purple[0] * ratio)
        g = int(blue[1] * (1 - ratio) + purple[1] * ratio)
        b = int(blue[2] * (1 - ratio) + purple[2] * ratio)
        
        gear_pts = create_gear_path(center, center, radius, radius - 2, 12)
        if len(gear_pts) >= 3:
            draw.polygon(gear_pts, fill=(r, g, b))
    
    # 内圆背景
    inner_circle_radius = int(size * 0.28)
    draw.ellipse(
        [center - inner_circle_radius, center - inner_circle_radius,
         center + inner_circle_radius, center + inner_circle_radius],
        fill=dark_bg
    )
    
    # 中心圆（渐变效果）
    center_radius = int(size * 0.22)
    for r in range(center_radius, 0, -1):
        ratio = r / center_radius
        rc = int(emerald[0] * ratio + cyan[0] * (1 - ratio))
        gc = int(emerald[1] * ratio + cyan[1] * (1 - ratio))
        bc = int(emerald[2] * ratio + cyan[2] * (1 - ratio))
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(rc, gc, bc)
        )
    
    # 中心白点
    center_dot = int(size * 0.06)
    draw.ellipse(
        [center - center_dot, center - center_dot,
         center + center_dot, center + center_dot],
        fill=white
    )
    
    # 外围节点
    node_distance = int(size * 0.14)
    node_radius = int(size * 0.025)
    node_color = (245, 158, 11)  # 橙色
    
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        nx = center + node_distance * math.cos(angle)
        ny = center + node_distance * math.sin(angle)
        draw.ellipse(
            [nx - node_radius, ny - node_radius,
             nx + node_radius, ny + node_radius],
            fill=node_color
        )
        # 连接线
        line_start = center + center_dot * math.cos(angle)
        line_end = center + (node_distance - node_radius) * math.cos(angle)
        line_start_y = center + center_dot * math.sin(angle)
        line_end_y = center + (node_distance - node_radius) * math.sin(angle)
        draw.line(
            [(line_start, line_start_y), (line_end, line_end_y)],
            fill=white,
            width=max(2, size // 128)
        )
    
    # 对角节点
    diag_distance = int(size * 0.10)
    diag_radius = int(size * 0.02)
    diag_color = (239, 68, 68)  # 红色
    
    for angle in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        nx = center + diag_distance * math.cos(angle)
        ny = center + diag_distance * math.sin(angle)
        draw.ellipse(
            [nx - diag_radius, ny - diag_radius,
             nx + diag_radius, ny + diag_radius],
            fill=diag_color
        )
    
    return img


def create_simple_logo(size):
    """创建简化版标志（方形圆角背景）"""
    # 创建方形图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 圆角矩形背景
    corner_radius = size // 8
    bg_color = (15, 23, 42)
    
    # 绘制圆角矩形
    draw.rounded_rectangle(
        [0, 0, size, size],
        radius=corner_radius,
        fill=bg_color
    )
    
    # 在内部绘制齿轮标志
    logo_size = int(size * 0.7)
    logo = create_logo(logo_size)
    offset = (size - logo_size) // 2
    img.paste(logo, (offset, offset), logo)
    
    return img


def create_favicon_sizes():
    """创建 favicon 所需的各种尺寸"""
    sizes = [16, 32, 48, 64, 128, 256]
    logo_dir = Path(__file__).parent
    
    print("\nCreating favicon sizes...")
    
    for size in sizes:
        img = create_simple_logo(size)
        output_path = logo_dir / f"favicon-{size}.png"
        img.save(output_path, 'PNG')
        print(f"  [OK] favicon-{size}.png")
    
    # 创建 ICO 文件（包含多个尺寸）
    try:
        ico_sizes = [16, 32, 48, 256]
        ico_images = [create_simple_logo(s) for s in ico_sizes]
        ico_path = logo_dir / "favicon.ico"
        ico_images[0].save(
            ico_path,
            format='ICO',
            sizes=[(s, s) for s in ico_sizes],
            append_images=ico_images[1:]
        )
        print(f"  [OK] favicon.ico (multi-size)")
    except Exception as e:
        print(f"  [WARN] Could not create favicon.ico: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("MechForge AI Logo Generator")
    print("=" * 60)
    print()
    
    logo_dir = Path(__file__).parent
    
    # 创建主标志的各种尺寸
    main_sizes = [512, 256, 128, 64, 32]
    print("Creating main logo sizes...")
    
    for size in main_sizes:
        img = create_logo(size)
        output_path = logo_dir / f"mechforge-logo-{size}.png"
        img.save(output_path, 'PNG')
        print(f"  [OK] mechforge-logo-{size}.png")
    
    # 创建简化版标志
    simple_sizes = [256, 128, 64, 48, 32]
    print("\nCreating simple logo sizes...")
    
    for size in simple_sizes:
        img = create_simple_logo(size)
        output_path = logo_dir / f"mechforge-logo-simple-{size}.png"
        img.save(output_path, 'PNG')
        print(f"  [OK] mechforge-logo-simple-{size}.png")
    
    # 创建 favicon
    create_favicon_sizes()
    
    # 创建 Apple Touch Icon
    print("\nCreating Apple Touch Icon...")
    apple_icon = create_simple_logo(180)
    apple_icon.save(logo_dir / "apple-touch-icon.png", 'PNG')
    print("  [OK] apple-touch-icon.png (180x180)")
    
    print()
    print("=" * 60)
    print("All logos generated successfully!")
    print("=" * 60)
    print()
    
    # 列出生成的文件
    png_files = sorted(logo_dir.glob("*.png"))
    ico_files = list(logo_dir.glob("*.ico"))
    all_files = png_files + ico_files
    
    if all_files:
        print(f"Generated {len(all_files)} files:")
        for f in all_files:
            size = f.stat().st_size
            print(f"  - {f.name:35} ({size:>8,} bytes)")
    
    print()
    print("Usage:")
    print("   - mechforge-logo-512.png    -> App icon, high-res")
    print("   - mechforge-logo-256.png    -> General use")
    print("   - mechforge-logo-64.png     -> Small UI elements")
    print("   - mechforge-logo-simple-*.png -> Simplified versions")
    print("   - favicon.ico               -> Website favicon")
    print("   - apple-touch-icon.png      -> iOS home screen icon")


if __name__ == "__main__":
    main()
