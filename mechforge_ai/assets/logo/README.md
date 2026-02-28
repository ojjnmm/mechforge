# MechForge AI - Brand Assets

MechForge AI 品牌标识和标志资源

---

## 标志文件

### SVG 矢量文件（推荐）

| 文件 | 说明 | 用途 |
|------|------|------|
| `mechforge-logo.svg` | 完整版标志 (512x512) | 大尺寸展示、印刷 |
| `mechforge-logo-simple.svg` | 简化版标志 (256x256) | App 图标、小尺寸 |
| `mechforge-logo-with-text.svg` | 带文字的标志 (800x300) | 网站头部、文档 |

### PNG 位图文件

#### 主标志

| 文件 | 尺寸 | 用途 |
|------|------|------|
| `mechforge-logo-512.png` | 512x512 | 高分辨率展示 |
| `mechforge-logo-256.png` | 256x256 | 通用尺寸 |
| `mechforge-logo-128.png` | 128x128 | 中等尺寸 |
| `mechforge-logo-64.png` | 64x64 | 小图标 |
| `mechforge-logo-32.png` | 32x32 | 超小图标 |

#### 简化版标志

| 文件 | 尺寸 | 用途 |
|------|------|------|
| `mechforge-logo-simple-256.png` | 256x256 | App 图标 |
| `mechforge-logo-simple-128.png` | 128x128 | 工具栏图标 |
| `mechforge-logo-simple-64.png` | 64x64 | 列表图标 |
| `mechforge-logo-simple-48.png` | 48x48 | 按钮图标 |
| `mechforge-logo-simple-32.png` | 32x32 | 小按钮 |

#### Favicon

| 文件 | 尺寸 | 用途 |
|------|------|------|
| `favicon.ico` | 多尺寸 | 网站 favicon |
| `favicon-16.png` | 16x16 | 浏览器标签 |
| `favicon-32.png` | 32x32 | 浏览器标签 (Retina) |
| `favicon-48.png` | 48x48 | Windows 任务栏 |
| `apple-touch-icon.png` | 180x180 | iOS 主屏幕图标 |

---

## 颜色方案

### 主色调

| 颜色 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Primary Blue | `#3B82F6` | rgb(59, 130, 246) | 主色、齿轮外圈 |
| Indigo | `#6366F1` | rgb(99, 102, 241) | 过渡色 |
| Purple | `#8B5CF6` | rgb(139, 92, 246) | 强调色 |

### 辅助色

| 颜色 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Emerald | `#10B981` | rgb(16, 185, 129) | AI 核心、成功状态 |
| Cyan | `#06B6D4` | rgb(6, 182, 212) | 科技感、信息状态 |
| Orange | `#F59E0B` | rgb(245, 158, 11) | 节点、警告状态 |
| Red | `#EF4444` | rgb(239, 68, 68) | 对角节点、错误状态 |

### 背景色

| 颜色 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Dark BG | `#0F172A` | rgb(15, 23, 42) | 深色背景 |
| Card BG | `#1E293B` | rgb(30, 41, 59) | 卡片背景 |

---

## 设计概念

### 标志含义

1. **外圈齿轮** (12齿)
   - 代表机械工程和精密制造
   - 体现 MechForge 的核心定位

2. **内圈齿轮** (8齿)
   - 代表工程的精确性和结构化
   - 与外圈形成层次感

3. **中心 AI 核心**
   - 电路图案象征人工智能
   - 节点和连接线代表神经网络
   - 渐变色彩体现科技感

4. **颜色渐变**
   - 蓝色到紫色：创新与技术的融合
   - 绿色到青色：AI 与工程的结合

---

## 使用指南

### 正确用法

✅ **应该这样做：**
- 使用 SVG 版本以保持清晰度
- 保持标志周围有足够的留白空间
- 在深色背景上使用标志
- 使用品牌配色方案

### 错误用法

❌ **不应该这样做：**
- 拉伸或压缩标志
- 改变标志的颜色
- 旋转标志
- 添加阴影或效果（已内置）
- 在复杂背景上使用

### 留白空间

在标志周围保持至少 10% 的留白空间：

```
+----------------------------------+
|          留白空间 (10%)          |
|    +------------------------+    |
|    |                        |    |
|    |        标志            |    |
|    |                        |    |
|    +------------------------+    |
|          留白空间 (10%)          |
+----------------------------------+
```

---

## 应用场景

### App 图标
- 使用：`mechforge-logo-simple-256.png`
- 平台：Windows, macOS, Linux
- 尺寸：256x256 (会自动缩放)

### 网站 Favicon
- 使用：`favicon.ico`
- 位置：网站根目录
- HTML：`<link rel="icon" href="/favicon.ico">`

### Apple Touch Icon
- 使用：`apple-touch-icon.png`
- HTML：`<link rel="apple-touch-icon" href="/apple-touch-icon.png">`

### 社交媒体
- 头像：`mechforge-logo-512.png`
- 封面：使用带文字的 SVG 版本

### 文档和演示
- 使用：`mechforge-logo-with-text.svg`
- 格式：SVG 保持清晰度

---

## 生成新尺寸

如果需要其他尺寸的标志，可以运行：

```bash
cd assets/logo
python create_png_logo.py
```

这将重新生成所有 PNG 文件。

---

## 预览

在浏览器中打开 `preview.html` 查看标志预览和使用指南。

---

## 许可证

MechForge AI 标志版权归项目所有者所有。

使用本项目标志需遵循项目许可证条款。

---

**MechForge AI** - Made with ❤️ for Mechanical Engineers
