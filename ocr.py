import re
import sys
from io import StringIO
from pathlib import Path
from subprocess import check_call, check_output

from PIL import Image

LETTERPATH = Path.cwd()/"letters"


def get_letter_img(img, x, y):
    return img.crop((6 + x*11, y*22, 6+(x+1)*11, (y+1)*22)).convert("L")


def get_headline_img(img, x):
    return img.crop((6 + x * 11, 22, 6 + (x + 1) * 11, 66)).convert("L")


def gocr(letter, h):
    f = Path("/tmp/{hash}.png")
    letter.save(f)
    l = check_output(f"gocr {f}", shell=True).decode("utf-8").strip()
    f2 = LETTERPATH/f"letter_{h}__{l}.png"
    f.rename(f2)
    return l


KNOWN = None
def initialize_known():
    global KNOWN
    if KNOWN is not None:
        return
    KNOWN = {}
    for f in LETTERPATH.glob("*.png"):
        m = re.match(r"letter_(-?\d+)__(.)\.png", f.name)
        h, letter = m.groups()
        KNOWN[int(h)] = letter


def ocr(letter):
    initialize_known()
    h = hash(tuple(letter.getdata()))
    if h in KNOWN:
        l = KNOWN[h]
        if l == "_":
            print(h)
    else:
        l = gocr(letter, h)
        KNOWN[h] = l
        print(f"{l}  letters/letter_{h}__{l}.png")
    return l

def get_body(img):
    out = StringIO()
    width, height = img.size
    nrows = height // 22
    text = []
    for y in range(4, nrows):
        for x in range(0, 39):
            i = get_letter_img(img, x, y)
            l = ocr(i)
            out.write(l)
            if l in [".", ",", ":"]:
                out.write(" ")
        out.write("\n")
    txt =  out.getvalue()
    txt = "\n\n".join(re.sub(r"\s+", " ", x).strip()
                      for x in re.split(r"\n\s*\n", txt))
    return txt.strip()

def get_headline(img):
    out = StringIO()

    for x in range(0, 39):
        i = get_headline_img(img, x)
        l = ocr(i)
        out.write(l)
        if l in [".", ",", ":"]:
            out.write(" ")
    return out.getvalue().strip()


def get_text(img):
    headline = get_headline(img)
    body = get_body(img)
    return f"{headline}\n\n{body}"


img = Image.open(sys.argv[1])
print(get_text(img))
