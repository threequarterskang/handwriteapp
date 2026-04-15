import fontforge
import os
import re

SVG_DIR = "./svg_output"
OUTPUT_FONT = "handwriting_multi.ttf"

SVG_PATTERN = re.compile(r"(.+?)_U([0-9A-F]+)_(\d)\.svg")

glyph_map = {}

# ========================================================
# 一、解析 SVG
# ========================================================

for fname in os.listdir(SVG_DIR):
    if not fname.lower().endswith(".svg"):
        continue

    m = SVG_PATTERN.match(fname)
    if not m:
        continue

    char_safe, hexcode, idx = m.groups()
    unicode_int = int(hexcode, 16)

    glyph_map.setdefault(unicode_int, []).append(
        os.path.join(SVG_DIR, fname)
    )

# ========================================================
# 二、创建 glyph（修复版）
# ========================================================

font = fontforge.font()
font.fontname = "HandwritingMulti"
font.familyname = "Handwriting Multi"
font.em = 1000

for unicode_int, svg_list in glyph_map.items():

    svg_list.sort()

    # ✅ base glyph（必须有内容）
    base = font.createChar(unicode_int, f"uni{unicode_int:04X}")
    base.importOutlines(svg_list[0])
    base.width = 1000

    # ✅ 变体 glyph
    for i, svg_path in enumerate(svg_list, start=1):
        gname = f"uni{unicode_int:04X}.{i}"
        g = font.createChar(-1, gname)
        g.importOutlines(svg_path)
        g.width = 1000

# ========================================================
# 三、GSUB（标准写法）
# ========================================================

# ⭐ 必须加 feature tag
font.addLookup("ss01", "gsub_single", (), (("ss01", (("DFLT", ("dflt",)),)),))
font.addLookupSubtable("ss01", "ss01_sub")

font.addLookup("ss02", "gsub_single", (), (("ss02", (("DFLT", ("dflt",)),)),))
font.addLookupSubtable("ss02", "ss02_sub")

font.addLookup("ss03", "gsub_single", (), (("ss03", (("DFLT", ("dflt",)),)),))
font.addLookupSubtable("ss03", "ss03_sub")

# 建立替换关系
for unicode_int, svg_list in glyph_map.items():

    base_name = f"uni{unicode_int:04X}"

    if base_name not in font:
        continue

    base = font[base_name]

    if len(svg_list) >= 1:
        base.addPosSub("ss01_sub", f"{base_name}.1")

    if len(svg_list) >= 2:
        base.addPosSub("ss02_sub", f"{base_name}.2")

    if len(svg_list) >= 3:
        base.addPosSub("ss03_sub", f"{base_name}.3")

# ========================================================
# 四、生成字体
# ========================================================

font.generate(OUTPUT_FONT)
print(f"✅ 字体生成完成：{OUTPUT_FONT}")