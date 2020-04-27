# change.org petition scraper

[Scrapy](https://scrapy.org/) based scraper for change.org that scrapes results for a search term.

## Installation

Python 3 and scrapy are the only dependencies, once you have Python installed you can install scrapy using.

`pip install scrapy==2.0.1`

## Running

In the directory where you've cloned this repository.

`scrapy crawl petitions -a search="search term" -o petitions.json`

This will create a JSON file with data about all of the results matching the "search term" search. If you want the result in csv replace `petitions.json` with `petitions.csv`.
