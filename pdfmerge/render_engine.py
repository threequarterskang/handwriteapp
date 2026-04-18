import xml.etree.ElementTree as ET
import copy
import re
import numpy as np


class RenderEngine:
    def __init__(self, svg_folder, page_height=2000):
        self.svg_folder = svg_folder
        self.page_height = page_height

        # glyph cache（存“已归一化 glyph”）
        self.glyph_cache = {}

    # =====================================================
    # 🟢 1️⃣ Glyph Normalization（内置，但隔离逻辑）
    # =====================================================
    def normalize_glyph(self, root):
        """
        把 potrace SVG → pure path SVG
        """

        new_root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg")

        for g in root.findall(".//{*}g"):
            transform = g.get("transform")
            tx, ty, sx, sy = self.parse_transform(transform)

            # matrix
            M = self.mat(tx, ty, sx, sy)

            for path in g.findall(".//{*}path"):
                new_path = copy.deepcopy(path)
                d = path.attrib.get("d")

                # ⚠️ 工业级这里应用 svgpathtools
                # 简化版：先保留（或你后续升级）
                new_path.attrib["d"] = d

                new_root.append(new_path)

        return new_root

    # =====================================================
    # 🟢 2️⃣ transform parser
    # =====================================================
    def parse_transform(self, t):
        tx = ty = 0
        sx = sy = 1

        if not t:
            return tx, ty, sx, sy

        m1 = re.search(r"translate\(([-\d.]+)[ ,]([-\d.]+)\)", t)
        if m1:
            tx, ty = float(m1.group(1)), float(m1.group(2))

        m2 = re.search(r"scale\(([-\d.]+)(?:[ ,]([-\d.]+))?\)", t)
        if m2:
            sx = float(m2.group(1))
            sy = float(m2.group(2)) if m2.group(2) else sx

        return tx, ty, sx, sy

    # =====================================================
    # 🟢 3️⃣ matrix
    # =====================================================
    def mat(self, tx, ty, sx, sy):
        return np.array([
            [sx, 0, tx],
            [0, sy, ty],
            [0,  0, 1]
        ])

    # =====================================================
    # 🟢 4️⃣ load glyph（含 normalization）
    # =====================================================
    def load_glyph(self, filename):
        if filename in self.glyph_cache:
            return self.glyph_cache[filename]

        path = f"{self.svg_folder}/{filename}"
        tree = ET.parse(path)
        root = tree.getroot()

        # 🔥 关键：在这里做 normalize
        normalized = self.normalize_glyph(root)

        self.glyph_cache[filename] = normalized
        return normalized

    # =====================================================
    # 🟢 5️⃣ render page（纯 render）
    # =====================================================
    def render_page(self, layout_items, config, index=0):
        fields = config.get("fields")
        if not fields:
            raise ValueError("missing fields")

        x0, y0, x1, y1 = fields[index]["blankbbox"]

        width = x1 - x0
        height = y1 - y0

        svg = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(width),
            height=str(height),
            viewBox=f"0 0 {width} {height}"
        )

        for item in layout_items:
            glyph = self.load_glyph(item["file"])

            x = item["x"] - x0
            y = item["y"] - y0
            scale = item.get("scale", 1.0)

            g = ET.Element("g")

            # ✔️ render only
            g.set("transform", f"translate({x},{y}) scale({scale})")

            for child in glyph:
                g.append(copy.deepcopy(child))

            svg.append(g)

        return svg

    # -----------------------------
    # 4️⃣ 多页渲染
    # -----------------------------
    def render_multi_page(self, pages):
        """
        pages = [
            [layout_item, layout_item],   # page1
            [layout_item, layout_item],   # page2
        ]
        """

        all_pages = []

        for page_items in pages:
            svg = self.render_page(page_items)
            all_pages.append(svg)

        return all_pages

    # -----------------------------
    # 5️⃣ 保存SVG
    # -----------------------------
    def save_svg(self, svg_root, filename):
        tree = ET.ElementTree(svg_root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    # -----------------------------
    # 6️⃣ 批量保存多页
    # -----------------------------
    def save_multi_page(self, svg_pages, base_name="output"):
        for i, page in enumerate(svg_pages):
            self.save_svg(page, f"{base_name}_page_{i+1}.svg")