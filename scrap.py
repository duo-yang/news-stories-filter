from caching import get_soup_from_url


DEBUG = False


todays_soup = None

front_page_soup = None
other_sections_soup = None


def scrap_setup():
    global todays_soup
    global front_page_soup
    global other_sections_soup
    todays_soup = get_soup_from_url(
        'http://www.nytimes.com/pages/todayspaper/index.html')

    front_page_soup = todays_soup.find('div', {'class': 'aColumn'})
    other_sections_soup = todays_soup.find('div', {'id': 'SpanABMiddleRegion'})


# Extract news story data
def extract_data_from_story_item(story_soup):
    title = story_soup.find('h3').text.strip()
    byline = story_soup.find('h6').text.strip()

    summary_p = story_soup.find('p', {'class': 'summary'})
    if summary_p:
        summary = summary_p.text.strip()
    else:
        summary = None

    thumbnail = None
    img_tag = story_soup.find('img')
    if img_tag:
        thumbnail = img_tag.get('src')

    # and some other ways of doing this
    # thumbnail = img_tag.get('src') if img_tag else None
    # thumbnail = img_tag and img_tag.get('src') or None

    url = story_soup.find('h3').find('a').get('href')

    story_dict = {
        'title': title,
        'byline': byline,
        'summary': summary,
        'thumbnail': thumbnail,
        'url': url
    }

    return story_dict


def extract_data_from_related_article(article_soup):
    title = article_soup.find('h2').text.strip()

    img_tag = article_soup.find('img')
    thumbnail = img_tag.get('src') if img_tag else None

    url = article_soup.find('a').get('href')

    return {
        'title': title,
        'thumbnail': thumbnail,
        'url': url
    }


# Extract related articles, access new page in the process
def extract_related_articles(url):
    related_coverage_list = []

    story_soup = get_soup_from_url(url, 'html.parser')
    related_soup = story_soup.find('aside', {'class': 'related-combined-coverage-marginalia'})

    if related_soup:
        for article_soup in related_soup.find_all('li'):
            article_dict = extract_data_from_related_article(article_soup)
            related_coverage_list.append(article_dict)

    return related_coverage_list


# Load news data
def load_articles_from_section(section_soup):
    story_list = []
    stories = section_soup.find_all('div', {'class': 'story'})
    for story_soup in stories:
        story_dict = extract_data_from_story_item(story_soup)
        story_dict['related_articles'] = extract_related_articles(story_dict['url'])
        story_list.append(story_dict)

        if DEBUG:
            print(story_dict['title'])
            print(story_dict['byline'])
            print(story_dict['summary'])
            print("Has Thumbnail: ", story_dict['thumbnail'] and True or False)
            print("Has URL:", story_dict['url'] and True or False)
            print("# of related articles:",
                  len(story_dict['related_articles']))
            print()
            print('-'*10)
            print()

    return story_list


def load_articles_from_headlines_only(section_soup):
    story_list = []
    stories = section_soup.find_all('li')
    for story_soup in stories:
        story_dict = {
            'title': story_soup.find('a').text.strip(),
            'url': story_soup.find('a').get('href')
        }

        byline_tag = story_soup.find('div', {'class': 'byline'})
        story_dict['byline'] = byline_tag.text.strip() if byline_tag else None

        story_dict['related_articles'] = extract_related_articles(story_dict['url'])
        story_list.append(story_dict)

        if DEBUG:
            print('Title:', story_dict['title'])
            if story_dict.get('byline'):
                print('Byline:', story_dict['byline'])
            print("Has URL:", story_dict['url'] and True or False)
            print("# of related articles:", len(story_dict['related_articles']))
            print()
            print('-'*10)
            print()

    return story_list


def load_page():
    scrap_setup()

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
            print('=' * len(section_title))
            print(section_title.upper())
            print('=' * len(section_title))
            print()

        other_stories.extend(load_articles_from_headlines_only(section_soup))

    return top_stories, other_stories
