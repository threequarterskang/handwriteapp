# =========================================================
# 最终诊断：font_image 与 layout.txt 一致性检查
#
# ✅ 找出：layout 有，但 font_image 没有的字
# ✅ 使用同一套 safe_filename()
# ✅ 不再解析文件名
# ✅ 不再正则猜测
# =========================================================

import os
import unicodedata

# ========================================================
# 一、配置区（只改这里）
# ========================================================

LAYOUT_PATH = "layout.txt"
FONT_DIR = "./font_images"

# ========================================================
# 二、安全文件名（✅ 与切图脚本完全一致）
# ========================================================

def safe_filename(char):
    """
    与切图脚本 100% 一致的转换规则
    """
    char = unicodedata.normalize("NFKC", char)

    replacements = {
        "/": "_SLASH_",
        "\\": "_BACKSLASH_",
        ":": "_COLON_",
        "*": "_STAR_",
        "?": "_Q_",
        '"': "_QUOTE_",
        "<": "_LT_",
        ">": "_GT_",
        "|": "_PIPE_"
    }

    for bad, good in replacements.items():
        char = char.replace(bad, good)

    return char

# ========================================================
# 三、读取 layout.txt
# ========================================================

def read_layout(path):
    """
    返回：
    {
        (page, row, col): char
    }
    """
    layout = {}
    with open(path, "r", encoding="utf-8") as f:
        next(f)  # 跳过表头
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 7:
                continue
            page, row, col, ch, *_ = parts
            layout[(int(page), int(row), int(col))] = ch
    return layout

# ========================================================
# 四、读取 font_image 中的所有文件名
# ========================================================

def read_font_image_files(font_dir):
    """
    返回：set(所有 png 文件名)
    """
    return set(os.listdir(font_dir))

# ========================================================
# 五、✅ 核心诊断逻辑（终局）
# ========================================================

def find_missing(layout, font_files):
    """
    找出 layout 有，但 font_image 没有的字
    """
    missing = []

    for (page, row, col), ch in layout.items():
        safe_ch = safe_filename(ch)

        # 构造“前缀”
        prefix = f"{safe_ch}_U{ord(ch):04X}_"

        # 检查是否存在以该前缀开头的文件
        found = any(
            fname.startswith(prefix)
            for fname in font_files
        )

        if not found:
            missing.append((page, row, col, ch))

    return missing

# ========================================================
# 六、主程序（✅ 最终）
# ========================================================

layout = read_layout(LAYOUT_PATH)
font_files = read_font_image_files(FONT_DIR)

missing = find_missing(layout, font_files)

print("🎯 诊断完成")
print(f"✅ layout 字符位置数: {len(layout)}")
print(f"✅ font_image 文件数: {len(font_files)}")
print(f"❌ 缺失字符数: {len(missing)}\n")

for page, row, col, ch in missing:
    print(f"  page={page}, row={row}, col={col}, char={repr(ch)}")