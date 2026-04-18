import xml.etree.ElementTree as ET
import re
import os


class RenderEngine:
    def __init__(self, svg_folder, page_height=2000):
        self.svg_folder = svg_folder
        self.page_height = page_height
        self.glyph_cache = {}

    # ==========================================
    # 🧠 解析 transform
    # ==========================================
    def parse_transform(self, transform_str):
        tx, ty = 0.0, 0.0
        sx, sy = 1.0, 1.0

        if not transform_str:
            return tx, ty, sx, sy

        t_match = re.search(r'translate\(([^)]+)\)', transform_str)
        if t_match:
            nums = list(map(float, t_match.group(1).replace(',', ' ').split()))
            tx = nums[0]
            ty = nums[1] if len(nums) > 1 else 0.0

        s_match = re.search(r'scale\(([^)]+)\)', transform_str)
        if s_match:
            nums = list(map(float, s_match.group(1).replace(',', ' ').split()))
            sx = nums[0]
            sy = nums[1] if len(nums) > 1 else sx

        return tx, ty, sx, sy

    # ==========================================
    # 🧠 加载 glyph（带缓存）
    # ==========================================
    def load_glyph(self, filename):
        if filename in self.glyph_cache:
            return self.glyph_cache[filename]

        path = os.path.join(self.svg_folder, filename)

        tree = ET.parse(path)
        root = tree.getroot()

        viewBox = root.attrib.get("viewBox")
        if not viewBox:
            raise ValueError(f"{filename} missing viewBox")

        _, _, vw, vh = map(float, viewBox.split())

        g = root.find("{http://www.w3.org/2000/svg}g")
        if g is None:
            raise ValueError(f"{filename} missing <g>")

        transform = g.attrib.get("transform", "")
        tx, ty, sx, sy = self.parse_transform(transform)

        real_w = vw * abs(sx)
        real_h = vh * abs(sy)

        glyph = {
            "root": root,
            "real_w": real_w,
            "real_h": real_h,
        }

        self.glyph_cache[filename] = glyph
        return glyph

    # ==========================================
    # 🧠 计算放置
    # ==========================================
    def place_glyph(self, glyph, blankbox):
        x0, y0, x1, y1 = blankbox

        box_w = x1 - x0
        box_h = y1 - y0

        gw = glyph["real_w"]
        gh = glyph["real_h"]

        scale = min(box_w / gw, box_h / gh)

        draw_x = x0 + (box_w - gw * scale) / 2
        draw_y = y0 + (box_h - gh * scale) / 2

        return draw_x, draw_y, scale

    # ==========================================
    # 🧠 渲染单页
    # ==========================================
    def render_page(self, layout_items, config, index=0):
        fields = config.get("fields")
        if not fields:
            raise ValueError("missing fields")

        x0, y0, x1, y1 = fields[index]["blankbbox"]

        width = x1 - x0
        height = y1 - y0

        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(width),
            "height": str(height),
            "viewBox": f"0 0 {width} {height}"
        })

        for item in layout_items:
            glyph = self.load_glyph(item["file"])

            blankbox = fields[index]["blankbbox"]

            draw_x, draw_y, scale = self.place_glyph(glyph, blankbox)

            # 🔥 坐标转换：全局 → 局部
            local_x = draw_x - x0
            local_y = draw_y - y0

            outer = ET.Element("g")
            outer.set("transform", f"translate({local_x},{local_y}) scale({scale})")

            for child in list(glyph["root"]):
                outer.append(child)

            svg.append(outer)

        return svg

    # ==========================================
    # 多页
    # ==========================================
    def render_multi_page(self, pages, config):
        all_pages = []

        for i, page_items in enumerate(pages):
            svg = self.render_page(page_items, config, i)
            all_pages.append(svg)

        return all_pages

    # ==========================================
    # 保存
    # ==========================================
    def save_svg(self, svg_root, filename):
        tree = ET.ElementTree(svg_root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def save_multi_page(self, svg_pages, base_name="output"):
        for i, page in enumerate(svg_pages):
            self.save_svg(page, f"{base_name}_page_{i+1}.svg")