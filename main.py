import logging
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image
from amcatclient import AmcatAPI

from ocr import get_text, get_headline, get_body
from twitter import get_tweets

TMP = Path("/tmp")

def parse(tweet: dict):
    img_fn = TMP/f"{tweet['id']}.png"
    if not img_fn.exists():
        urlretrieve(tweet['image'], img_fn)
    img = Image.open(img_fn)
    title = get_headline(img)
    body = get_body(img)
    return dict(title=title,
                text=body,
                publisher="teletekst",
                date=tweet['created_at'],
                url=f"https://twitter.com/Teletekst/status/{tweet['id']}")

# Todo: argparse (sorry...)
project = 69
aset = 3521
host = "https://vu.amcat.nl"


amcat = AmcatAPI(host=host)
token = open("BEARER_TOKEN").read().strip()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
for i, batch in enumerate(get_tweets(query="from:teletekst", token=token, batch_size=100, start_time='2021-01-01T00:00:00Z')):
    articles = [parse(tweet) for tweet in batch]
    print(f"{i} {articles[0]['date']}")

    amcat.create_articles(project=project, articleset=aset, json_data=articles)
