import re
import fitz  # PyMuPDF
import numpy as np
import cv2
from pathlib import Path
import glob

PDF_DIRECTORY = "./pdf/"

def pdf_to_img(page, zoom=2):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    return img

##################################################
# binary img
##################################################
def binaryimg(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    binary = cv2.medianBlur(binary, 1)

    kernel = np.ones((5,5), np.uint8)

    binary = cv2.erode(binary, kernel)

    #binary = np.where(binary == 255, 1, 0).astype(np.uint8)

    return binary

def main():


    doc = fitz.open(f"{PDF_DIRECTORY}6.1 TR.pdf")

    page = doc[0]

    img = pdf_to_img(page)

    cv2.imshow("pdftoimg", img)

    #key = cv2.waitKey(0)
    cv2.imwrite("pdftoimg.png", img)

    imgbin = binaryimg(img)

    cv2.imshow("binaryimg", imgbin)

    #key = cv2.waitKey(0)
    cv2.imwrite("binaryimg.png", imgbin)

def largest_rectangle(binary):
    h, w = binary.shape
    height = [0] * w

    actualhei = 0
    actualwid = 0

    best_rect = (0, 0, 0, 0)

    for i in range(h):
        for j in range(w):
            if binary[i][j] == 1:
                height[j] += 1
            else:
                height[j] = 0
                

if __name__ == "__main__":
    main()