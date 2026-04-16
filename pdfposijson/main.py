# main.py

from pathlib import Path
import glob
from core.jsonfix import create_template, load_template, save_template
from core.getpdfcordi import pdf_to_img, binaryimg, pdf_to_img_cordinate, find_local_blank
import fitz
import re


PDF_DIRECTORY = "./pdf/"

##################################################
# preprocessor
##################################################
def preprocess(pdf_path, pdf_name = None):
    
    for f in Path(pdf_path).glob("*.pdf"):
        print(f"processing file: {f}")

        if not create_template(f, f"./config/{f.stem}.json"):
            print(f"Failed to create template for {f}")
            continue
        
def main():

    for f in Path(PDF_DIRECTORY).glob("*.pdf"):
        print(f"processing file: {f}")

        doc = fitz.open(f)

        page = doc[0]

        img = pdf_to_img(page)

        imgbin = binaryimg(img)

        fjson = f.name.replace(".pdf", "")

        cfg = load_template(fjson)

        for fields in cfg.get("fields", []):
 
            # key = fields.get("key")
            
            x0, y0, x1, y1 = fields["placeholderbbox"]

            x0 = float(x0)
            y0 = float(y0)

#           pattern = r'\[(?P<x0>\d+\.\d+),\s*(?P<y0>\d+\.\d+),\s*(?P<x1>\d+\.\d+),\s*(?P<y1>\d+\.\d+)\]'            
#           match = re.search(pattern, fields.get("placeholderbbox"))            
#           x0 = float(match.group('x0'))
#           y0 = float(match.group('y0'))

            imgx, imgy = pdf_to_img_cordinate(page, x0, y0, zoom=2)

            x, y, w, h = find_local_blank(imgbin, imgx, imgy)

            fields["blankbbox"] = [x*0.35277, y*0.35277, (x + w)*0.35277, (y + h)*0.35277]
        
        save_template(fjson, cfg)

if __name__ == "__main__":
    #preprocess(PDF_DIRECTORY)
    main()