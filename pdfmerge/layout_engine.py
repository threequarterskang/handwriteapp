import math
import numpy as np


class LayoutEngine:
    def __init__(self, font_engine):
        self.font_engine = font_engine

    def classify_char(self, ch):
        if '\u4e00' <= ch <= '\u9fff':
            return "CJK"  # 中文
        elif ch.isalpha():
            return "LATIN"
        elif ch.isdigit():
            return "DIGIT"
        else:
            return "PUNCT"
    
    # =========================================
    # ✔️ MAIN LAYOUT
    # =========================================
    def layout(self, text, index, config):
        fields = config.get("fields")
        if not fields:
            raise ValueError("missing fields")

        x0, y0, x1, y1 = fields[index]["blankbbox"]

        max_w = x1 - x0
        max_h = y1 - y0

        # 字体不一样间距不同
        spacing_rules = {
            "CJK": 1.0,      # 中文基本不动
            "LATIN": 1.3,    # 英文更紧凑
            "DIGIT": 1.2,
            "PUNCT": 0.5    # 标点更紧
        }
        # ---------------------------------
        # 1️⃣ collect glyph metrics
        # ---------------------------------
        advances = []
        y_maxs = []
        y_mins = []
        glyphs = []

        valid_chars = 0

        for ch in text:
            g = self.font_engine.get_glyph(ch)
            if not g:
                continue

            glyphs.append((ch, g))
            advances.append(g["advance"])

            bbox = g["bbox"]
            y_mins.append(bbox["y0"])
            y_maxs.append(bbox["y1"])

            valid_chars += 1

        if not advances:
            return []

        avg_advance = sum(advances) / len(advances)

        # ---------------------------------
        # 2️⃣ build font metrics (IMPORTANT FIX)
        # ---------------------------------
        ascent = np.percentile(y_maxs, 95)
        descent = np.percentile(y_mins, 5)

        em_height = ascent - descent

        line_height = em_height * 1.2  # ✔️ correct model

        # ---------------------------------
        # 3️⃣ estimate layout
        # ---------------------------------
        print(f'max_w: {max_w}---avg_advance: {avg_advance}')
        chars_per_line = max(1, int(max_w / (avg_advance * 0.00009)))
        lines = math.ceil(valid_chars / chars_per_line)
        print(f'{lines} row font')
        scale_w = max_w / (chars_per_line * avg_advance * 0.00009)
        scale_h = max_h / (lines * line_height)
        print(f'({scale_w}----{scale_h})')
        scale = min(scale_w, scale_h) * 2
        print(f'({text}---{scale})')
        # ---------------------------------
        # 4️⃣ layout loop
        # ---------------------------------
        result = []

        x = x0
        y = y0
        magic_number = 0.1

        for ch, g in glyphs:
            if not g:
                continue
            
            char_type = self.classify_char(ch)
            spacing_factor = spacing_rules[char_type]

            advance = g["advance"] * scale * spacing_factor * magic_number

            # ✔ line break
            if x + advance * magic_number > x0 + max_w:
                x = x0
                y += line_height * scale

            # ---------------------------------
            # ✔ baseline correction (FIXED)
            # ---------------------------------
            draw_x = x
            draw_y = y + (ascent * scale)
            
            print(g["file"])
            result.append({
                "char": ch,
                "file": g["file"],
                "x": draw_x,
                "y": draw_y,
                "scale": scale
            })

            x += advance

        return result

    # =========================================
    # ✔️ SCALE (consistent model)
    # =========================================
    def compute_scale(self, max_w, max_h, avg_advance, ascent, descent, text_len):
        em = ascent - descent
        line_height = em * 1.2

        chars_per_line = max(1, int(max_w / avg_advance))
        lines = math.ceil(text_len / chars_per_line)

        scale_w = max_w / (chars_per_line * avg_advance)
        scale_h = max_h / (lines * line_height)

        return min(scale_w, scale_h) * 0.95