# =========================================================
# 生成 layout.txt（显式字符映射版）
#
# ✅ page,row,col,char,rows,cols,direction
# ✅ 12×12 / 页，最后一页 3×12
# ✅ 一个字符 3 个大方格
# ✅ 特殊字符使用占位符：COMMA, QUOTE 等
# =========================================================

import os
import math
import csv

# ========================================================
# 一、配置区（只改这里）
# ========================================================

TXT_DIR = "./output_txt"
TXT_FILES = [
    "chinese.txt",
    "english.txt",
    "numbers.txt",
    "others.txt"
]

SCAN_DIR = "./scans"
SCAN_PREFIX = "handwriting"

LAYOUT_OUT = "layout.txt"

ROWS_FULL = 12     # 正常页行数
ROWS_LAST = 3      # 最后一页行数
COLS = 12          # 每页列数（大方格）
GROUP_SIZE = 3      # 每个字符占 3 列

# ========================================================
# 二、特殊字符映射（✅ 核心）
# ========================================================

CHAR_MAP = {
    ",": "COMMA",
    '"': "QUOTE",
    "/": "SLASH",
    "\\": "BACKSLASH",
    ":": "COLON",
    "*": "STAR",
    "?": "Q",
    "<": "LT",
    ">": "GT",
    "|": "PIPE"
}

# ========================================================
# 三、读取所有 TXT（顺序 = 最终字符顺序）
# ========================================================

def read_all_chars(txt_dir, txt_files):
    chars = []
    for fname in txt_files:
        path = os.path.join(txt_dir, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                chars.extend(list(f.read().strip()))
    return chars

all_chars = read_all_chars(TXT_DIR, TXT_FILES)

# ========================================================
# 四、统计扫描页数
# ========================================================

def count_scan_pages(scan_dir, prefix):
    return len([
        f for f in os.listdir(scan_dir)
        if f.startswith(prefix) and f.lower().endswith(".png")
    ])

total_pages = count_scan_pages(SCAN_DIR, SCAN_PREFIX)

# ========================================================
# 五、生成 layout.txt（✅ 显式字符）
# ========================================================

with open(LAYOUT_OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["page", "row", "col", "char", "rows", "cols", "direction"])

    char_idx = 0
    chars_per_page = (ROWS_FULL * COLS) // GROUP_SIZE

    for page in range(1, total_pages + 1):

        if page == total_pages:
            remaining = len(all_chars) - char_idx
            rows = math.ceil(remaining / (COLS // GROUP_SIZE))
        else:
            rows = ROWS_FULL

        for row in range(1, rows + 1):
            for group in range(COLS // GROUP_SIZE):
                if char_idx >= len(all_chars):
                    break

                ch = all_chars[char_idx]
                char_idx += 1

                # ✅ 使用显式占位符
                ch_mapped = CHAR_MAP.get(ch, ch)

                for i in range(GROUP_SIZE):
                    col = group * GROUP_SIZE + i + 1
                    writer.writerow([
                        page,
                        row,
                        col,
                        ch_mapped,
                        rows,
                        COLS,
                        "LTR"
                    ])

print("✅ layout.txt 已生成（显式字符映射版）")
print(f"总字符数: {char_idx}")
print(f"总页数: {total_pages}")