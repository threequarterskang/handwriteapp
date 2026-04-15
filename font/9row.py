# =========================================================
# 手写字体采集表（12 行 · 行距更紧）
#
# ✅ 字体：./SimSun.ttf
# ✅ 中文 100%
# ✅ 12 行
# ✅ 顶部更紧
# ✅ 行与行更紧（上一格 ↔ 下一字）
# =========================================================

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# ========================================================
# 一、配置区
# ========================================================

TXT_DIR = "./output_txt"
OUTPUT_PDF = "./handwriting_sheet_12rows_row_tight.pdf"
FONT_PATH = "./SimSun.ttf"

ROWS = 12
BOX_SIZE = 11
BOX_GAP = 4
TEXT_TO_BOX_GAP = 4      # 字 ↔ 格子
CELL_HEIGHT = 24          # ✅ 行高（压缩行距）

MARGIN = 12
TOP_MARGIN = 10

MAX_COLS = 9

TXT_FILES = [
    "chinese.txt",
    "english.txt",
    "numbers.txt",
    "others.txt"
]

# ========================================================
# 二、注册字体
# ========================================================

pdfmetrics.registerFont(
    TTFont("SimSun", FONT_PATH)
)

# ========================================================
# 三、读取字符
# ========================================================

all_chars = []
for fname in TXT_FILES:
    path = os.path.join(TXT_DIR, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            all_chars.extend(list(f.read().strip()))

# ========================================================
# 四、自动计算列数
# ========================================================

PAGE_W, PAGE_H = A4

MIN_COL_WIDTH = (3 * BOX_SIZE + 2 * BOX_GAP) * mm
AVAILABLE_W = PAGE_W - 2 * MARGIN * mm
COLS = min(MAX_COLS, int(AVAILABLE_W // MIN_COL_WIDTH))
col_width = AVAILABLE_W / COLS

CHARS_PER_PAGE = ROWS * COLS

# ========================================================
# 五、生成 PDF
# ========================================================

c = canvas.Canvas(OUTPUT_PDF, pagesize=A4)

styles = getSampleStyleSheet()
style = styles["Normal"]
style.fontName = "SimSun"
style.fontSize = 8

y_start = PAGE_H - TOP_MARGIN * mm
x_start = MARGIN * mm

for idx, ch in enumerate(all_chars):

    page_local = idx % CHARS_PER_PAGE
    col = page_local % COLS
    row = page_local // COLS

    if page_local == 0 and idx != 0:
        c.showPage()
        c.setFont("SimSun", 8)

    x = x_start + col * col_width
    y = y_start - row * CELL_HEIGHT * mm

    # ---------- 字 ----------
    para = Paragraph(f"{idx+1:04d} {ch}", style)
    para.wrapOn(c, col_width, 10 * mm)
    para.drawOn(c, x, y - 7)

    # ---------- 格子 ----------
    box_y = y - TEXT_TO_BOX_GAP * mm - BOX_SIZE * mm
    for i in range(3):
        bx = x + i * (BOX_SIZE + BOX_GAP) * mm
        c.rect(bx, box_y, BOX_SIZE * mm, BOX_SIZE * mm)

c.save()

print("✅ 行距更紧的 12 行 PDF 已生成:", OUTPUT_PDF)
print(f"实际列数: {COLS}，每页 {CHARS_PER_PAGE} 字")