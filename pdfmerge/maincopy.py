import json

from font_engine import FontEngine
from layout_engine import LayoutEngine
from render_engine import RenderEngine
from pdf_engine import PDFEngine
from pipeline import HandwritingPipeline


# ----------------------------
# load data
# ----------------------------
with open("data/template.json", "r", encoding="utf-8") as f:
    template = json.load(f)

with open("data/font.json", "r", encoding="utf-8") as f:
    font_map = json.load(f)

with open("data/db.json", "r", encoding="utf-8") as f:
    db = json.load(f)


# ----------------------------
# init engine
# ----------------------------
font_engine = FontEngine(font_map)
layout_engine = LayoutEngine()
render_engine = RenderEngine()
pdf_engine = PDFEngine("template.pdf")


pipeline = HandwritingPipeline(
    font_engine,
    layout_engine,
    render_engine,
    pdf_engine
)


# ----------------------------
# run
# ----------------------------
result = pipeline.run(template, db)

result.save("output.pdf")

print("DONE: output.pdf generated")