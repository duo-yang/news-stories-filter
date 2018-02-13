# News Stories filter
Course Project for SI 507

This project aims to provide a site enable the reader to 'beep' certain keywords on the [New York Times Today's Newspaper](http://www.nytimes.com/pages/todayspaper/index.html) site LOCALLY on their browser and provide a better interface for reading news.
The end goal would be a scenario where if the viewer is tired of news stories with certain keywords in them, say 'Trump', they can avoid those stories on the frontpage altogether, and get a much more enjoyable frontpage news.

The other function of the tool is search for certain key words and only search those stories, like only viewing stories about 'Trump' for the thillseekers.

The project is built on Flask for web backend. The data are scraped and cached from the New York Times Today's Newspaper site and stored in postgreSQL databases. 

## Features & Process
1.  Avoid Keyword
![Home Page](examples/home_page.png?raw=true "Home Page")
Type in the keyword to avoid and go!
![Avoid Page](examples/avoid.png?raw=true "Avoid Page")
The keyword stories are all gone now.
The same can be achieved with URL `/avoid-word/<keyword>`

2.  Search Keyword
Similar process, just another page. Go 'Try something else'
![Search Page](examples/search.png?raw=true "Avoid Page")
The keyword stories are all here.
The same can be achieved with URL `/search-word/<keyword>`

## Requirements
1.  Database setup requires `db_config.py`, see [db_config_example.py](examples/db_config_example.py) for instructions.
2.  Virtual environment module requirements, see [requirements.txt](requirements.txt)

## Sources
The scraping mechanism is partially referenced from lab session codes.
