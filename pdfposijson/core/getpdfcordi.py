# core/getpdfcordi.py

import re
import fitz  # PyMuPDF
import numpy as np
import cv2
from pathlib import Path
import glob

def pdf_to_img(page, zoom=2):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    return img

# =========================
# 2. 解析 PDF 标记 {xxx}
# =========================
def extract_markers(pdf_path):
    doc = fitz.open(pdf_path)
    markers = {}

    special_fields = ["□全检", "□Ⅱ", "□抽检", "□合格"]

    for page_index, page in enumerate(doc):
        text_dict = page.get_text("dict")

        for block in text_dict["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"]
                    
                    matches = re.findall(r"\{(.*?)\}", text)

                    if "□" in text:
                        print(f"{pdf_path}, {text}")

                    # Only detect exact special fields from the configured list
                    for field in special_fields:
                        if field in text:
                            matches.append(field)

                    if matches:
                        chars = span.get("chars", [])
                        for m in matches:
                            # Find the position of the field in the text
                            start_idx = text.find(m)
                            if start_idx != -1:
                                end_idx = start_idx + len(m)
                                # Get bbox from chars if available
                                if chars and end_idx <= len(chars):
                                    char_bboxes = [chars[i]["bbox"] for i in range(start_idx, end_idx)]
                                    if char_bboxes:
                                        # Combine bboxes
                                        x0 = min(b[0] for b in char_bboxes)
                                        y0 = min(b[1] for b in char_bboxes)
                                        x1 = max(b[2] for b in char_bboxes)
                                        y1 = max(b[3] for b in char_bboxes)
                                    else:
                                        x0, y0, x1, y1 = span["bbox"]
                                else:
                                    x0, y0, x1, y1 = span["bbox"]
                            else:
                                x0, y0, x1, y1 = span["bbox"]

                            markers[m] = {
                                "key": m,
                                "placeholderbbox": [x0, y0, x1, y1]
                            }
                            
                            print (f"🔍 解析到标记: {pdf_path} - [{m}], {pt_to_mm(x0)}, {pt_to_mm(y0)}, {pt_to_mm(x1)}, {pt_to_mm(y1)}\n")
    return doc, markers

def pt_to_mm(pt):
    return pt * 25.4 / 72

##################################################
# binary img
##################################################
def binaryimg(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    binary = cv2.medianBlur(binary, 1)

    kernel = np.ones((5,5), np.uint8)

    binary = cv2.erode(binary, kernel)

    binary = np.where(binary == 255, 1, 0).astype(np.uint8)

    return binary

##################################################
# 最大矩形
##################################################

def largest_rectangle_from_topleft(binary):
    h, w = binary.shape
    
    max_area = 0
    best_rect = (0, 0, 0, 0)

    max_width = w  # 当前允许的最大宽度

    for i in range(h):
        # 找这一行从0开始连续的1的宽度
        row_width = 0
        for j in range(max_width):
            if binary[i][j] == 1:
                row_width += 1
            else:
                break

        # 更新最大宽度（关键！保证是矩形）
        max_width = min(max_width, row_width)

        if max_width == 0:
            break

        area = max_width * (i + 1)

        if area > max_area:
            max_area = area
            best_rect = (0, 0, max_width, i + 1)

    return best_rect

def pdf_to_img_cordinate(page, x0, y0, zoom=2):
#   pdf_x0 = marker["rect"][0]
#   pdf_y1 = marker["rect"][3]      when use the left-bottom as origin ,y1 should be used.
#   pdf_y0 = marker["rect"][1]

#   page_height = page.rect.height

    img_x = int(round(x0 * zoom))
#   img_y = int((page_height - pdf_y1) * zoom)   when use the left-bottom as origin ,y1 should be used.
    img_y = int(round(y0 * zoom))

    return img_x, img_y

def find_local_blank(binary, start_x, start_y, roi_width=200, roi_height=300):
    h, w = binary.shape

    x_end = min(start_x + roi_width, w)
    y_end = min(start_y + roi_height, h)

    roi = binary[start_y:y_end, start_x:x_end]

    x, y, rw, rh = largest_rectangle_from_topleft(roi)

    return (start_x+x)/2, (start_y+y)/2, rw/2, rh/2









