import unittest

import datetime
from bs4 import BeautifulSoup as Soup

from SI507F17_finalproject import *
import caching
import scrap
import nytimes_news
import db_utils


class CacheTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_has_cache_expired(self):
        self.assertTrue(caching.has_cache_expired(
            str(datetime.datetime(1999, 1, 1, 1, 1, 1, 100)), 1))

    def test_get_text_from_cache(self):
        self.assertIsInstance(caching.get_text_from_cache(
                'http://www.nytimes.com/pages/todayspaper/index.html'), str)
        self.assertIsNone(caching.get_text_from_cache('a'))

    def test_get_html_from_cache(self):
        self.assertIsInstance(caching.get_html_from_url(
                'http://www.nytimes.com/pages/todayspaper/index.html'), str)

    def test_get_soup_from_cache(self):
        self.assertIsInstance(caching.get_soup_from_url(
                'http://www.nytimes.com/pages/todayspaper/index.html'), Soup)

    def tearDown(self):
        pass


class ScrapTest(unittest.TestCase):
    def setUp(self):
        self.top_stories, self.other_stories = scrap.load_page()
        self.top_news_stories = []
        self.other_news_stories = []
        self.test_story_dict = {
            'title': "Walmart Will Let Its 1.4 Million Workers Take Their Pay "
                     "Before Payday",
            'byline': None,
            'summary': None,
            'top_story': False,
            'thumbnail': None,
            'url': "https://www.nytimes.com/2017/12/13/business/walmart-"
                   "workers-pay-advances.html?ref=todayspaper",
            'num_related': 3,
            'tagged': False,
            'tags': []
        }
        self.test_story = NewsStory(self.test_story_dict)
        for story in self.top_stories:
            new_story = NewsStory(story)
            self.top_news_stories.append(new_story)
        for story in self.other_stories:
            new_story = NewsStory(story)
            self.other_news_stories.append(new_story)

    def test_top_stories(self):
        for story in self.top_stories:
            self.assertIsInstance(story['title'], str)
            self.assertIsInstance(story['byline'], str)
            self.assertIsInstance(story['summary'], str)
            self.assertIsInstance(story['thumbnail'], str)
            self.assertIsInstance(story['url'], str)

    def test_headlines_only(self):
        for story in self.other_stories:
            self.assertIsInstance(story['title'], str)
            self.assertIsInstance(story['url'], str)
            self.assertTrue(
                story['byline'] is None or isinstance(story['byline'], str))

    def test_related_articles(self):
        for story in self.top_stories:
            self.assertIsInstance(story['related_articles'], list)
        for story in self.other_stories:
            self.assertIsInstance(story['related_articles'], list)

    def test_top_news_story_init(self):
        for story in self.top_news_stories:
            self.assertIsInstance(story.title, str)
            self.assertIsInstance(story.byline, str)
            self.assertIsInstance(story.summary, str)
            self.assertIsInstance(story.thumbnail, str)
            self.assertIsInstance(story.url, str)
            self.assertTrue(story.top_story)
            self.assertFalse(story.tagged)
            self.assertIsInstance(story.tags, list)
            self.assertTrue(len(story.tags) == 0)

    def test_other_news_story_init(self):
        for story in self.other_news_stories:
            self.assertIsInstance(story.title, str)
            self.assertTrue(
                story.byline is None or isinstance(story.byline, str))
            self.assertIsNone(story.summary)
            self.assertIsNone(story.thumbnail)
            self.assertIsInstance(story.url, str)
            self.assertFalse(story.top_story)
            self.assertFalse(story.tagged)
            self.assertIsInstance(story.tags, list)
            self.assertTrue(len(story.tags) == 0)

    def test_tagging(self):
        for story in self.top_news_stories:
            story.tagging()
            self.assertTrue(story.tagged)
            self.assertGreater(len(story.tags), 0)

    def test_tags(self):
        self.test_story.tagging()
        self.assertIn('walmart', self.test_story.tags)
        self.assertNotIn('Walmart', self.test_story.tags)

    def test_contains(self):
        self.test_story.tagging()
        self.assertTrue('walmart' in self.test_story)
        self.assertTrue('Walmart' in self.test_story)

    def test_repr(self):
        pre = self.test_story
        for story in self.top_news_stories:
            self.assertNotEqual(pre.__repr__(), story.__repr__())
            pre = story

    def tearDown(self):
        self.top_stories = None
        self.other_stories = None
        self.top_news_stories = None
        self.other_news_stories = None
        self.test_story = None
        self.test_story_dict = None


class DBTest(unittest.TestCase):
    def setUp(self):
        nytimes_news.set_up()
        self.test_story_dict = {
            'title': "abcdefghijklmnopqrstuvwxyz",
            'byline': None,
            'summary': None,
            'top_story': False,
            'thumbnail': None,
            'url': "https:test",
            'num_related': 3,
            'tagged': False,
            'tags': []
        }
        self.test_story = NewsStory(self.test_story_dict)
        self.test_story.tagging()

    def test_search_stories(self):
        db_utils.insert_story(self.test_story, False)
        self.assertEqual(
            len(db_utils.search_stories(
                "abcdefghijklmnopqrstuvwxyz", False)), 1)

    def test_avoid_stories(self):
        db_utils.insert_story(self.test_story, False)
        stories = db_utils.avoid_stories("abcdefghijklmnopqrstuvwxyz", False)
        for story in stories:
            self.assertNotEqual(story['title'], "abcdefghijklmnopqrstuvwxyz")

    def tearDown(self):
        pass