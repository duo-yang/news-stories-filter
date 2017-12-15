import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup as Soup

# ----------
# UTILITIES FOR CACHING
# ----------

# Constraints

CACHE_FNAME = 'cache/cache_file.json'
TOP_URL = 'http://www.nytimes.com/pages/todayspaper/index.html'
HTML_CACHE_FILE = 'cache/html_cache.html'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEFAULT_EXPIRATION_IN_DAYS = 3
DEFAULT_BASE_URL = ""
DEFAULT_API_KEYS = []

DEBUG = True


# Load cache file

try:
    with open(CACHE_FNAME, 'r', encoding='utf-8') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except FileNotFoundError:
    CACHE_DICTION = {}


# Cache functions for html

def has_cache_expired(timestamp_str,
                      expire_in_days=DEFAULT_EXPIRATION_IN_DAYS):
    """Check if cache timestamp is over expire_in_days old

    :param timestamp_str:  [str] timestamp when the cache is done
    :param expire_in_days: [int] time of expiration in days
                                    (default DEFAULT_EXPIRATION_IN_DAYS)

    :return: [bool] if the cache has expired
    """

    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_days = delta.days

    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_days > expire_in_days:
        return True
    else:
        return False


def get_text_from_cache(url):
    """If URL exists in cache and has not expired,
    return the html (str), else return None

    :param url: [str] url key to fetch from cache

    :return: [str]  html text (if url exists)
    :return: [None] if url not exists
    """

    if url in CACHE_DICTION:
        url_dict = CACHE_DICTION[url]

        if has_cache_expired(url_dict['timestamp'],
                             url_dict['expire_in_days']):
            # also remove old copy from cache
            del CACHE_DICTION[url]
            html = None
        else:
            html = CACHE_DICTION[url]['html']
    else:
        html = None

    return html


def get_soup_from_cache(url):
    """If URL exists in cache and has not expired,
    return the html (BeautifulSoup object), else return None

    :param url: [str] url key to fetch from cache

    :return: [BeautifulSoup] BeautifulSoup object for html (if url exists)
    :return: [None]          if url not exists
    """

    html_txt = get_text_from_cache(url)
    if html_txt:
        return Soup(html_txt, 'html.parser')
    else:
        return None


def set_in_cache(url,
                 html,
                 expire_in_days):
    """Add URL and html to the cache dictionary,
    and save the whole dictionary to a file as json

    :param url:            [str] url key to set in cache
    :param html:           [str] html text to set in cache
    :param expire_in_days: [int] time of expiration in days to set

    :return: [None]
    """

    CACHE_DICTION[url] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w', encoding='utf-8') as cache_json_file:
        cache_json_txt = json.dumps(CACHE_DICTION)
        cache_json_file.write(cache_json_txt)


def get_html_from_url(url,
                      expire_in_days=DEFAULT_EXPIRATION_IN_DAYS):
    """Check in cache, if not found, load html,
    save in cache and then return that html

    :param url:            [str] url key to fetch from cache
    :param expire_in_days: [int] time of expiration in days
                                 (default DEFAULT_EXPIRATION_IN_DAYS)

    :return: [str] html text
    """

    # check in cache
    html = get_text_from_cache(url)
    if html:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
            print()
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(url))
            print()

        # fetch fresh
        response = requests.get(url)

        # Encode using UTF-8
        response.encoding = 'utf-8'

        html = response.text

        # cache it
        set_in_cache(url, html, expire_in_days)

        if url == TOP_URL:
            # Write html file
            with open(HTML_CACHE_FILE, 'w', encoding='utf-8') as html_write:
                html_write.write(html)

    return html


def get_soup_from_url(url,
                      expire_in_days=DEFAULT_EXPIRATION_IN_DAYS):
    """Check in cache, if not found, load html,
    save in cache and then return that html (BeautifulSoup object)

    :param url:            [str] url key to fetch from cache
    :param expire_in_days: [int] time of expiration in days
                                 (default DEFAULT_EXPIRATION_IN_DAYS)

    :return: [BeautifulSoup] BeautifulSoup object for html
    """

    html = get_html_from_url(url)

    return Soup(html, 'html.parser')


# Cache functions for API

def params_unique_combination(base_url,
                              params_d,
                              private_keys=DEFAULT_API_KEYS):
    """Get the unique identifier for the API call

    :param base_url:     [str]  base url key
    :param params_d:     [dict] parameters/terms dictionary for the API call
    :param private_keys: [list] API private keys
                                (default DEFAULT_API_KEYS)

    :return: [str] unique identifier text
    """
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return base_url + "_".join(res)


def get_json_from_api(params_diction,
                      base_url=DEFAULT_BASE_URL):
    """Get the unique identifier for the API call

    :param base_url: [str]  base url for API call
    :param params_d: [dict] parameters/terms dictionary for the API call

    :return: [str] cached json text
    """
    unique_id = params_unique_combination(base_url, params_diction)
    if unique_id in CACHE_DICTION:
        if DEBUG:
            print('Loading from cache: {0}'.format(base_url))
            print('with terms: {0}'.format(params_diction))
            print()
        return CACHE_DICTION[unique_id]
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(base_url))
            print('with terms: {0}'.format(params_diction))
            print()
        res = requests.get(base_url, params_diction)
        res.encoding = 'utf-8'
        CACHE_DICTION[unique_id] = json.loads(res.text)
        with open(CACHE_FNAME, 'w', encoding='utf-8') as cache_json_file:
            cache_json_txt = json.dumps(CACHE_DICTION)
            cache_json_file.write(cache_json_txt)
        return CACHE_DICTION[unique_id]


def set_pickle_in_cache(url,
                        pickle_text,
                        expire_in_days=DEFAULT_EXPIRATION_IN_DAYS):

    CACHE_DICTION['PICKCLE-' + url] = {
        'story_text': pickle_text,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w', encoding='utf-8') as cache_json_file:
        cache_json_txt = json.dumps(CACHE_DICTION)
        cache_json_file.write(cache_json_txt)


def get_pickle_from_cache(url):

    if 'PICKCLE-' + url in CACHE_DICTION:
        url_dict = CACHE_DICTION[url]

        if has_cache_expired(url_dict['timestamp'],
                             url_dict['expire_in_days']):
            # also remove old copy from cache
            del CACHE_DICTION['PICKCLE-' + url]
            story_text = None
        else:
            story_text = CACHE_DICTION['PICKCLE-' + url]['story_text']
    else:
        story_text = None

    return story_text
