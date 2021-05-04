import logging
import time

import requests


def get_tweets(query, token, batch_size=100, **options):
    """
    Yield all tweets matching query
    :param query: query (string)
    :param token: bearer token for academic api
    :param batch_size: number of tweets per batch (max=100)
    :return:
    """
    data = {'query': query,
            'expansions': "attachments.media_keys",
            'media.fields': "url",
            'tweet.fields': 'created_at',
            'max_results': batch_size,
            **options}
    url = "https://api.twitter.com/2/tweets/search/all"
    headers = {"Authorization": f"Bearer {token}"}
    while True:
        r = requests.get(url, params=data, headers=headers)
        r.raise_for_status()
        d = r.json()
        yield parse_result(d)
        if not 'next_token' in d['meta']:
            return
        data['next_token'] = d['meta']['next_token']
        time.sleep(1) # rate limit: 1 request per second


def parse_result(d: dict):
    urls = {x['media_key']: x['url'] for x in d['includes']['media']}
    for tweet in d['data']:
        media = tweet['attachments']['media_keys']
        if len(media) != 1:
            raise Exception("Trouble parsing tweet")
        url = urls[media[0]]
        yield {'created_at': tweet['created_at'],
               'id': tweet['id'],
               'text': tweet['text'],
               'image': url}




