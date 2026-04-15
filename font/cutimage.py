# =========================================================
# 最终版：LTR + 行分组 + 行内排序 + 安全文件名
#
# ✅ page,row,col,char,rows,cols,direction
# ✅ 12×12 / 页，最后一页 3×12
# ✅ 一个字符 3 个大方格
# ✅ 特殊符号安全
# ✅ 特殊符号不再重复
# ✅ 不点角 / 不透视
# ✅ cut image 按扫描页面分文件夹存放
# =========================================================

import cv2
import numpy as np
import os
import re
import unicodedata

# ========================================================
# 一、配置区（只改这里）
# ========================================================

SCAN_DIR = "./scans"           # 扫描图目录
LAYOUT_PATH = "layout.txt"      # layout.txt
OUTPUT_BASE_DIR = "./font_images"  # 输出根目录

SCAN_PREFIX = "handwriting"

# 裁剪内边距（去掉边框）
PADDING = 25

# 大方框最小面积（过滤小方框）
MIN_BOX_AREA = 5000

# 正方形容忍度
ASPECT_TOL = 0.2

# 行分组 y 轴容差
Y_TOL = 15

# 创建输出根目录
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# ✅ 二、显式字符映射（新增）
# ========================================================

CHAR_MAP = {
    "COMMA": ",",
    "QUOTE": '"',
    "SLASH": "/",
    "BACKSLASH": "\\",
    "COLON": ":",
    "STAR": "*",
    "Q": "?",
    "LT": "<",
    "GT": ">",
    "PIPE": "|"
}

# ========================================================
# 二、自然排序扫描文件
# ========================================================

def natural_sort_key(s):
    """
    让 handwriting.01.png 正确排序
    """
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', s)]

scan_files = sorted(
    [f for f in os.listdir(SCAN_DIR) if f.lower().endswith(".png")],
    key=natural_sort_key
)

# ========================================================
# 三、读取 layout.txt（LTR）
# ========================================================

def read_layout(path):
    """
    返回：
    {
        page: [
            (row, col, char, rows, cols, direction)
        ]
    }
    """
    layout = {}
    with open(path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != 7:
                continue
            page, row, col, ch, rows, cols, direction = parts

            # ✅ 显式映射（新增）
            ch = CHAR_MAP.get(ch, ch)

            layout.setdefault(int(page), []).append(
                (int(row), int(col), ch, int(rows), int(cols), direction)
            )
    return layout

layout = read_layout(LAYOUT_PATH)

# ========================================================
# 四、安全文件名（✅ 关键）
# ========================================================

def safe_filename(char):
    char = unicodedata.normalize("NFKC", char)
    replacements = {
        ",": "_COMMA_",
        '"': "_QUOTE_",
        "/": "_SLASH_",
        "\\": "_BACKSLASH_",
        ":": "_COLON_",
        "*": "_STAR_",
        "?": "_Q_",
        "<": "_LT_",
        ">": "_GT_",
        "|": "_PIPE_"
    }
    for bad, good in replacements.items():
        char = char.replace(bad, good)
    return char

# ========================================================
# 五、检测大方框
# ========================================================

def detect_large_boxes(image):
    """
    检测图像中的大方框（四边形 + 面积大）
    返回：(x, y, w, h)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(
        gray, 200, 255, cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_BOX_AREA:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        if abs(w - h) / max(w, h) > ASPECT_TOL:
            continue

        boxes.append((x, y, w, h))

    # 按 y → x 排序（从上到下，从左到右）
    boxes.sort(key=lambda b: (b[1], b[0]))
    return boxes

# ========================================================
# 六、按“行分组 + 行内排序”（✅ 不乱序）
# ========================================================

def group_boxes_by_row(boxes, rows, cols, y_tol=Y_TOL):
    """
    按 y 坐标分组为行
    行内按 x 排序
    """
    boxes = sorted(boxes, key=lambda b: b[1])

    row_boxes = [[] for _ in range(rows)]

    for b in boxes:
        x, y, w, h = b
        placed = False

        for r in range(rows):
            if not row_boxes[r]:
                row_boxes[r].append(b)
                placed = True
                break

            _, y_ref, _, _ = row_boxes[r][0]
            if abs(y - y_ref) < y_tol:
                row_boxes[r].append(b)
                placed = True
                break

        if not placed:
            dists = [
                abs(y - row_boxes[r][0][1])
                for r in range(rows) if row_boxes[r]
            ]
            if dists:
                r = np.argmin(dists)
                row_boxes[r].append(b)

    # 行内按 x 排序
    for r in range(rows):
        row_boxes[r].sort(key=lambda b: b[0])

    return row_boxes

# ========================================================
# 七、裁剪字体区域（不含边框）
# ========================================================

def crop_char(image, box, padding):
    x, y, w, h = box

    inner_x = max(0, x + padding)
    inner_y = max(0, y + padding)
    inner_w = min(w - 2 * padding, image.shape[1] - inner_x)
    inner_h = min(h - 2 * padding, image.shape[0] - inner_y)

    if inner_w <= 0 or inner_h <= 0:
        return None

    return image[
        inner_y:inner_y + inner_h,
        inner_x:inner_x + inner_w
    ]

# ========================================================
# 八、主程序（✅ 按扫描页分文件夹）
# ========================================================

char_counter = {}  # key = ord(ch)

for page_idx, fname in enumerate(scan_files, start=1):
    img_path = os.path.join(SCAN_DIR, fname)
    img = cv2.imread(img_path)

    if img is None:
        print(f"⚠️ 无法读取: {fname}")
        continue

    boxes = detect_large_boxes(img)
    print(f"📄 {fname}: 检测到 {len(boxes)} 个大方框")

    if page_idx not in layout:
        continue

    # ✅ 为当前扫描页创建独立输出目录
    page_dir = os.path.join(
        OUTPUT_BASE_DIR,
        f"page_{page_idx:02d}"
    )
    os.makedirs(page_dir, exist_ok=True)

    for row, col, ch, rows, cols, direction in layout[page_idx]:

        if direction != "LTR":
            continue

        row_boxes = group_boxes_by_row(boxes, rows, cols)

        if row - 1 >= len(row_boxes):
            continue
        if col - 1 >= len(row_boxes[row - 1]):
            continue

        box = row_boxes[row - 1][col - 1]
        char_img = crop_char(img, box, PADDING)

        if char_img is None:
            continue

        # ✅ 用 Unicode 码点作为唯一 key（解决特殊符号重复）
        key = ord(ch)
        char_counter[key] = char_counter.get(key, 0) + 1

        # ✅ 安全文件名
        safe_ch = safe_filename(ch)
        safe_name = (
            f"{safe_ch}_U{key:04X}_"
            f"{char_counter[key]}.png"
        )

        cv2.imwrite(
            os.path.join(page_dir, safe_name),
            char_img
        )
        print(f"✅ 保存: {page_dir}/{safe_name}")

print("\n🎉 所有扫描图处理完成")
print("📁 输出根目录:", OUTPUT_BASE_DIR)