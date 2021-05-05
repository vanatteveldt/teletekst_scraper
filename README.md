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

Call [main.py](main.py) to use the Academic Twitter API to retrieve all teletekst from a certain data, OCR it, and upload to AmCAT.
All parameters are hard-coded (sorry!), so edit main.py to change them:

```
echo "YOUR_TWITTER_TOKEN" > BEARER_TOKEN
python main.py
```

This will use a custom [OCR](ocr.py) to segment the image and try to recognize all letters.
If an exact match is not found, it will pick the closest match in terms of pixel distance. 

All new characters are saved to the [letters](letters) folder.
It's probably good to quickly check if they all make sense, you can just rename the last part of the file to change the result. 
If you did check, feel free to PR the new letters.

If the match distance is larger than the threshold, it gives a warning message:

```
Bad match: letters/letter_{hash_}__{winner}.png (score: {winning_score}, best match letters/letter_{winning_hash}__{winner}.png, size {letter.size})")
```
It's probably a good idea to check these in any case, often it's an accented letter or non-alphanumeric character. 

After making corrections you can re-run 
(but of course the 'wrong' items might already be in AmCAT by that time, so could be good to do a dry run first)

## Twitter scraper only

To only retrieve all messages and image urls, call `get_tweets` from [twitter.py](twitter.py)

## OCR only

You can use `ocr.py` to convert teletekst images to text:

```
python ocr.py test_image.png
```
