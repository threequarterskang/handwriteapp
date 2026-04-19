import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import cairosvg
import tempfile
from io import BytesIO


# 将 SVG 转换为 PNG 图像
def convert_svg_to_png(svg_file):
    output = BytesIO()
    cairosvg.svg2png(url=svg_file, write_to=output)
    output.seek(0)
    return output


# 保存 BytesIO 内容为临时文件
def save_bytesio_to_tempfile(bytes_io, suffix='.png'):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with open(temp_file.name, 'wb') as f:
        f.write(bytes_io.read())
    return temp_file.name


# 合并 SVG 图像和现有的 PDF 内容到同一页面
def merge_svg_and_pdf(svg_file, pdf_file, output_pdf):
    # 读取现有 PDF 文件
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    # 获取 PDF 页面（这里假设我们处理第一页）
    page = pdf_reader.pages[0]

    # 创建一个临时文件来生成最终的 PDF
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_output.close()

    # 使用 ReportLab 创建一个新的 PDF，合并现有页面和 SVG 内容
    c = canvas.Canvas(temp_output.name, pagesize=(page.mediabox[2], page.mediabox[3]))

    # 在 ReportLab canvas 上绘制现有的 PDF 内容
    c.setPageSize((page.mediabox[2], page.mediabox[3]))  # 设置与现有页面相同的页面尺寸
    c.showPage()

    # 将 SVG 转换为 PNG
    svg_png = convert_svg_to_png(svg_file)
    svg_png.seek(0)  # 重置指针

    # 将 BytesIO 内容保存为临时文件
    temp_svg_png = save_bytesio_to_tempfile(svg_png, suffix='.png')

    # 将 SVG PNG 图像嵌入到 PDF 页面上
    c.drawImage(temp_svg_png, 100, 100, width=400, height=400)  # 设置位置和尺寸（可以根据需要调整）

    # 保存合并后的页面
    c.save()

    # 合并现有的 PDF 页面和新的 SVG 页面
    pdf_writer.add_page(page)

    # 将新的合并内容添加到 PDF
    final_pdf = PdfReader(temp_output.name)
    pdf_writer.add_page(final_pdf.pages[0])

    # 写入最终合并的 PDF
    with open(output_pdf, 'wb') as output:
        pdf_writer.write(output)

    # 删除临时文件
    os.remove(temp_output.name)
    os.remove(temp_svg_png)

    print(f"合并后的 PDF 文件保存在: {output_pdf}")


def main():
    svg_file = 'outputTR148.svg'
    pdf_file = '6.1 TR.pdf'
    output_pdf = 'combinetr.pdf'
    merge_svg_and_pdf(svg_file, pdf_file, output_pdf)


if __name__ == "__main__":
    #multiresult()
    main()