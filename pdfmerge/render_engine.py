import xml.etree.ElementTree as ET
import os
import copy

class RenderEngine:
    def __init__(self, svg_folder, width=595.5, height=842):
        self.svg_folder = svg_folder
        self.width = width
        self.height = height
        self.cache = {}

    # ==========================================
    # 🧠 load glyph
    # ==========================================
    def load_glyph(self, filename):
        if filename in self.cache:
            return self.cache[filename]

        path = os.path.join(self.svg_folder, filename)
        root = ET.parse(path).getroot()

        self.cache[filename] = root
        return root

    # ==========================================
    # 🧠 render page（核心）
    # ==========================================
    def render_page(self, results):

        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(self.width),
            "height": str(self.height),
            "viewBox": f"0 0 {self.width} {self.height}"
        })

        flat = []
        for r in results:
            flat.extend(r) if isinstance(r, list) else flat.append(r)

        for item in flat:

            root = self.load_glyph(item["file"])

            x = float(item["x"])
            y = float(item["y"])
            scale = float(item["scale"])
            print(scale)
            # 🔥 关键：修改 glyph 内部 transform
            new_root = self.apply_to_glyph(root, x, y, scale)

            svg.append(new_root)

        return svg

    # ==========================================
    # 🧠 transform rewrite
    # ==========================================
    def apply_to_glyph(self, root, x, y, scale):

        root = copy.deepcopy(root)

        # =========================
        # 🔥 1. 重写 svg root（关键）
        # =========================
        root.set("width", str(self.width))
        root.set("height", str(self.height))
        root.set("viewBox", f"0 0 {self.width} {self.height}")

        # =========================
        # 🔥 2. 处理所有 g
        # =========================
        for g in root.findall(".//{*}g"):

            old = g.get("transform", "")

            tx, ty, sx, sy = self.parse_transform(old)

            # scale 合并
            Sx = sx * scale
            Sy = sy * scale

            # translate 合并（带 sy）
            X = x + tx * scale
            Y = y + ty * scale * sy

            g.set("transform", f"translate({X},{Y}) scale({Sx},{Sy})")

        return root

    # ==========================================
    # 🧠 parse transform
    # ==========================================
    def parse_transform(self, transform):
        import re

        tx = ty = 0.0
        sx = sy = 1.0

        if not transform:
            return tx, ty, sx, sy

        t = re.search(r'translate\(([^)]+)\)', transform)
        if t:
            nums = list(map(float, t.group(1).replace(',', ' ').split()))
            tx = nums[0]
            ty = nums[1] if len(nums) > 1 else 0.0

        s = re.search(r'scale\(([^)]+)\)', transform)
        if s:
            nums = list(map(float, s.group(1).replace(',', ' ').split()))
            sx = nums[0]
            sy = nums[1] if len(nums) > 1 else sx

        return tx, ty, sx, sy

    # ==========================================
    # 🧠 多页渲染
    # ==========================================
    def render_multi_page(self, pages, flip_y=False):
        all_pages = []
        for page_results in pages:
            svg = self.render_page(page_results, flip_y=flip_y)
            all_pages.append(svg)
        return all_pages

    # ==========================================
    # 💾 保存单页
    # ==========================================
    def save_svg(self, svg_root, filename):
        tree = ET.ElementTree(svg_root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    # ==========================================
    # 💾 保存多页
    # ==========================================
    def save_multi_page(self, svg_pages, base_name="output"):
        for i, page in enumerate(svg_pages):
            filename = f"{base_name}_page_{i+1}.svg"
            self.save_svg(page, filename)