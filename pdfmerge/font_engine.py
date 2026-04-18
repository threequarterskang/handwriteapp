import random


class FontEngine:
    def __init__(self, font_data):
        self.glyph_map = font_data["char"]
        self.meta = font_data.get("meta", {})
        self.last_choice = {}

    # -----------------------------
    # ✔️ 只负责 glyph selection
    # -----------------------------
    def get_glyph(self, char):
        glyph = self.glyph_map.get(char)
        if not glyph:
            return None

        svg_list = glyph["svg"]

        last = self.last_choice.get(char)
        candidate = [g for g in svg_list if g != last]
        chosen = random.choice(candidate or svg_list)

        self.last_choice[char] = chosen

        bbox = chosen["bbox"]

        return {
            "char": char,
            "file": chosen["file"],
            "bbox": bbox,
            "advance": chosen["advance"]
        }

    # -----------------------------
    # ✔️ metrics helper（optional）
    # -----------------------------
    def get_metrics(self, char):
        glyph = self.glyph_map.get(char)
        if not glyph:
            return None

        # average bbox for char group
        svg_list = glyph["svg"]

        avg_height = sum(g["bbox"]["height"] for g in svg_list) / len(svg_list)
        avg_advance = sum(g["advance"] for g in svg_list) / len(svg_list)

        return {
            "avg_height": avg_height,
            "avg_advance": avg_advance
        }