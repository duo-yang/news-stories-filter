# Import statements

import psycopg2
import psycopg2.extras
from psycopg2 import sql
from db_config import *
import sys

DEBUG = False

# Write code / functions to set up database connection and cursor here.
db_connection = None
db_cursor = None


def get_connection_and_cursor():
    global db_connection, db_cursor
    if not db_connection:
        try:
            db_connection = psycopg2.connect(
                "dbname='{0}' user='{1}' password='{2}'".format(
                    db_name, db_user, db_password))
            print("Success connecting to database")
        except:
            print("Unable to connect to the database. "
                  "Check server and credentials.")
            sys.exit(1)  # Stop running program if there's no db connection.

    if not db_cursor:
        db_cursor = db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor


# Write code / functions to create tables with the columns you want
# and all database setup here.
def setup_database():
    conn, cur = get_connection_and_cursor()

    # Create States table
    if not DEBUG:
        cur.execute("""DROP TABLE IF EXISTS \"Stories\" CASCADE""")

    cur.execute("""CREATE TABLE IF NOT EXISTS \"Stories\" (
            \"ID\" SERIAL PRIMARY KEY,
            \"Title\" TEXT UNIQUE NOT NULL,
            \"Byline\" TEXT NOT NULL,
            \"Summary\" TEXT,
            \"Top_Story\" BOOL,
            \"Thumbnail\" TEXT,
            \"Url\" TEXT,
            \"Num_Related\" INTEGER NOT NULL)
        """)

    cur.execute("""DROP TABLE IF EXISTS \"Tags\"""")
    # Create Sites table
    cur.execute("""CREATE TABLE IF NOT EXISTS \"Tags\" (
        \"ID\" SERIAL PRIMARY KEY,
        \"Tag_Name\" TEXT UNIQUE NOT NULL)
    """)

    cur.execute("""DROP TABLE IF EXISTS \"Stories_Tags\"""")
    # Create Sites table
    cur.execute("""CREATE TABLE IF NOT EXISTS \"Stories_Tags\" (
            \"ID\" SERIAL PRIMARY KEY,
            \"Story_ID\" INTEGER NOT NULL,
            \"Tag_ID\" INTEGER NOT NULL)
        """)

    # Add foreign key constraint
    if not DEBUG:
        cur.execute("""ALTER TABLE \"Stories_Tags\"
            ADD CONSTRAINT \"Stories_FK\"
            FOREIGN KEY (\"Story_ID\")
            REFERENCES \"Stories\" (\"ID\")
            ON DELETE NO ACTION ON UPDATE NO ACTION
        """)
        cur.execute("""ALTER TABLE \"Stories_Tags\"
                ADD CONSTRAINT \"Tags_FK\"
                FOREIGN KEY (\"Tag_ID\")
                REFERENCES \"Tags\" (\"ID\")
                ON DELETE NO ACTION ON UPDATE NO ACTION
        """)

    conn.commit()

    if DEBUG:
        print('Setup database complete')


# Functions to insert data
# into the database here.
def insert_story(story):
    conn, cur = get_connection_and_cursor()

    query = sql.SQL("""INSERT INTO \"Stories\" (\"Title\", \"Byline\",
        \"Summary\", \"Top_Story\", \"Thumbnail\", \"Url\", \"Num_Related\")
        VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6})
        ON CONFLICT DO NOTHING;
        """).format(
            sql.SQL("\'" + story.title + "\'"),
            sql.SQL("\'" + story.byline + "\'"),
            sql.SQL("\'" + story.summary + "\'"),
            sql.SQL("\'" + str(story.top_story) + "\'"),
            sql.SQL("\'" + story.thumbnail + "\'"),
            sql.SQL("\'" + story.url + "\'"),
            sql.SQL(str(story.num_related)))
    query_string = query.as_string(conn)
    cur.execute(query_string)

    query = sql.SQL("""SELECT \"ID\" FROM \"Stories\"
        WHERE \"Title\"={0}""").format(sql.SQL("\'" + story.title + "\'"))
    query_string = query.as_string(conn)
    cur.execute(query_string)
    story_id = cur.fetchall()[0]['ID']

    if story.tagged:
        for tag in story.tags:
            query = sql.SQL("""INSERT INTO \"Tags\" (\"Tag_Name\")
                    VALUES({0})
                    ON CONFLICT DO NOTHING;
                    """).format(sql.SQL("\'" + tag + "\'"))
            query_string = query.as_string(conn)
            cur.execute(query_string)

            query = sql.SQL("""SELECT \"ID\" FROM \"Tags\"
                    WHERE \"Tag_Name\"={0};""").format(
                        sql.SQL("\'" + tag + "\'"))
            query_string = query.as_string(conn)
            cur.execute(query_string)
            tag_id = cur.fetchall()[0]['ID']

            query = sql.SQL("""INSERT INTO \"Stories_Tags\"
                    (\"Story_ID\", \"Tag_ID\")
                    VALUES({0}, {1})
                    ON CONFLICT DO NOTHING;
                    """).format(sql.SQL(str(story_id)),
                        sql.SQL(str(tag_id)))
            query_string = query.as_string(conn)
            cur.execute(query_string)

    conn.commit()


# Search stories
def search_stories(key_word):
    conn, cur = get_connection_and_cursor()

    query = sql.SQL("""SELECT \"Title\", \"Byline\", \"Summary\", \"Top_Story\", 
        \"Thumbnail\", \"Url\", \"Num_Related\" FROM \"Stories\"
        INNER JOIN \"Stories_Tags\"
        ON \"Stories\".\"ID\"=\"Stories_Tags\".\"Story_ID\"
        INNER JOIN \"Tags\"
        ON \"Stories_Tags\".\"Tag_ID\"=\"Tags\".\"ID\"
        WHERE \"Tags\".\"Tag_Name\" = {0};
        """).format(sql.SQL("\'" + key_word + "\'"))
    query_string = query.as_string(conn)
    cur.execute(query_string)

    key_stories = cur.fetchall()

    conn.commit()

    return key_stories


def avoid_stories(key_word):
    conn, cur = get_connection_and_cursor()

    query = sql.SQL("""SELECT \"Title\", \"Byline\", \"Summary\", \"Top_Story\", 
        \"Thumbnail\", \"Url\", \"Num_Related\" FROM \"Stories\"
        INNER JOIN \"Stories_Tags\"
        ON \"Stories\".\"ID\"=\"Stories_Tags\".\"Story_ID\"
        INNER JOIN \"Tags\"
        ON \"Stories_Tags\".\"Tag_ID\"=\"Tags\".\"ID\"
        WHERE \"Tags\".\"Tag_Name\" != {0};
        """).format(sql.SQL("\'" + key_word + "\'"))
    query_string = query.as_string(conn)
    cur.execute(query_string)

    key_stories = cur.fetchall()

    conn.commit()

    return key_stories
