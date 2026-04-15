# =========================================================
# 批量：PNG → BMP → SVG（Potrace 官方支持）
#
# ✅ 适用：
#   ./font_images/page_01/点_U70B9_1.png
#   ./font_images/page_02/_SLASH__U002F_2.png
#   ...
#
# ✅ 2484 个 PNG
# ✅ OpenType + 多 glyph 前置步骤
# ✅ Potrace 只支持 BMP
# =========================================================

import cv2
import os
import re
import subprocess

# ========================================================
# 一、配置区（只改这里）
# ========================================================

PNG_ROOT_DIR = "./font_images"   # PNG 根目录
BMP_OUTPUT_DIR = "./bmp_output"   # 中间 BMP 目录
SVG_OUTPUT_DIR = "./svg_output"   # 最终 SVG 目录

# Potrace 可执行文件路径（如不在 PATH 中请写绝对路径）
POTRACE_CMD = "potrace"

# 创建输出目录
os.makedirs(BMP_OUTPUT_DIR, exist_ok=True)
os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)

# ========================================================
# 二、PNG 文件名解析（✅ 核心）
# ========================================================

PNG_PATTERN = re.compile(
    r"(.+?)_U([0-9A-F]+)_(\d)\.png"
)

def parse_png_name(fname):
    """
    从 PNG 文件名解析：
    - 安全字符
    - Unicode（十六进制）
    - 形态序号（1 / 2 / 3）

    返回：
    (char_safe, unicode_hex, index)
    """
    m = PNG_PATTERN.match(fname)
    if not m:
        return None

    char_safe, unicode_hex, idx = m.groups()
    return char_safe, unicode_hex, int(idx)

# ========================================================
# 三、PNG → BMP（✅ Potrace 前置条件）
# ========================================================

def convert_png_to_bmp(png_path, bmp_path):
    """
    将 PNG 转为 24-bit BMP
    Potrace 官方支持格式
    """
    img = cv2.imread(png_path)
    if img is None:
        raise ValueError(f"无法读取 PNG: {png_path}")

    # ✅ 保存为 24-bit BMP
    cv2.imwrite(bmp_path, img)

print("🚀 开始 PNG → BMP 转换...")

for root, _, files in os.walk(PNG_ROOT_DIR):
    for fname in files:
        if not fname.lower().endswith(".png"):
            continue

        result = parse_png_name(fname)
        if not result:
            continue

        png_path = os.path.join(root, fname)
        bmp_name = fname.replace(".png", ".bmp")
        bmp_path = os.path.join(BMP_OUTPUT_DIR, bmp_name)

        convert_png_to_bmp(png_path, bmp_path)

print("✅ PNG → BMP 完成")

# ========================================================
# 四、BMP → SVG（Potrace，批量）
# ========================================================

def convert_bmp_to_svg(bmp_path, svg_path):
    """
    使用 Potrace 将 BMP 转为 SVG
    手写体友好
    """
    subprocess.run([
        POTRACE_CMD,
        "-s",           # 输出 SVG
        bmp_path,
        "-o",
        svg_path
    ], check=True)

print("🚀 开始 BMP → SVG（Potrace）...")

for fname in os.listdir(BMP_OUTPUT_DIR):
    if not fname.lower().endswith(".bmp"):
        continue

    bmp_path = os.path.join(BMP_OUTPUT_DIR, fname)
    svg_path = os.path.join(
        SVG_OUTPUT_DIR,
        fname.replace(".bmp", ".svg")
    )

    convert_bmp_to_svg(bmp_path, svg_path)

print("✅ BMP → SVG 完成")
print("📁 SVG 输出目录:", SVG_OUTPUT_DIR)