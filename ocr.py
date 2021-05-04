import logging
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
    if l == "/":
        l = '⁄'  # linux does not like slashes in file names
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
        if not m:
            print(f.name)
            raise
        h, letter = m.groups()
        img = Image.open(f)
        KNOWN[int(h)] = (letter, img)


def compare_images(img1, img2):
    if img1.size[1] != img2.size[1]:
        return None
    return sum((x1-x2)**2 for (x1, x2) in zip(list(img1.getdata()),list(img2.getdata())))


def closest(letter: Image, accept_zero=True):
    winner, winning_score, winning_hash = None, None, None
    for hash_, (l, img) in KNOWN.items():
        score = compare_images(letter, img)
        if score is None:
            continue
        if (not accept_zero) and (score == 0):
            continue
        if winning_score is None or score < winning_score:
            winner = l
            winning_score = score
            winning_hash = hash_
    return winner, winning_score, winning_hash


def guess(letter: Image, accept_zero=True):
    winner, winning_score, winning_hash = closest(letter, accept_zero=accept_zero)
    if winning_score < 90000:
        return winner
    if letter.size[1] == 44:
        # Try resizing
        img = letter.resize((11, 22))
        winner2, winning_score2, _ = closest(img, accept_zero=accept_zero)
        if winning_score2 < 350000:
            return winner2
    hash_ = hash(tuple(letter.getdata()))
    logging.warning(f"Bad match: letters/letter_{hash_}__{winner}.png (score: {winning_score}, best match letters/letter_{winning_hash}__{winner}.png, size {letter.size})")
    return winner

# letters/letter_-3616073949698735120__-.png
# letters/letter_7901707541910618925__-.png

def ocr(letter: Image):
    initialize_known()
    h = hash(tuple(letter.getdata()))
    if h in KNOWN:
        l, img = KNOWN[h]
        #logging.info(f"KNOWN: {l}  letters/letter_{h}__{l}.png")
    else:
        l = guess(letter)
        fn = LETTERPATH/f"letter_{h}__{l}.png"
        letter.save(fn)
        KNOWN[h] = (l, letter)
        logging.info(f"GUESS: {l}  letters/letter_{h}__{l}.png")
    return l


def get_body(img):
    out = StringIO()
    width, height = img.size
    nrows = height // 22
    text = []
    for y in range(4, nrows):
        prev = None
        for x in range(0, 39):
            i = get_letter_img(img, x, y)
            l = ocr(i)
            if prev in (".", ",", ":") and l.isalpha():
                out.write(" ")
            out.write(l)
            prev=l
        out.write("\n")
    txt =  out.getvalue()
    txt = "\n\n".join(re.sub(r"\s+", " ", x).strip()
                      for x in re.split(r"\n\s*\n", txt))
    return txt.strip()


def get_headline(img):
    out = StringIO()
    prev = None
    for x in range(0, 39):
        i = get_headline_img(img, x)
        l = ocr(i)
        if prev in (".", ",", ":") and l.isalpha():
            out.write(" ")
        out.write(l)
        prev = l
    return out.getvalue().strip()


def get_text(img_fn: str):
    img = Image.open(img_fn)
    headline = get_headline(img)
    body = get_body(img)
    return f"{headline}\n\n{body}"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
    print(get_text(sys.argv[1]))

    sys.exit()
    initialize_known()


    for f in LETTERPATH.glob("*.png"):
        image = Image.open(f)
        if image.size[1] != 44:
            continue

        m = re.match(r"letter_(-?\d+)__(.)\.png", f.name)
        h, letter = m.groups()
        winner = guess(image)
        if letter != winner:# and score > 90000:
            print(letter, winner)