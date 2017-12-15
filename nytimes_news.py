import string
import scrap

from scrap import load_page
from db_utils import insert_story, setup_database


class NewsStory(object):
    def __init__(self, story_dict, tags=None):
        self.title = story_dict['title']
        self.byline = story_dict['byline']
        if 'summary' in story_dict:
            if story_dict['summary']:
                self.top_story = True
                self.summary = story_dict['summary']
                self.thumbnail = story_dict['thumbnail']
            else:
                self.top_story = False
                self.summary = None
                self.thumbnail = None
        else:
            self.top_story = False
            self.summary = None
            self.thumbnail = None
        self.url = story_dict['url']
        if 'num_related' in story_dict:
            self.num_related = story_dict['num_related']
        else:
            self.num_related = len(story_dict['related_articles'])
        if tags:
            self.tags = tags
            self.tagged = True
        else:
            self.tags = []
            self.tagged = False

    def __repr__(self):
        return "title: {0}\nbyline: {1}\nsummary: {2}\ntop story: {3}\n" \
               "thumbnail: {4}\nurl: {5}\nrelated stories: {6}\n" \
               "tagged: {7}\ntags: {8}".format(
                    self.title, self.byline, self.summary, self.top_story,
                    self.thumbnail, self.url, self.num_related,
                    self.tagged, self.tags)

    def __str__(self):
        return "Title: {0}\nByline: {1}\nSummary: {2}\nTop story: {3}\n" \
               "Thumbnail: {4}\nUrl: {5}\n# of related stories: {6}\n" \
               "Tagged: {7}\nTags: {8}".format(
                    self.title, self.byline, self.summary, self.top_story,
                    self.thumbnail, self.url, self.num_related,
                    self.tagged, self.tags)

    def __contains__(self, item):
        return item.lower() in self.tags

    def tagging(self):
        if not self.tagged:
            self.tags = self.title.translate(
                str.maketrans("", "", string.punctuation)).lower().split()
            if self.top_story:
                self.tags.extend(self.summary.translate(
                    str.maketrans("", "", string.punctuation)).lower().split())
            self.tagged = True
            "".split()


def set_up():
    top_stories, other_stories = load_page()

    setup_database()

    top_news_stories = []
    for story in top_stories:
        new_story = NewsStory(story)
        new_story.tagging()
        if scrap.DEBUG:
            print(new_story)
            print()
        top_news_stories.append(new_story)

        insert_story(new_story)

    other_news_stories = []
    for story in other_stories:
        new_story = NewsStory(story)
        new_story.tagging()
        if scrap.DEBUG:
            print(new_story)
            print()
        other_news_stories.append(new_story)

        insert_story(new_story)
