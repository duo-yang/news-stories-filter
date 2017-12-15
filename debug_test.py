from pprint import pprint

import scrap
from nytimes_news import NewsStory, set_up
from scrap import load_page
from db_utils import insert_story, search_stories, setup_database, \
    avoid_stories


# top_stories, other_stories = load_page()
#
# setup_database()
#
# top_news_stories = []
# for story in top_stories:
#     new_story = NewsStory(story)
#     new_story.tagging()
#     if scrap.DEBUG:
#         print(new_story)
#         print()
#     top_news_stories.append(new_story)
#
#     insert_story(new_story)
#
# other_news_stories = []
# for story in other_stories:
#     new_story = NewsStory(story)
#     new_story.tagging()
#     if scrap.DEBUG:
#         print(new_story)
#         print()
#     other_news_stories.append(new_story)
#
#     insert_story(new_story)

set_up()

top_stories = []
other_stories = []
for story in avoid_stories('Trump'):
    new_story = NewsStory(story)
    if new_story.top_story:
        top_stories.append(new_story)
    else:
        other_stories.append(new_story)

pprint(top_stories)
pprint(other_stories)

# pprint(search_stories('Trump'))
# pprint(avoid_stories('Trump'))
