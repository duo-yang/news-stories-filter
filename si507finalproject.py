from flask import Flask, render_template, request

from nytimes_news import NewsStory, set_up

import logging
import db_utils

app = Flask(__name__)

set_up()


@app.route('/')
@app.route('/avoid')
def home_avoid():
    return render_template('index.html')


@app.route('/avoid-word/<keyword>')
def home_avoid_word(keyword):
    list_stories = db_utils.avoid_stories(keyword)

    top_stories = []
    other_stories = []
    for story in list_stories:
        new_story = NewsStory(story)
        if new_story.top_story:
            top_stories.append(new_story)
        else:
            other_stories.append(new_story)

    return render_template('news.html', keyword=keyword, joinword='without',
                           top_stories=top_stories,
                           other_stories=other_stories)


@app.route('/search')
def home_find():
    return render_template('search.html')


@app.route('/search-word/<keyword>')
def home_search_word(keyword):
    list_stories = db_utils.search_stories(keyword)

    top_stories = []
    other_stories = []
    for story in list_stories:
        new_story = NewsStory(story)
        if new_story.top_story:
            top_stories.append(new_story)
        else:
            other_stories.append(new_story)

    return render_template('news.html', keyword=keyword, joinword='without',
                           top_stories=top_stories,
                           other_stories=other_stories)


@app.route('/avoid-news', methods=['GET', 'POST'])
def avoid():
    if request.method == "POST":
        keyword = request.form['keyword']
    else:
        keyword = 'Trump'
    list_stories = db_utils.avoid_stories(keyword)

    top_stories = []
    other_stories = []
    for story in list_stories:
        new_story = NewsStory(story)
        if new_story.top_story:
            top_stories.append(new_story)
        else:
            other_stories.append(new_story)

    return render_template('news.html', keyword=keyword, joinword='without',
                           top_stories=top_stories,
                           other_stories=other_stories)


@app.route('/search-news', methods=['GET', 'POST'])
def find():
    if request.method == "POST":
        keyword = request.form['keyword']
    else:
        keyword = 'Trump'
    list_stories = db_utils.search_stories(keyword)

    top_stories = []
    other_stories = []
    for story in list_stories:
        new_story = NewsStory(story)
        if new_story.top_story:
            top_stories.append(new_story)
        else:
            other_stories.append(new_story)

    return render_template('news.html', keyword=keyword, joinword='with',
                           top_stories=top_stories,
                           other_stories=other_stories)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html')


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run()
