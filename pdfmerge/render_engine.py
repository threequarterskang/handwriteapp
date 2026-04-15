import xml.etree.ElementTree as ET
import copy

class SVGRenderer:
    def __init__(self, svg_folder, page_height=2000):
        self.svg_folder = svg_folder
        self.page_height = page_height

        # 🔥 glyph缓存（工业级关键）
        self.glyph_cache = {}

    # -----------------------------
    # 1️⃣ 加载SVG glyph（带缓存）
    # -----------------------------
    def load_glyph(self, filename):
        if filename in self.glyph_cache:
            return self.glyph_cache[filename]

        path = f"{self.svg_folder}/{filename}"
        tree = ET.parse(path)
        root = tree.getroot()

        # 只缓存内容（避免tree引用问题）
        self.glyph_cache[filename] = copy.deepcopy(root)

        return self.glyph_cache[filename]

    # -----------------------------
    # 2️⃣ 坐标转换（PDF → SVG）
    # -----------------------------
    def convert_y(self, y):
        return self.page_height - y

    # -----------------------------
    # 3️⃣ 渲染单页
    # -----------------------------
    def render_page(self, layout_items, index, valueconfig):
        fields = valueconfig.get("fields")

        x0 = fields[index]["blankbbox"][0]
        y0 = fields[index]["blankbbox"][1]
        x1 = fields[index]["blankbbox"][2]
        y1 = fields[index]["blankbbox"][3]

        max_width = x1 - x0
        max_height = y1 - y0

        svg = ET.Element(
            "svg", 
            xmlns="http://www.w3.org/2000/svg",
            width=str(max_width),
            height=str(max_height),
            viewBox=f"0 0 {max_width} {max_height}"
            )

        for item in layout_items:
            glyph = self.load_glyph(item["file"])

            # 🔥 坐标修正
            x = item["x"]-x0
            y = item["y"]-y0
            #y = self.convert_y(item["y"])

            scale = item.get("scale", 1.0)
            #rotate = item.get("rotate", 0)

            # -------------------------
            # group包装
            # -------------------------
            g = ET.Element("g")

            transform = f"translate({x},{y}) scale({scale})" # rotate({rotate})"
            g.set("transform", transform)

            # 克隆glyph内容
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