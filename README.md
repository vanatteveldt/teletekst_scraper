# teletekst_scraper
Scraper for Dutch teletekst using custom OCR on their twitter stream 

# Install

Clone from github and install requirements, e.g.:

```
git clone git@github.com:vanatteveldt/teletekst_scraper
cd teletekst_scraper
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

# Usage

Download a teletekst image from https://twitter.com/Teletekst and OCR it:

```
python ocr.py test_image.png
```

If any unknown letters are encountered, it will print a message like this:

```
X  letters/letter_-5443486846543098756__X.png
```

This means the letter with the given hash was recognized as a capital `X`. 
Since the `gocr` performs quite poorly on the teletekst font, it is probably a good idea to check and correct the identification.
You can do that by renaming the file in the letters folder.
