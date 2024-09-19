
## Installation

This crawler is designed with python 3.11 and uses scrapy 2.11

To install the project, you need to first install python 3.11 and create virtualenv and then install all the requirements from requirements.txt file

```bash
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
```

## Running the crawler

To run the cralwer run the following command, this will crawl all the items

```bash
scrapy crawl steamcommunity
```

## Exporting the data to CSV

Scrapy by default support CSV export, we don't have to customize or code for it. To crawl the data and export into CSV use following command
```bash
scrapy crawl steamcommunity -t csv -0 steamcommunity.csv
```
this will export the data to steamcomminity.csv file


## Test Requirements

1. [x]  Handle dynamic content using a headless browser (e.g., Playwright or Selenium).
1. [x]  Manage pagination (scrape multiple pages).
1. [x]  Implement error handling for network issues and retries on failures.
   1.  scrapy provides default error handling, there is a custom retry in the parse_game method.
1. [x]  Ensure the script is efficient and can handle many requests without getting blocked.
   1. I've configured `CONCURRENT_REQUESTS = 2` and `DOWNLOAD_DELAY = 1` in settings.py to achive this.
1. [x]  Dockerize your solution.
   1. Docker file is added.
1. [x] Use asyncio to scrape pages concurrently.
   1.  scrapy bydefault uses twisted to achieve the asyncio operations for working with multiple requests.
1. [x]  Save the data in a more structured format like JSON, or store it in a database (e.g., SQLite or MongoDB).
   1.  To store the data in JSON format, you can run the crawler with following command `scrapy crawl steamcommunity -t json -o steamcommunity.json`
1. [x]  Write a few unit tests for the functions used in the script.
    1. In scrapy, we usually don't write unit tests for the functioins which deals with html pages, instead we use spidermon which is spider monitoring tool and do data validation via jsonschema. This is configured in `IterviewTest/monitors` and schema can be found in `InterviewTest/schema/steamcomminity.json`
    