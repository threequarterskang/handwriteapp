import sqlite3
import json
import cv2
import fitz
from pathlib import Path
import glob
import svgutils.transform as st
import json
from layout_engine import LayoutEngine
from font_engine import FontEngine
from render_engine import RenderEngine

QUERY_DB_NAME = "placeholder.db"
DATA_DB_NAME = "total.db"
PDF_DIRECTORY = "./pdf/"
folder = Path("./config")
svg_path = "./svgoutput"

def find_field_index_by_key(fields, key_name, value):
    index = 0
    for i , field in enumerate(fields):
        if str(field.get(key_name)) == str(value):
            index = i
            break
    return index
import PyPDF2
import cairosvg

# 转换 SVG 为 PDF
def convert_svg_to_pdf(svg_file, pdf_file):
    cairosvg.svg2pdf(url=svg_file, write_to=pdf_file)

# 合并 PDF 文件
def merge_pdfs(pdf_list, output_pdf):
    pdf_writer = PyPDF2.PdfWriter()
    
    # 将所有 PDF 添加到 pdf_writer
    for pdf in pdf_list:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
    
    # 保存合并后的 PDF
    with open(output_pdf, 'wb') as output:
        pdf_writer.write(output)
        
def main():
    with open("svgfong.json", "r", encoding="utf-8") as f:
        font_map = json.load(f)

    conn1 = sqlite3.connect(DATA_DB_NAME)
    conn2 = sqlite3.connect(QUERY_DB_NAME)
    conn1.row_factory = sqlite3.Row
    
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()

    res = cur2.execute(
        'SELECT "英文名字", "数据最大范围" FROM field_rule'
    )

    if res:
        print(res)
    else:
        raise ValueError("placehodler's max field is failed to get")

    mapping = dict(res.fetchall())

    print(mapping)

    cur1.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )

    tables = [row[0] for row in cur1.fetchall()]

    if not tables:
        raise ValueError("tables error")
    
    print(tables)

    for tbn in tables:
        if tbn in mapping:
            cur1.execute(
                f'SELECT * FROM "{tbn}"'
            )

            for filename in folder.glob("*.json"):
                print(filename.stem)
                if tbn in filename.stem:
                    with open(filename, "r", encoding="utf-8") as ftemplate:
                        template = json.load(ftemplate)

            fields = template.get("fields")
            row = cur1.fetchone()
            max_column = int(mapping[tbn])
            result = []
            for idx in range(1,max_column+1):
                column_name = f"{{{idx}}}"
                text = row[column_name]
                font_engine = FontEngine(font_map)
                layout_engine = LayoutEngine(font_engine)
                svg_engine = RenderEngine(layout_engine)
                svg_engine.svg_folder = svg_path
                print(idx)
                if text is None:
                    print(f'{column_name} is none..')
                else:
                    index = find_field_index_by_key(fields, "key", idx)
                    result.append(layout_engine.layout(text, index, template))
            svgrender = svg_engine.render_page(result)   
            render = svg_engine.save_svg(svgrender, f'output{tbn}{idx}.svg')
                             
    
    conn1.close()
    conn2.close()


if __name__ == "__main__":
    main()
    print("All done")




