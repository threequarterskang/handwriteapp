import random

class FontEngine:
    def __init__(self, font_data):
        self.glyph_map = font_data["char"]
        self.meta = font_data.get("meta", {})
        self.last_choice = {}
    
    def get_glyph(self, char, target_height=None):
        glyph = self.glyph_map.get(char)

        if not glyph:
            return None
        
        svg_list = glyph["svg"]

        last = self.last_choice.get(char)
        candidate = [g for g in svg_list if g!= last]
        chosen = random.choice(candidate or svg_list)
        self.last_choice[char] = chosen

        bbox = chosen["bbox"]
        scale = 1.0

        if target_height:
            scale = target_height / bbox["height"]

        # slight scale randomness (handwriting feel)
        scale *= random.uniform(0.97, 1.03)

        return {
            "char": char,
            "file": chosen["file"],
            "bbox": bbox,
            "advance": chosen["advance"],
            "scale": scale
        }
