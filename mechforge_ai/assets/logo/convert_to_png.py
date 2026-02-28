#!/usr/bin/env python3
"""
将 SVG 标志转换为 PNG 格式
需要安装: pip install cairosvg pillow
"""

import subprocess
import sys
from pathlib import Path


def check_cairosvg():
    """检查是否安装了 cairosvg"""
    try:
        import cairosvg
        return True
    except ImportError:
        return False


def convert_with_cairosvg(svg_path: Path, png_path: Path, size: int):
    """使用 CairoSVG 转换"""
    import cairosvg
    
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=size,
        output_height=size
    )
    print(f"  ✓ {png_path.name} ({size}x{size})")


def convert_with_inkscape(svg_path: Path, png_path: Path, size: int):
    """使用 Inkscape 转换"""
    cmd = [
        "inkscape",
        str(svg_path),
        "--export-type=png",
        f"--export-filename={png_path}",
        f"--export-width={size}",
        f"--export-height={size}",
        "--export-background-opacity=0"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  ✓ {png_path.name} ({size}x{size})")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to convert {svg_path.name}: {e}")
    except FileNotFoundError:
        print(f"  ✗ Inkscape not found")


def create_placeholder_png(png_path: Path, size: int, label: str):
    """创建占位符 PNG（当转换工具不可用时）"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建透明背景图像
        img = Image.new('RGBA', (size, size), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(59, 130, 246, 255),
            outline=(99, 102, 241, 255),
            width=4
        )
        
        # 绘制内圆
        inner_margin = size // 4
        draw.ellipse(
            [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
            fill=(16, 185, 129, 255)
        )
        
        # 尝试添加文字
        try:
            font_size = size // 8
            font = ImageFont.truetype("arial.ttf", font_size)
            text = "MF"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        except:
            pass
        
        img.save(png_path)
        print(f"  ✓ {png_path.name} ({size}x{size}) - Placeholder")
        
    except ImportError:
        print(f"  ✗ PIL not available, cannot create placeholder")


def main():
    """主函数"""
    print("=" * 60)
    print("MechForge AI Logo Converter")
    print("=" * 60)
    print()
    
    # 检查可用工具
    has_cairosvg = check_cairosvg()
    
    if has_cairosvg:
        print("Using: CairoSVG")
    else:
        print("CairoSVG not found, trying Inkscape...")
    
    print()
    
    # 定义转换任务
    logo_dir = Path(__file__).parent
    
    conversions = [
        {
            "svg": logo_dir / "mechforge-logo.svg",
            "base_name": "mechforge-logo",
            "sizes": [512, 256, 128, 64, 32, 16]
        },
        {
            "svg": logo_dir / "mechforge-logo-simple.svg",
            "base_name": "mechforge-logo-simple",
            "sizes": [256, 128, 64, 48, 32, 16]
        }
    ]
    
    # 执行转换
    for task in conversions:
        svg_path = task["svg"]
        base_name = task["base_name"]
        
        if not svg_path.exists():
            print(f"⚠️  {svg_path.name} not found, skipping...")
            continue
        
        print(f"\n🎨 Converting {svg_path.name}...")
        
        for size in task["sizes"]:
            png_path = logo_dir / f"{base_name}-{size}.png"
            
            if has_cairosvg:
                try:
                    convert_with_cairosvg(svg_path, png_path, size)
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    create_placeholder_png(png_path, size, base_name)
            else:
                convert_with_inkscape(svg_path, png_path, size)
    
    # 转换带文字版本
    svg_with_text = logo_dir / "mechforge-logo-with-text.svg"
    if svg_with_text.exists():
        print(f"\n🎨 Converting {svg_with_text.name}...")
        
        for width in [800, 400, 200]:
            png_path = logo_dir / f"mechforge-logo-with-text-{width}.png"
            
            if has_cairosvg:
                try:
                    import cairosvg
                    cairosvg.svg2png(
                        url=str(svg_with_text),
                        write_to=str(png_path),
                        output_width=width
                    )
                    print(f"  ✓ {png_path.name} ({width}px width)")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("Conversion complete!")
    print("=" * 60)
    print()
    print("Generated files:")
    
    # 列出生成的文件
    png_files = sorted(logo_dir.glob("*.png"))
    if png_files:
        for f in png_files:
            size = f.stat().st_size
            print(f"  📄 {f.name} ({size:,} bytes)")
    else:
        print("  No PNG files generated")
    
    print()
    print("💡 To install CairoSVG:")
    print("   pip install cairosvg")


if __name__ == "__main__":
    main()
