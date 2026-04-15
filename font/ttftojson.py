import json
from pathlib import Path
import glob
import os
import re
import xml.etree.ElementTree as ET
from svgpathtools import svg2paths

SVG_DIRECTORY = "./svg_output/"
SVG_OUT = "svgfong.json"

def normalize_bbox(bbox):
    x0, y0, x1, y1 = bbox

    width = x1 - x0
    height = y1 - y0

    return {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "width": width,
        "height": height
    }

def compute_baseline(all_glyphs):
    max_y1 = 0

    for g in all_glyphs:
        y1 = g["bbox"]["y1"]
        if y1 > max_y1:
            max_y1 = y1

    return max_y1 + 20  # padding（很重要）

def compute_advance(bbox):
    return bbox["width"] * 1.15

def parse_svg(svg_path):
    svg_path = Path(svg_path)
    tree = ET.parse(svg_path)
    root = tree.getroot()

    width = root.get("width")
    height = root.get("height")

    if width is None or height is None:
        viewbox = root.get("viewBox")
        _, _, width, height = map(float, viewbox.split())

    width = float(clean_number(width))
    height = float(clean_number(height))

    bbox = get_svg_bbox(svg_path)
    xmin, ymin, xmax, ymax = bbox

    offset_x = -xmin
    offset_y = -ymin

    return{
        "file": svg_path.name,
        "width": width,
        "height": height,
        "bbox": [xmin, ymin, xmax, ymax],
        "offset_x": offset_x,
        "offset_y": offset_y
    }

def clean_number(value):
    if value is None:
        return None

    # 提取数字（支持 pt / px / em 等）
    m = re.match(r"([0-9.]+)", str(value))
    if m:
        return float(m.group(1))

    return None

def get_svg_bbox(svg_file):
    paths, _ = svg2paths(svg_file)

    xmin, ymin = float("inf"), float("inf")
    xmax, ymax = float("-inf"), float("-inf")

    for path in paths:
        box = path.bbox()
        xmin = min(xmin, box[0])
        xmax = max(xmax, box[1])
        ymin = min(ymin, box[2])
        ymax = max(ymax, box[3])

    return [xmin, ymin, xmax, ymax]

def get_char(name, unicode_str):
    try:
        return chr(int(unicode_str[1:], 16))
    except:
        pass

    return name 

def parse_file_name(svg_file):
    name = svg_file.replace(".svg", "")
    parts = name.split("_")
    idx = parts[-1]
    unicode = parts[-2]
    name = "_".join(parts[:-2])

    return name, unicode, int(idx)

def build_font_json():
    result= {"char": {}}
    all_gyphs = []

    for f in Path(SVG_DIRECTORY).glob("*.svg"):
        parsed = parse_file_name(f.name)
        if not parsed:
            continue
        name, unicode, idx = parsed

        meta = parse_svg(f)

        bbox = normalize_bbox(meta["bbox"])

        advance = compute_advance(bbox)

        glyph = {
            "id": idx,
            "file": meta["file"],
            "bbox": bbox,
            "advance": advance
        }

        all_gyphs.append(glyph)

        char_key = get_char(name, unicode)

        if char_key not in result["char"]:
            result["char"][char_key] = {
                "unicode": unicode,
                "char": char_key,
                "svg": []
            }

        result["char"][char_key]["svg"].append(glyph)

    for char in result["char"].values():
        char["svg"].sort(key=lambda x: x["id"])

    baseline = compute_baseline(all_gyphs)

    result["meta"] = {
        "baseline": baseline
    }

    return result
        
def save_json(data):
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = build_font_json()
    save_json(data)
    print("svg font json is created!!")