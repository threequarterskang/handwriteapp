import math
from font_engine import FontEngine


class LayoutEngine:
    def __init__(self, font_engine):
        self.font_engine = font_engine

    # -----------------------------
    # ✔️ main layout
    # -----------------------------
    def layout(self, text, index, config):
        fields = config.get("fields")
        if not fields:
            raise ValueError("missing fields")

        x0, y0, x1, y1 = fields[index]["blankbbox"]

        max_width = x1 - x0
        max_height = y1 - y0

        baseline = self.font_engine.meta.get("baseline", 100)

        # -----------------------------
        # 1️⃣ collect metrics
        # -----------------------------
        advances = []
        count = 0

        for ch in text:
            g = self.font_engine.get_glyph(ch)
            if not g:
                continue

            advances.append(g["advance"])
            count += 1

        avg_advance = sum(advances) / max(1, len(advances))

        # -----------------------------
        # 2️⃣ compute global scale
        # -----------------------------
        scale = self.compute_scale(
            len(text),
            max_width,
            max_height,
            avg_advance,
            baseline
        )

        # -----------------------------
        # 3️⃣ layout cursor (IMPORTANT FIX)
        # -----------------------------
        x = x0
        y = y0
        line_height = baseline * scale * 1.2

        result = []
        placed_boxes = []

        # -----------------------------
        # 4️⃣ layout loop
        # -----------------------------
        for ch in text:
            glyph = self.font_engine.get_glyph(ch)
            if not glyph:
                continue

            advance = glyph["advance"] * scale

            # ✔️ line break (correct logic)
            if x + advance > x0 + max_width:
                x = x0
                y += line_height  # ✔️ FIX: NOT y0

            # -----------------------------
            # position (NO jitter in core)
            # -----------------------------
            draw_x = x
            draw_y = y - (baseline * scale)

            box = {
                "x0": draw_x,
                "y0": draw_y,
                "x1": draw_x + advance,
                "y1": draw_y + line_height
            }

            placed_boxes.append(box)

            result.append({
                "char": ch,
                "file": glyph["file"],
                "x": draw_x,
                "y": draw_y,
                "scale": scale
            })

            # advance cursor
            x += advance

        return result

    # -----------------------------
    # ✔️ scale computation (clean version)
    # -----------------------------
    def compute_scale(self, text_len, max_w, max_h, avg_advance, baseline):
        chars_per_line = max(1, int(max_w / avg_advance))
        lines = math.ceil(text_len / chars_per_line)

        scale_w = max_w / (avg_advance * chars_per_line)
        scale_h = max_h / (baseline * lines)

        scale = min(scale_w, scale_h)

        return scale * 0.95