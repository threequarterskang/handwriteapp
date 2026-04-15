import random
import math
from font_engine import FontEngine

# =========================
# LayoutEngine
# =========================

class LayoutEngine:
    def __init__(self, font_engine):
        self.font_engine = font_engine

    def layout(self, text, index, config):
        fields = config.get("fields")
        if not fields:
            raise ValueError("missing fields!!")

        x0 = fields[index]["blankbbox"][0]
        y0 = fields[index]["blankbbox"][1]
        x1 = fields[index]["blankbbox"][2]
        y1 = fields[index]["blankbbox"][3]

        max_width = x1 - x0
        max_height = y1 - y0

        baseline = self.font_engine.meta.get("baseline", 0)

        placed = []
        result = []

        width = 0 
        count = 0
        for ch in text:
            glyph = self.font_engine.get_glyph(ch)

            if not glyph:
                continue
            
            w = glyph["advance"]

            width += w
            count += 1

        avg_advance = width / count * 0.4
        blankwidth = x1 - x0
        blankheight = y1 -y0

        scale = self.compute_scale(
            count, blankwidth, blankheight, avg_advance, baseline
            )
        
        for ch in text:
            glyph = self.font_engine.get_glyph(ch)

            if not glyph:
                continue

            x = x0
            y = y0
            line_height = baseline * scale * 1.2
            bbox = glyph["bbox"]
            w = bbox["width"] * scale
            h = bbox["height"] * scale

            # Auto line break
            if x + w > max_width:
                x = x0
                y0 += line_height

            # Handwriting jitter
            dx = random.uniform(-3, 3)
            dy = random.uniform(-2, 2)

            # Baseline alignment (CORE)
            draw_y = y - (baseline - bbox["y0"]) * scale + dy

            box = {
                "x0": x + dx,
                "y0": draw_y,
                "x1": x + dx + w,
                "y1": draw_y + h
            }

            # Collision resolve
            box = self.resolve_collision(box, placed)

            result.append({
                "char": ch,
                "file": glyph["file"],
                "x": box["x0"],
                "y": box["y0"],
                "scale": scale
            })

            placed.append(box)

            # Advance with slight randomness
            x += glyph["advance"] * scale * random.uniform(0.98, 1.05)
        return result
    
    def compute_scale(self, text_len, blank_w, blank_h, avg_advance, baseline):
        scale = blank_h / baseline

        for _ in range(20):
            char_w = avg_advance * scale

            chars_per_line = max(1, int(blank_w/char_w))

            lines = math.ceil(text_len / chars_per_line)

            total_h = lines * baseline * scale
            
            if total_h > blank_h:
                scale *= 0.95
            else:
                break
        return scale


    def resolve_collision(self, box, placed):
        for _ in range(8):
            overlap_found = False

            for p in placed:
                if self.is_overlap(box, p):
                    overlap_found = True
                    break

            if not overlap_found:
                return box

            # shift slightly
            shift_x = random.uniform(2, 5)
            shift_y = random.uniform(-2, 2)

            box["x0"] += shift_x
            box["x1"] += shift_x
            box["y0"] += shift_y
            box["y1"] += shift_y

        return box

    def is_overlap(self, a, b):
        return not (
            a["x1"] < b["x0"] or
            a["x0"] > b["x1"] or
            a["y1"] < b["y0"] or
            a["y0"] > b["y1"]
        )
