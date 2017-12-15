from pprint import pprint

from nytimes_news import NewsStory
from scrap import *
from db_stories import insert_story, search_stories, setup_database,\
    avoid_stories


if DEBUG:
    print('The Front Page'.upper())

top_stories = load_articles_from_section(front_page_soup)
other_stories = load_articles_from_headlines_only(front_page_soup.find(
    'ul', {'class': 'headlinesOnly'}))

for section_soup in other_sections_soup.find_all(
        'ul', {'class': 'headlinesOnly'}):
    section_title = section_soup.parent.find(
        'h3', {'class': 'sectionHeader'}).text.strip()
    if DEBUG:
        print()
        print('='*len(section_title))
        print(section_title.upper())
        print('='*len(section_title))
        print()

    other_stories.extend(load_articles_from_headlines_only(section_soup))

# setup_database()

top_news_stories = []
for story in top_stories:
    new_story = NewsStory(story)
    new_story.tagging()
    if DEBUG:
        print(new_story)
        print()
    top_news_stories.append(new_story)

    insert_story(new_story)

other_news_stories = []
for story in other_stories:
    new_story = NewsStory(story)
    new_story.tagging()
    if DEBUG:
        print(new_story)
        print()
    other_news_stories.append(new_story)

pprint(search_stories('Trump'))
pprint(avoid_stories('Trump'))
