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

    binary = cv2.medianBlur(binary, 3)

    kernel = np.ones((5,5), np.uint8)

    binary = cv2.erode(binary, kernel)

    binary = np.where(binary == 255, 1, 0).astype(np.uint8)

    return binary

##################################################
# 最大矩形
##################################################
def largest_rectangle(binary): 
    h, w = binary.shape
    heights = [0] * w

    max_area = 0
    best_rect = (0, 0, 0 ,0)

    for i in range(h):
        for j in range(w):
            if binary[i][j] == 1:
                heights[j] += 1
            else:
                heights[j] = 0
        
        stack = []
        j = 0

        while j <= w:
            cur = heights[j] if j < w else 0

            if not stack or cur >= heights[stack[-1]]:
                stack.append(j)
                j += 1
            else:
                top = stack.pop()
                width = j if not stack else j - stack[-1] - 1
                area = heights[top] * width

                if area > max_area:
                    max_area = area
                    h_rect = heights[top]
                    w_rect = width

                    x = stack[-1] + 1 if stack else 0
                    y = i - h_rect + 1
                    best_rect = (x, y, w_rect, h_rect)
    return best_rect

def pdf_to_img_cordinate(page, x0, y0, zoom=1):
#   pdf_x0 = marker["rect"][0]
#   pdf_y1 = marker["rect"][3]      when use the left-bottom as origin ,y1 should be used.
#   pdf_y0 = marker["rect"][1]

#   page_height = page.rect.height

    img_x = int(round(x0 * zoom))
#   img_y = int((page_height - pdf_y1) * zoom)   when use the left-bottom as origin ,y1 should be used.
    img_y = int(round(y0 * zoom))

    return img_x, img_y

def find_local_blank(binary, start_x, start_y, roi_width=60, roi_height=180):
    h, w = binary.shape
    
    x_end = min(start_x + roi_width, w)
    y_end = min(start_y + roi_height, h)

    roi = binary[start_y:y_end, start_x:x_end]

    x, y, rw, rh = largest_rectangle(roi)

    return start_x+x, start_y+y, rw, rh









